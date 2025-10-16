from flask import Blueprint, request, jsonify
from .utils import token_required
from .models import all_ingredients, recipe_store, SUBSTITUTION_MAP, FavoriteRecipe, UserProfile, db, RecipeRating
from sqlalchemy import func
import math

recipes_bp = Blueprint('recipes', __name__)

def calculate_match_score(recipe_ingredients, user_ingredients):
    perfect_matches = 0
    substitution_matches = 0
    made_substitutions = {}
    
    user_ingredients_set = set(user_ingredients)

    for required_ing in recipe_ingredients:
        if required_ing in user_ingredients_set:
            perfect_matches += 1
        else:
            possible_subs = SUBSTITUTION_MAP.get(required_ing, [])
            for sub in possible_subs:
                if sub in user_ingredients_set:
                    substitution_matches += 1
                    made_substitutions[required_ing] = sub
                    break
            
    if len(recipe_ingredients) == 0:
        return 0, {}
        
    score = (perfect_matches + (substitution_matches * 0.7)) / len(recipe_ingredients)
    
    if perfect_matches + substitution_matches == 0:
        return 0, {}

    return score, made_substitutions

@recipes_bp.route("/recognize-ingredients", methods=['POST'])
@token_required
def recognize_ingredients(current_user):
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()

    try:
        CLARIFAI_PAT = "deb567833d0c44789a5b2b0840802b06"

        if not CLARIFAI_PAT or CLARIFAI_PAT == "YOUR_VERIFIED_PERSONAL_ACCESS_TOKEN":
            return jsonify({'message': 'Server configuration error: PAT not set.'}), 500

        from clarifai.client.model import Model
        model = Model("https://clarifai.com/clarifai/main/models/food-item-recognition", pat=CLARIFAI_PAT)
        response = model.predict_by_bytes(image_bytes, input_type="image")
        
        if response.status.code != 10000:
            return jsonify({'message': 'Image recognition failed due to API error.'}), 500

        concepts = response.outputs[0].data.concepts
        recognized_items = [concept.name.lower() for concept in concepts if concept.value > 0.4]
        final_ingredients = [item for item in recognized_items if item in all_ingredients]
        
        if not final_ingredients:
            return jsonify({'message': 'Could not recognize any known ingredients.'}), 404

        return jsonify({"recognized_ingredients": final_ingredients})
    except Exception as e:
        print(f"Clarifai Error: {e}")
        return jsonify({'message': 'Image recognition failed.'}), 500

@recipes_bp.route("/ingredients")
@token_required
def get_ingredients(current_user):
    return jsonify({"ingredients": all_ingredients})

@recipes_bp.route("/generate", methods=["POST"])
@token_required
def generate(current_user):
    # Get filters from query parameters
    dietary_filter = request.args.get('dietary', 'all')
    difficulty_filter = request.args.get('difficulty', 'all')
    max_time_filter = request.args.get('max_time', type=int)

    # 1. Start with all recipes
    filtered_recipes = list(recipe_store.values())

    # 2. Apply filters
    if dietary_filter != 'all':
        filtered_recipes = [r for r in filtered_recipes if dietary_filter in r.tags]
    
    if difficulty_filter != 'all':
        filtered_recipes = [r for r in filtered_recipes if r.difficulty == difficulty_filter]

    if max_time_filter:
        filtered_recipes = [r for r in filtered_recipes if r.cook_time <= max_time_filter]

    # 3. Perform ingredient matching on the filtered list
    data = request.json
    ingredients_from_user = data.get("ingredients", {}).keys()
    
    scores = []
    for recipe in filtered_recipes:
        score, substitutions = calculate_match_score(recipe.ingredients.keys(), ingredients_from_user)
        if score > 0.1:
            scores.append((recipe.name, score, substitutions))
            
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # 4. Format results
    results = []
    for r_name, score, subs in scores[:10]:
        rec = recipe_store[r_name]
        results.append({
            "name": rec.name,
            "difficulty": rec.difficulty,
            "cook_time": rec.cook_time,
            "cuisine": rec.cuisine,
            "image_url": rec.image_url,
            "substitutions": subs
        })
    return jsonify({"recipes": results})

@recipes_bp.route("/all", methods=["GET"])
@token_required
def get_all_recipes(current_user):
    results = []
    sorted_recipes = sorted(recipe_store.values(), key=lambda r: r.name)

    for rec in sorted_recipes:
        results.append({
            "name": rec.name,
            "difficulty": rec.difficulty,
            "cook_time": rec.cook_time,
            "cuisine": rec.cuisine,
            "image_url": rec.image_url,
            "substitutions": {}
        })
    return jsonify({"recipes": results})

@recipes_bp.route("/favorites", methods=["POST"])
@token_required
def add_favorite(current_user):
    data = request.get_json()
    recipe_name = data.get('recipe_name')

    if not recipe_name or recipe_name not in recipe_store:
        return jsonify({'message': 'Invalid recipe name supplied'}), 400

    existing_fav = FavoriteRecipe.query.filter_by(user_id=current_user.id, recipe_name=recipe_name).first()
    if existing_fav:
        return jsonify({'message': 'Recipe is already in your favorites'}), 409

    new_favorite = FavoriteRecipe(user_id=current_user.id, recipe_name=recipe_name)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({'message': 'Recipe added to favorites successfully!'}), 201

@recipes_bp.route("/favorites", methods=["GET"])
@token_required
def get_favorites(current_user):
    favorite_entries = FavoriteRecipe.query.filter_by(user_id=current_user.id).all()
    favorite_recipe_names = [f.recipe_name for f in favorite_entries]
    
    results = []
    for name in favorite_recipe_names:
        rec = recipe_store.get(name)
        if rec:
            results.append({
                "name": rec.name,
                "difficulty": rec.difficulty,
                "cook_time": rec.cook_time,
                "cuisine": rec.cuisine,
                "image_url": rec.image_url,
                "substitutions": {}
            })
            
    return jsonify({"recipes": results})

@recipes_bp.route("/recipe/<recipe_name>")
@token_required
def get_recipe_details(current_user, recipe_name):
    recipe = recipe_store.get(recipe_name)
    if not recipe:
        return jsonify({"message": "Recipe not found"}), 404
    return jsonify(vars(recipe))

@recipes_bp.route("/rate", methods=["POST"])
@token_required
def rate_recipe(current_user):
    data = request.get_json()
    recipe_name = data.get('recipe_name')
    rating = data.get('rating')

    if not all([recipe_name, rating]) or recipe_name not in recipe_store:
        return jsonify({'message': 'Invalid data provided'}), 400
    
    existing_rating = RecipeRating.query.filter_by(user_id=current_user.id, recipe_name=recipe_name).first()
    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = RecipeRating(user_id=current_user.id, recipe_name=recipe_name, rating=rating)
        db.session.add(new_rating)
    
    db.session.commit()
    return jsonify({'message': 'Rating saved successfully'}), 200

@recipes_bp.route("/recipe/<recipe_name>/ratings", methods=["GET"])
@token_required
def get_recipe_ratings(current_user, recipe_name):
    if recipe_name not in recipe_store:
        return jsonify({"message": "Recipe not found"}), 404

    avg_rating, rating_count = db.session.query(
        func.avg(RecipeRating.rating), func.count(RecipeRating.id)
    ).filter(RecipeRating.recipe_name == recipe_name).first()
    
    user_rating_obj = RecipeRating.query.filter_by(user_id=current_user.id, recipe_name=recipe_name).first()
    user_rating = user_rating_obj.rating if user_rating_obj else 0

    return jsonify({
        "average_rating": float(avg_rating) if avg_rating else 0,
        "rating_count": rating_count if rating_count else 0,
        "user_rating": user_rating
    })

@recipes_bp.route("/suggestions", methods=["GET"])
@token_required
def get_suggestions(current_user):
    user_high_ratings = {r.recipe_name for r in RecipeRating.query.filter(
        RecipeRating.user_id == current_user.id, RecipeRating.rating >= 3
    ).all()}

    suggestions = []

    def get_top_rated_fallback():
        top_recipes = db.session.query(
            RecipeRating.recipe_name
        ).group_by(RecipeRating.recipe_name).order_by(
            func.avg(RecipeRating.rating).desc(), func.count(RecipeRating.id).desc()
        ).limit(5).all()
        return [r.recipe_name for r in top_recipes]

    if not user_high_ratings:
        suggestions = get_top_rated_fallback()
    else:
        similar_users = db.session.query(RecipeRating.user_id).filter(
            RecipeRating.recipe_name.in_(user_high_ratings),
            RecipeRating.user_id != current_user.id,
            RecipeRating.rating >= 3
        ).distinct().limit(50).all()
        
        similar_user_ids = [u.user_id for u in similar_users]

        if similar_user_ids:
            recommended_recipes = db.session.query(
                RecipeRating.recipe_name
            ).filter(
                RecipeRating.user_id.in_(similar_user_ids),
                RecipeRating.rating >= 3,
                ~RecipeRating.recipe_name.in_(user_high_ratings)
            ).group_by(RecipeRating.recipe_name).order_by(func.count(RecipeRating.user_id).desc()).limit(5).all()
            
            suggestions = [r.recipe_name for r in recommended_recipes]

        if not suggestions:
            suggestions = get_top_rated_fallback()

    results = []
    for name in suggestions:
        rec = recipe_store.get(name)
        if rec:
            results.append({
                "name": rec.name,
                "difficulty": rec.difficulty,
                "cook_time": rec.cook_time,
                "cuisine": rec.cuisine,
                "image_url": rec.image_url,
                "substitutions": {}
            })
    
    return jsonify({"recipes": results})

