# app/recipes.py
from flask import Blueprint, request, jsonify
from .utils import token_required
from .models import all_ingredients, recipe_store, SUBSTITUTION_MAP, FavoriteRecipe, UserProfile, db
import math
from clarifai.client.model import Model
import os

recipes_bp = Blueprint('recipes', __name__)

def to_vector(ingredient_dict):
    return [ingredient_dict.get(ing, 0.0) for ing in all_ingredients]

def cosine(vec1, vec2):
    dot_product = sum(x * y for x, y in zip(vec1, vec2))
    norm_a = math.sqrt(sum(x * x for x in vec1))
    norm_b = math.sqrt(sum(x * x for x in vec2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def calculate_match_score(recipe_ingredients, user_ingredients):
    perfect_matches = 0
    substitution_matches = 0
    made_substitutions = {}
    
    user_ingredients_set = set(user_ingredients)

    for required_ing in recipe_ingredients:
        if required_ing in user_ingredients_set:
            perfect_matches += 1
        else:
            found_substitute = False
            possible_subs = SUBSTITUTION_MAP.get(required_ing, [])
            for sub in possible_subs:
                if sub in user_ingredients_set:
                    substitution_matches += 1
                    made_substitutions[required_ing] = sub
                    found_substitute = True
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

        if CLARIFAI_PAT == "YOUR_VERIFIED_PERSONAL_ACCESS_TOKEN" or not CLARIFAI_PAT:
             return jsonify({'message': 'Server configuration error: PAT not set in recipes.py.'}), 500

        model = Model("https://clarifai.com/clarifai/main/models/food-item-recognition", pat=CLARIFAI_PAT)
        response = model.predict_by_bytes(image_bytes, input_type="image")
        
        print("--- Full Clarifai API Response ---")
        print(response)
        print("---------------------------------")

        if response.status.code != 10000:
             print(f"Clarifai API Error: {response.status.description}")
             return jsonify({'message': 'Image recognition failed due to API error.'}), 500

        concepts = response.outputs[0].data.concepts
        recognized_items = [concept.name.lower() for concept in concepts if concept.value > 0.4]
        final_ingredients = [item for item in recognized_items if item in all_ingredients]
        
        if not final_ingredients:
            return jsonify({'message': 'Could not recognize any known ingredients. Please try a clearer photo.'}), 404

        return jsonify({"recognized_ingredients": final_ingredients})

    except Exception as e:
        print(f"Clarifai Error: {e}")
        return jsonify({'message': 'Image recognition failed. Check server logs.'}), 500

@recipes_bp.route("/ingredients")
@token_required
def get_ingredients(current_user):
    return jsonify({"ingredients": all_ingredients})

@recipes_bp.route("/generate", methods=["POST"])
@token_required
def generate(current_user):
    user_preference = current_user.dietary_preference
    
    if user_preference == 'veg':
        filtered_recipes = {name: recipe for name, recipe in recipe_store.items() if recipe.diet_type == 'veg'}
    else:
        filtered_recipes = recipe_store
    
    data = request.json
    ingredients_from_user = data.get("ingredients", {}).keys()
    
    scores = []
    for recipe in filtered_recipes.values():
        score, substitutions = calculate_match_score(recipe.ingredients.keys(), ingredients_from_user)
        if score > 0.1:
            scores.append((recipe.name, score, substitutions))
            
    scores.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    for r_name, score, subs in scores[:5]:
        rec = filtered_recipes[r_name]
        results.append({
            "name": rec.name,
            "similarity": round(score, 2),
            "difficulty": rec.difficulty,
            "cook_time": rec.cook_time,
            "cuisine": rec.cuisine,
            "image_url": rec.image_url,
            "steps_snippet": rec.steps[0] if rec.steps else "Click for details.",
            "substitutions": subs
        })
    return jsonify({"recipes": results})

@recipes_bp.route("/all", methods=["GET"])
@token_required
def get_all_recipes(current_user):
    results = []
    # Sort recipes alphabetically for a consistent order
    sorted_recipes = sorted(recipe_store.values(), key=lambda r: r.name)

    for rec in sorted_recipes:
        results.append({
            "name": rec.name,
            "difficulty": rec.difficulty,
            "cook_time": rec.cook_time,
            "cuisine": rec.cuisine,
            "image_url": rec.image_url,
            "substitutions": {} # Not needed for list view
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
                "substitutions": {} # Not needed for favorite list view
            })
            
    return jsonify({"recipes": results})

@recipes_bp.route("/recipe/<recipe_name>")
@token_required
def get_recipe_details(current_user, recipe_name):
    recipe = recipe_store.get(recipe_name)
    if not recipe:
        return jsonify({"message": "Recipe not found"}), 404
    return jsonify(vars(recipe))
