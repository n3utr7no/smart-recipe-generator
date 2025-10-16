from .extensions import bcrypt
from . import db

class Recipe:
    def __init__(self, name, ingredients, steps, nutrition, difficulty, cook_time, cuisine, image_url, reviews, tags, servings):
        self.name = name
        self.ingredients = {k.lower(): float(v) for k, v in ingredients.items()}
        self.steps = steps
        self.nutrition = nutrition
        self.difficulty = difficulty
        self.cook_time = cook_time
        self.cuisine = cuisine
        self.image_url = image_url
        self.reviews = reviews
        self.tags = tags
        self.servings = servings

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    favorites = db.relationship('FavoriteRecipe', backref='user', lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship('RecipeRating', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class FavoriteRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    recipe_name = db.Column(db.String(150), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_name', name='_user_recipe_uc'),)

class RecipeRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    recipe_name = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # Rating from 1 to 5
    # A user can only rate a recipe once
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_name', name='_user_rating_uc'),)

all_ingredients = []
recipe_store = {}

SUBSTITUTION_MAP = {
    "beef": ["lamb", "ground beef", "pork"],
    "lamb": ["beef", "ground beef"],
    "pork": ["beef", "chicken"],
    "butter": ["olive oil"],
    "cheddar cheese": ["mozzarella", "parmesan"],
    "mozzarella": ["cheddar cheese", "parmesan"],
    "parmesan": ["cheddar cheese", "mozzarella"],
    "lime": ["lemon"],
    "lemon": ["lime"],
    "onion": ["shallot"],
    "yogurt": ["cream"],
    "rice": ["noodles"],
    "pasta": ["noodles", "rice"],
    "noodles": ["pasta", "rice"],
    "shrimp": ["fish", "chicken"]
}

def add_recipe(name, ingredients, *args):
    recipe_store[name] = Recipe(name, ingredients, *args)
    for k in ingredients.keys():
        if k.lower() not in all_ingredients:
            all_ingredients.append(k.lower())

def init_data():
    global all_ingredients, recipe_store
    all_ingredients = []
    recipe_store = {}

    img_pasta = "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2360"
    img_chicken_rice = "https://plus.unsplash.com/premium_photo-1694141252774-c937d97641da?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=776"
    img_paneer_curry = "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=774"
    img_butter_chicken = "https://plus.unsplash.com/premium_photo-1661419883163-bb4df1c10109?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=774"
    img_chana_masala = "https://media.istockphoto.com/id/1474839044/photo/floating-vegetable-baked-in-little-pan-on-green.webp?a=1&b=1&s=612x612&w=0&k=20&c=uD3QvbhYniKjPPTjyr3xsWnhVw2NEP-c3KMpI1B-xJY="
    img_palak_paneer = "https://images.unsplash.com/photo-1589647363585-f4a7d3877b10?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1744"
    img_lentil_soup = "https://images.unsplash.com/photo-1626500154744-e4b394ffea16?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1740"
    img_carbonara = "https://images.unsplash.com/photo-1608756687911-aa1599ab3bd9?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=774"
    img_risotto = "https://images.unsplash.com/photo-1664214649073-f4250ad39390?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=774"
    img_lasagna = "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=870"
    img_fajitas = "https://plus.unsplash.com/premium_photo-1679986537856-f13d1b30204c?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=774"
    img_burrito_bowl = "https://images.unsplash.com/photo-1668665771757-4d42737d295a?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YnVycml0byUyMGJvd2x8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&q=60&w=600"
    img_fish_tacos = "https://images.unsplash.com/photo-1604467715878-83e57e8bc129?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZmlzaCUyMHRhY29zfGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_fried_rice = "https://images.unsplash.com/photo-1603133872878-684f208fb84b?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZnJpZWQlMjByaWNlfGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_pad_thai = "https://images.unsplash.com/photo-1637806930600-37fa8892069d?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cGFkJTIwdGhhaXxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&q=60&w=600"
    img_mapo_tofu = "https://plus.unsplash.com/premium_photo-1712604940796-1a1dd9021bf1?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8bWFwbyUyMHRvZnV8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&q=60&w=600"
    img_zucchini = "https://images.unsplash.com/photo-1563252722-6434563a985d?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8enVjY2hpbml8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&q=60&w=600"
    img_mac_cheese = "https://plus.unsplash.com/premium_photo-1661677825991-caa232fea9da?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bWFjJTIwY2hlZXNlfGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_cheeseburger = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2hlZXNlJTIwYnVyZ2VyfGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_salmon = "https://images.unsplash.com/photo-1499125562588-29fb8a56b5d5?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c2FsbW9ufGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_shepherds_pie = "https://plus.unsplash.com/premium_photo-1726718442760-cccbd5f1e252?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8c2hlcGVyZCUyMHBpZXxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&q=60&w=600"
    img_broccoli_soup = "https://plus.unsplash.com/premium_photo-1711125003788-c1fe4c2bc421?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8YnJvY29sbGklMjBzb3VwfGVufDB8fDB8fHww&auto=format&fit=crop&q=60&w=600"
    img_chicken_noodle = "https://images.unsplash.com/photo-1644083152667-2c78739e882a?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8Y2hpY2tlbiUyMG5vb2RsZXxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&q=60&w=600"
    img_greek_salad = "https://images.unsplash.com/photo-1599021419847-d8a7a6aba5b4?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Z3JlZWslMjBzYWxhZHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&q=60&w=600"
    img_french_onion = "https://www.recipetineats.com/tachyon/2018/11/French-Onion-Soup_1.jpg"
    img_pancakes = "https://hips.hearstapps.com/hmg-prod/images/best-homemade-pancakes-index-640775a2dbad8.jpg?crop=0.8890503582601677xw:1xh;center,top&resize=1200:*"
    img_scrambled_eggs = "https://cdn.loveandlemons.com/wp-content/uploads/2021/05/scrambled-eggs.jpg"
    img_avocado_toast = "https://alegumeaday.com/wp-content/uploads/2024/03/Bean-avocado-toast-3.jpg"
    img_stuffed_peppers = "https://embed.widencdn.net/img/beef/t9bwp7fitq/exact/Stuffed%20Peppers%20-%20NCBA%20Beef%20Aug%20202431717.jpg?keep=c&u=7fueml"
    img_cabbage_salad = "https://www.eatingwell.com/thmb/QlftacWORbiPiWx194pBjVvQwco=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/simple-cabbage-salad-1x1-a7431961d8d948efad5ed24f4865baec.jpg"

    add_recipe("Spaghetti Carbonara", {"pasta": 200, "egg": 2, "bacon": 100, "parmesan": 50}, 
    [
        "Bring a large pot of salted water to a boil and cook spaghetti until al dente. Reserve about 1 cup of pasta water before draining.",
        "While the pasta cooks, dice the bacon or pancetta. Cook in a large skillet over medium heat until crisp. Turn off the heat.",
        "In a separate bowl, whisk together the eggs, grated Parmesan cheese, and a generous amount of freshly cracked black pepper.",
        "Once cooked, immediately transfer the drained hot pasta to the skillet with the bacon and its rendered fat. Toss to combine.",
        "Quickly pour the egg and cheese mixture over the pasta, stirring vigorously. The heat from the pasta will cook the eggs and create a creamy sauce.",
        "If the sauce is too thick, add a splash of the reserved pasta water until it reaches your desired consistency. Serve immediately."
    ], 
    {"calories": 800, "protein": 35, "carbs": 75, "fat": 40}, "Medium", 25, "Italian", img_carbonara, [], [], 2)

    add_recipe("Mushroom Risotto", {"rice": 200, "mushroom": 150, "vegetable broth": 500, "parmesan": 40, "onion": 50}, 
        [
            "In a saucepan, bring the vegetable broth to a simmer over low heat. Keep it warm.",
            "In a separate large pot, melt butter with olive oil over medium heat. Add the chopped onion and sauté until soft.",
            "Add the sliced mushrooms and cook until browned. Season with salt and pepper.",
            "Add the Arborio rice and stir for 2 minutes until the grains are translucent at the edges.",
            "Pour in a ladle of warm broth and stir continuously until the liquid is almost fully absorbed.",
            "Continue adding broth one ladle at a time, allowing each addition to be absorbed before adding the next. This will take about 20-25 minutes.",
            "Once the rice is creamy and al dente, remove from heat. Stir in the grated Parmesan cheese and a knob of butter. Serve immediately."
        ], 
        {"calories": 600, "protein": 18, "carbs": 90, "fat": 15}, "Hard", 45, "Italian", img_risotto, [], ['veg', 'gluten-free'], 2)

    add_recipe("Beef Lasagna", {"ground beef": 250, "lasagna noodles": 150, "tomato": 200, "mozzarella": 100, "onion": 50}, 
        [
            "Prepare the meat sauce: Brown ground beef with onions and garlic. Drain fat, stir in tomato sauce and seasonings, and simmer for at least 30 minutes.",
            "Prepare a simple béchamel or use ricotta cheese as a layer. Cook lasagna noodles according to package directions.",
            "Assemble the lasagna: Start with a layer of meat sauce, followed by noodles, then the cheese layer. Repeat until all ingredients are used, finishing with a layer of sauce and mozzarella.",
            "Bake in a preheated oven at 375°F (190°C) for 45-55 minutes, or until bubbly and golden brown on top. Let it rest for 10 minutes before slicing."
        ], 
        {"calories": 900, "protein": 45, "carbs": 80, "fat": 45}, "Hard", 90, "Italian", img_lasagna, [], [], 6)

    add_recipe("Chicken Fajitas", {"chicken": 200, "bell pepper": 150, "onion": 100, "corn tortillas": 4}, 
        [
            "Slice chicken, bell peppers, and onions into thin, uniform strips.",
            "Heat a large skillet over high heat with a bit of oil. Add the chicken and cook until browned and cooked through. Remove from skillet.",
            "Add the peppers and onions to the same skillet, cooking until tender-crisp and slightly charred.",
            "Return the chicken to the skillet, squeeze lime juice over everything, and toss to combine. Serve immediately with warm corn tortillas and desired toppings."
        ], 
        {"calories": 550, "protein": 30, "carbs": 40, "fat": 28}, "Easy", 25, "Mexican", img_fajitas, [], ['gluten-free'], 2)

    add_recipe("Veggie Burrito Bowl", {"rice": 150, "black beans": 100, "bell pepper": 100, "avocado": 50, "lime": 1}, 
        [
            "Cook rice according to package directions. Once cooked, fluff with a fork and stir in cilantro and a squeeze of lime juice.",
            "While rice cooks, sauté diced bell peppers and onions until soft. Warm up the black beans.",
            "Assemble the bowl: Start with a base of cilantro-lime rice. Top with the sautéed vegetables, black beans, and freshly sliced avocado.",
            "Serve with salsa, a dollop of yogurt or sour cream, and extra lime wedges."
        ], 
        {"calories": 500, "protein": 12, "carbs": 85, "fat": 15}, "Easy", 20, "Mexican", img_burrito_bowl, [], ['veg', 'gluten-free'], 1)

    add_recipe("Fish Tacos", {"fish": 200, "cabbage": 100, "lime": 1, "corn tortillas": 4, "yogurt": 50}, 
        [
            "Cut fish fillets into strips and season with chili powder, cumin, and salt. Pan-fry or grill until cooked through and flaky.",
            "Prepare a simple slaw by thinly shredding cabbage and tossing it with lime juice and a pinch of salt.",
            "Warm the corn tortillas in a dry skillet or microwave.",
            "Assemble the tacos: Place a piece of fish in each tortilla, top with the slaw, and a drizzle of a creamy yogurt or sour cream sauce."
        ], 
        {"calories": 450, "protein": 30, "carbs": 35, "fat": 20}, "Easy", 20, "Mexican", img_fish_tacos, [], ['gluten-free'], 2)

    add_recipe("Veggie Fried Rice", {"rice": 200, "egg": 1, "carrot": 50, "soy sauce": 30, "onion": 30}, 
        [
            "Use cold, day-old cooked rice for best results. Heat a wok or large skillet over high heat with oil.",
            "Add diced carrots and onions, stir-frying for 2-3 minutes until slightly softened. Push vegetables to one side of the wok.",
            "Pour a lightly beaten egg onto the empty side of the wok. Scramble until just cooked, then mix it in with the vegetables.",
            "Add the cold rice to the wok, breaking up any clumps. Stir-fry for 3-4 minutes, then drizzle with soy sauce (use Tamari for gluten-free) and toss everything to combine evenly. Serve hot."
        ], 
        {"calories": 450, "protein": 10, "carbs": 75, "fat": 12}, "Easy", 15, "Asian", img_fried_rice, [], ['veg', 'gluten-free'], 2)

    add_recipe("Pad Thai", {"noodles": 150, "shrimp": 100, "tofu": 50, "peanut": 20, "egg": 1}, 
        [
            "Soak rice noodles in warm water until pliable, then drain. Prepare the sauce by mixing fish sauce, tamarind paste, sugar, and lime juice.",
            "Heat oil in a wok. Stir-fry shrimp and cubed tofu until cooked. Push to one side.",
            "Add the drained noodles to the wok, tossing them in the oil. Add the sauce and stir-fry until the noodles have absorbed it.",
            "Push noodles to the side, crack an egg into the empty space and scramble it. Mix everything together and serve garnished with crushed peanuts, fresh cilantro, and lime wedges."
        ], 
        {"calories": 700, "protein": 25, "carbs": 90, "fat": 25}, "Medium", 30, "Thai", img_pad_thai, [], ['gluten-free'], 2)

    add_recipe("Mapo Tofu", {"tofu": 250, "pork": 50, "soy sauce": 30}, 
        [
            "Stir-fry ground pork (optional, can be omitted for veg version) until crispy. Add chili bean paste, fermented black beans, and garlic.",
            "Add broth and bring to a simmer. Gently add cubes of soft tofu to the sauce.",
            "Thicken the sauce with a cornstarch slurry.",
            "Finish with a drizzle of sesame oil and garnish with Szechuan peppercorns and scallions."
        ], 
        {"calories": 400, "protein": 20, "carbs": 10, "fat": 30}, "Medium", 25, "Chinese", img_mapo_tofu, [], ['gluten-free'], 3)

    add_recipe("Zucchini Stir-Fry", {"zucchini": 200, "garlic": 10, "soy sauce": 15, "onion": 30}, 
        [
            "Heat a wok or large skillet over high heat with a tablespoon of oil.",
            "Add minced garlic and sliced onions, stir-frying for 30 seconds until fragrant.",
            "Add sliced zucchini and stir-fry for 3-5 minutes until it is tender-crisp.",
            "Drizzle with soy sauce (use Tamari for gluten-free), toss to combine, and serve immediately."
        ], 
        {"calories": 150, "protein": 5, "carbs": 10, "fat": 10}, "Easy", 10, "Asian", img_zucchini, [], ['veg', 'gluten-free'], 2)

    add_recipe("Macaroni and Cheese", {"macaroni": 200, "cheddar cheese": 100, "milk": 150, "butter": 30, "all-purpose flour": 20}, 
        [
            "Cook macaroni pasta according to package directions until al dente. Drain well.",
            "While the pasta cooks, melt butter in a saucepan over medium heat. Whisk in flour and cook for one minute to create a roux.",
            "Gradually whisk in milk until the sauce is smooth and slightly thickened. Bring to a simmer.",
            "Remove from heat and stir in the shredded cheddar cheese until completely melted and smooth. Season with salt and pepper. Pour the cheese sauce over the cooked macaroni and stir to combine."
        ], 
        {"calories": 800, "protein": 25, "carbs": 70, "fat": 45}, "Easy", 25, "American", img_mac_cheese, [], ['veg'], 4)

    add_recipe("Classic Cheeseburger", {"ground beef": 150, "bread": 1, "cheddar cheese": 30, "lettuce": 20, "tomato": 20}, 
        [
            "Gently form the ground beef into a patty, about 1-inch thick. Season both sides generously with salt and pepper.",
            "Preheat a grill or skillet over medium-high heat. Cook the patty for 3-5 minutes per side for medium-rare.",
            "During the last minute of cooking, place a slice of cheddar cheese on top of the patty to melt.",
            "Toast the bun lightly and assemble the burger with the patty, lettuce, and tomato slices."
        ], 
        {"calories": 600, "protein": 30, "carbs": 35, "fat": 38}, "Easy", 20, "American", img_cheeseburger, [], [], 1)

    add_recipe("Grilled Salmon", {"salmon": 200, "lemon": 1, "olive oil": 10, "garlic": 5}, 
        [
            "Preheat your grill to medium-high heat. Pat the salmon fillets dry with a paper towel.",
            "In a small bowl, mix together olive oil, minced garlic, salt, and pepper. Brush this mixture generously over both sides of the salmon.",
            "Place the salmon skin-side down on the preheated grill. Cook for 4-6 minutes per side, depending on thickness, flipping only once.",
            "The salmon is done when it flakes easily with a fork. Remove from grill and serve immediately with fresh lemon wedges squeezed over the top."
        ], 
        {"calories": 450, "protein": 40, "carbs": 2, "fat": 30}, "Easy", 15, "American", img_salmon, [], ['gluten-free'], 1)

    add_recipe("Shepherd's Pie", {"lamb": 250, "potato": 300, "carrot": 100, "onion": 50, "vegetable broth": 100}, 
        [
            "Peel and boil potatoes until tender. Drain, then mash with butter and milk until creamy. Season with salt and pepper.",
            "In a skillet, brown the ground lamb (or beef) with chopped onions and carrots. Drain excess fat.",
            "Stir in flour (use cornstarch for gluten-free), then gradually add vegetable broth and seasonings. Simmer until the filling has thickened.",
            "Spread the meat filling in the bottom of a baking dish. Top evenly with the mashed potatoes, creating a seal. Bake at 400°F (200°C) for 20-25 minutes until the topping is golden brown."
        ], 
        {"calories": 750, "protein": 30, "carbs": 50, "fat": 45}, "Medium", 75, "European", img_shepherds_pie, [], [], 4)

    add_recipe("Broccoli Cheddar Soup", {"broccoli": 300, "cheddar cheese": 100, "milk": 200, "onion": 50, "carrot": 50}, 
        [
            "In a large pot, melt butter and sauté finely chopped onion and shredded carrots until soft.",
            "Add broccoli florets and cover with vegetable broth. Bring to a boil, then reduce heat and simmer until the broccoli is very tender.",
            "Carefully transfer the soup to a blender (or use an immersion blender) and blend until smooth. Return to the pot.",
            "Over low heat, gradually stir in milk and shredded cheddar cheese. Do not let the soup boil after adding cheese. Stir until the cheese is melted and the soup is heated through."
        ], 
        {"calories": 450, "protein": 15, "carbs": 20, "fat": 35}, "Easy", 30, "American", img_broccoli_soup, [], ['veg', 'gluten-free'], 4)

    add_recipe("Chicken Noodle Soup", {"chicken": 150, "noodles": 100, "carrot": 50, "onion": 50}, 
        [
            "In a large pot, combine chicken, chopped carrots, onions, and celery with enough water or chicken broth to cover.",
            "Bring to a boil, then reduce heat and simmer for about 30 minutes, or until the chicken is cooked through.",
            "Remove the chicken from the pot, shred it using two forks, and return it to the pot.",
            "Bring the soup back to a simmer and add the egg noodles. Cook until the noodles are tender, about 7-10 minutes. Season with salt, pepper, and fresh herbs before serving."
        ], 
        {"calories": 350, "protein": 25, "carbs": 30, "fat": 15}, "Easy", 40, "American", img_chicken_noodle, [], [], 4)

    add_recipe("Greek Salad", {"tomato": 100, "lettuce": 150, "cheese": 50, "olive oil": 10, "onion": 30}, 
        [
            "In a large salad bowl, combine chopped lettuce, tomatoes, sliced red onion, and cucumbers.",
            "Crumble a block of feta cheese over the top of the vegetables.",
            "In a small jar, shake together olive oil, lemon juice (or red wine vinegar), and a pinch of oregano to make the dressing.",
            "Drizzle the dressing over the salad just before serving and toss gently to combine."
        ], 
        {"calories": 300, "protein": 8, "carbs": 10, "fat": 25}, "Easy", 10, "Mediterranean", img_greek_salad, [], ['veg', 'gluten-free'], 2)

    add_recipe("French Onion Soup", {"onion": 400, "vegetable broth": 500, "bread": 2, "cheese": 50}, 
        [
            "Thinly slice a large amount of onions. In a large pot, melt butter and cook the onions over low heat for 25-30 minutes until deeply caramelized and sweet.",
            "Deglaze the pot with a splash of white wine or just add the vegetable (or beef) broth. Bring to a simmer.",
            "Season with salt and pepper and let it simmer for another 15 minutes.",
            "Ladle the soup into oven-safe bowls. Top each with a slice of toasted bread and a generous amount of Gruyère or Swiss cheese. Broil until the cheese is melted and bubbly."
        ], 
        {"calories": 400, "protein": 15, "carbs": 45, "fat": 18}, "Medium", 60, "European", img_french_onion, [], ['veg'], 2)

    add_recipe("Classic Pancakes", {"all-purpose flour": 150, "egg": 1, "milk": 150, "sugar": 20, "butter": 20}, 
        [
            "In a large bowl, whisk together flour, sugar, baking powder, and salt.",
            "In a separate medium bowl, whisk together milk and egg. Melt the butter and whisk it into the milk mixture.",
            "Pour the wet ingredients into the dry ingredients and stir until just combined. Do not overmix; a few lumps are okay.",
            "Heat a lightly oiled griddle or frying pan over medium-high heat. Pour or scoop the batter onto the griddle, using approximately 1/4 cup for each pancake. Cook until bubbles appear on the surface, then flip and cook until golden brown."
        ], 
        {"calories": 400, "protein": 10, "carbs": 60, "fat": 12}, "Easy", 20, "American", img_pancakes, [], ['veg'], 2)

    add_recipe("Scrambled Eggs", {"egg": 3, "milk": 30, "butter": 10}, 
        [
            "Crack eggs into a bowl and whisk vigorously with milk, salt, and pepper until the mixture is uniform and slightly frothy.",
            "Melt butter in a non-stick skillet over low to medium-low heat. Do not let it brown.",
            "Pour the egg mixture into the skillet. Let it sit for about 20-30 seconds until the edges begin to set.",
            "Gently push the eggs from the edges toward the center with a spatula, creating soft curds. Continue this process until the eggs are mostly set but still slightly moist. Remove from heat and serve immediately."
        ], 
        {"calories": 300, "protein": 20, "carbs": 2, "fat": 24}, "Easy", 5, "Universal", img_scrambled_eggs, [], ['gluten-free'], 1)

    add_recipe("Avocado Toast", {"bread": 2, "avocado": 1, "lemon": 1, "egg": 1}, 
        [
            "Toast your slices of bread to your desired level of crispness.",
            "While the bread is toasting, cut the avocado in half, remove the pit, and scoop the flesh into a bowl.",
            "Mash the avocado with a fork. Squeeze in some fresh lemon juice and season with salt, pepper, and optional red pepper flakes. Mix well.",
            "Spread the mashed avocado mixture evenly over the warm toast. For extra protein, top with a fried or poached egg."
        ], 
        {"calories": 350, "protein": 12, "carbs": 30, "fat": 20}, "Easy", 5, "Universal", img_avocado_toast, [], ['veg'], 1)

    add_recipe("Stuffed Bell Peppers", {"bell pepper": 2, "ground beef": 150, "rice": 50, "tomato": 50, "onion": 30}, 
        [
            "Cut bell peppers in half lengthwise and remove seeds. Par-boil or roast them for 10 minutes to soften.",
            "While peppers cook, brown ground beef with chopped onion in a skillet. Drain fat.",
            "Stir in cooked rice, diced tomatoes, and seasonings like oregano and garlic powder.",
            "Spoon the filling into the pepper halves, top with cheese if desired, and bake at 375°F (190°C) for 20-25 minutes until heated through and peppers are tender."
        ], 
        {"calories": 500, "protein": 28, "carbs": 40, "fat": 25}, "Medium", 60, "Mediterranean", img_stuffed_peppers, [], ['gluten-free'], 2)

    add_recipe("Simple Cabbage Salad", {"cabbage": 200, "carrot": 50, "vinegar": 10, "olive oil": 10}, 
        [
            "Thinly shred the cabbage and carrots using a knife or mandoline slicer. Place them in a large bowl.",
            "In a small bowl, whisk together olive oil, vinegar, a pinch of sugar, salt, and pepper to create a simple vinaigrette.",
            "Pour the dressing over the shredded vegetables.",
            "Toss everything together until well combined. For best results, let the salad sit for at least 15 minutes before serving to allow the flavors to meld."
        ], 
        {"calories": 150, "protein": 2, "carbs": 15, "fat": 10}, "Easy", 10, "Universal", img_cabbage_salad, [], ['veg', 'gluten-free'], 4)