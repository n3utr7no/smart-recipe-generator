# app/models.py
from .extensions import bcrypt
from . import db

class Recipe:
    def __init__(self, name, ingredients, steps, nutrition, difficulty, cook_time, cuisine, image_url, reviews, diet_type):
        self.name = name
        self.ingredients = {k.lower(): float(v) for k, v in ingredients.items()}
        self.steps = steps
        self.nutrition = nutrition
        self.difficulty = difficulty
        self.cook_time = cook_time
        self.cuisine = cuisine
        self.image_url = image_url
        self.reviews = reviews
        self.diet_type = diet_type

# app/models.py
# ... imports ...

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # NEW: Add a name column
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    dietary_preference = db.Column(db.String(50), nullable=False)
    favorites = db.relationship('FavoriteRecipe', backref='user', lazy=True, cascade="all, delete-orphan")

    # UPDATED: Modify __init__ to accept 'name'
    def __init__(self, email, password, dietary_preference, name):
        self.name = name
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.dietary_preference = dietary_preference

# ... rest of the file is unchanged ...

# Add this new model for storing favorites
class FavoriteRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    recipe_name = db.Column(db.String(150), nullable=False)
    # Ensure a user can't favorite the same recipe twice
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_name', name='_user_recipe_uc'),)

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

# app/models.py

# ... (keep all the existing code above init_data) ...

def init_data():
    global all_ingredients, recipe_store
    # Reset stores to prevent duplicates on app reload
    all_ingredients = []
    recipe_store = {}

    # Image URLs for recipes
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

    add_recipe("Tomato Pasta", {"tomato": 200, "pasta": 150, "garlic": 10, "cheese": 30, "basil": 10}, 
        [
            "Bring a large pot of salted water to a boil. Add the pasta and cook according to package directions until al dente.",
            "While the pasta is cooking, heat a tablespoon of olive oil in a large skillet or pan over medium heat.",
            "Add the minced garlic and sauté for about 30-60 seconds until fragrant, being careful not to burn it.",
            "Pour in the crushed tomatoes. Season with salt, pepper, and fresh chopped basil. Stir to combine.",
            "Bring the sauce to a simmer and then reduce the heat to low. Let it cook for at least 10 minutes to allow the flavors to meld.",
            "Once the pasta is cooked, drain it well and add it directly to the skillet with the tomato sauce.",
            "Toss everything together until the pasta is evenly coated with the sauce. Serve immediately, topped with grated cheese."
        ], 
        {"calories": 450, "protein": 15, "carbs": 60, "fat": 15}, "Easy", 20, "Italian", img_pasta, [], 'veg')

    add_recipe("Chicken Rice", {"chicken": 200, "rice": 150, "onion": 50, "garlic": 10}, 
        [
            "In a medium pot, heat a tablespoon of oil over medium heat. Add the chopped onion and sauté until softened, about 3-4 minutes.",
            "Add the minced garlic and cook for another minute until fragrant.",
            "Add the chicken pieces to the pot and cook until they are browned on all sides.",
            "Stir in the uncooked rice and toast it for about a minute, stirring constantly.",
            "Pour in 300ml of chicken broth or water. Season generously with salt and pepper.",
            "Bring the mixture to a boil, then reduce the heat to low, cover the pot with a tight-fitting lid, and let it simmer for 18-20 minutes.",
            "Remove the pot from the heat and let it stand, covered, for 5-10 minutes before fluffing the rice with a fork and serving."
        ], 
        {"calories": 600, "protein": 40, "carbs": 65, "fat": 18}, "Medium", 40, "Asian", img_chicken_rice, [], 'non-veg')

    add_recipe("Paneer Curry", {"paneer": 200, "tomato": 100, "onion": 50, "ginger": 5, "garlic": 5}, 
        [
            "Heat a tablespoon of oil in a pan over medium heat. Add the chopped onions and cook until they turn golden brown.",
            "Add the minced ginger and garlic paste and sauté for another minute until the raw smell disappears.",
            "Stir in the tomato puree along with spices like turmeric, coriander, and cumin powder. Cook this masala mixture until the oil begins to separate from the paste.",
            "Pour in about 1/2 cup of water to form a gravy. Stir well and bring the mixture to a gentle simmer.",
            "Gently add the paneer cubes to the gravy. Be careful not to break them.",
            "Cover the pan and let the curry simmer for 5-7 minutes, allowing the paneer to absorb the flavors of the gravy.",
            "Garnish with fresh cilantro before serving."
        ], 
        {"calories": 550, "protein": 22, "carbs": 30, "fat": 38}, "Medium", 35, "Indian", img_paneer_curry, [], 'veg')
    add_recipe("Butter Chicken", {"chicken": 250, "tomato": 150, "butter": 50, "cream": 50, "ginger": 10, "garlic": 10}, 
        [
            "In a bowl, mix the chicken pieces with yogurt, ginger-garlic paste, and spices (like garam masala, turmeric, and chili powder). Let it marinate for at least 30 minutes.",
            "Heat a grill or a pan with a little oil. Cook the marinated chicken pieces until they are cooked through and have a slight char on the outside. Set aside.",
            "For the gravy, melt butter in a large pan over medium heat. Sauté chopped onions until soft, then add tomato puree. Cook for 10-15 minutes until the sauce thickens and darkens in color.",
            "Let the gravy cool slightly, then transfer it to a blender and blend until completely smooth. Strain it back into the pan for an extra silky texture.",
            "Add the cooked chicken to the smooth gravy. Stir in the cream, a pinch of sugar (to balance acidity), and simmer for 5-10 minutes.",
            "Serve hot, garnished with a swirl of cream or a knob of butter."
        ], 
        {"calories": 700, "protein": 30, "carbs": 15, "fat": 58}, "Medium", 45, "Indian", img_butter_chicken, [], 'non-veg')

    add_recipe("Chana Masala", {"chickpeas": 300, "tomato": 150, "onion": 50, "ginger": 10, "garlic": 10}, 
        [
            "Heat oil in a pan over medium heat. Add finely chopped onions and sauté until they are deep golden brown.",
            "Add ginger-garlic paste and cook for one minute until fragrant.",
            "Stir in powdered spices (turmeric, coriander, cumin, and chana masala powder). Sauté for 30 seconds, then add the tomato puree.",
            "Cook this masala mixture, stirring occasionally, until the oil begins to separate from the paste. This is a crucial step for a flavorful base.",
            "Add the boiled chickpeas along with about 1 cup of their cooking water. Bring to a simmer.",
            "Using the back of a spoon, mash some of the chickpeas against the side of the pan. This helps to thicken the gravy naturally.",
            "Simmer for at least 15 minutes, allowing the flavors to meld together. Garnish with cilantro and serve."
        ], 
        {"calories": 450, "protein": 15, "carbs": 70, "fat": 12}, "Easy", 30, "Indian", img_chana_masala, [], 'veg')
        
    add_recipe("Palak Paneer", {"spinach": 300, "paneer": 200, "onion": 50, "cream": 30, "garlic": 10}, 
        [
            "Wash the spinach thoroughly. Bring a pot of water to a boil, add the spinach and blanch for 2 minutes. Immediately drain and transfer to a bowl of ice-cold water to preserve its vibrant green color.",
            "Blend the blanched spinach into a smooth puree. Set aside.",
            "Cut the paneer into cubes. Heat a little oil in a non-stick pan and lightly pan-fry the paneer cubes until they are golden on all sides. Set aside.",
            "In the same pan, heat a tablespoon of oil or ghee. Add chopped onions and minced garlic, and sauté until fragrant and lightly browned.",
            "Pour in the spinach puree and cook for about 5 minutes, stirring occasionally.",
            "Add the fried paneer cubes and the cream to the spinach gravy. Season with salt and a pinch of garam masala.",
            "Stir gently and simmer for another 2-3 minutes. Serve hot."
        ], 
        {"calories": 500, "protein": 20, "carbs": 15, "fat": 40}, "Medium", 40, "Indian", img_palak_paneer, [], 'veg')
        
    add_recipe("Lentil Soup (Dal)", {"lentils": 200, "tomato": 100, "turmeric": 5, "garlic": 10}, 
        [
            "Rinse the lentils under cold water until the water runs clear. In a pot, combine the lentils with 4 cups of water, chopped tomatoes, and turmeric powder.",
            "Bring the mixture to a boil, then reduce the heat to a simmer. Cook for 25-30 minutes, or until the lentils are soft and have broken down.",
            "While the lentils are cooking, prepare the tempering (tadka). Heat ghee or oil in a small pan over medium heat.",
            "Add cumin seeds and let them splutter. Then add finely chopped garlic and dried red chilies. Sauté until the garlic turns golden brown.",
            "Carefully pour the hot tempering over the cooked lentils. You should hear a sizzling sound.",
            "Stir everything together well. Season with salt to taste.",
            "Garnish with fresh cilantro and serve hot with rice or bread."
        ], 
        {"calories": 350, "protein": 18, "carbs": 60, "fat": 4}, "Easy", 35, "Indian", img_lentil_soup, [], 'veg')
    add_recipe("Spaghetti Carbonara", {"pasta": 200, "egg": 2, "bacon": 100, "parmesan": 50}, 
    [
        "Bring a large pot of salted water to a boil and cook spaghetti until al dente. Reserve about 1 cup of pasta water before draining.",
        "While the pasta cooks, dice the bacon or pancetta. Cook in a large skillet over medium heat until crisp. Turn off the heat.",
        "In a separate bowl, whisk together the eggs, grated Parmesan cheese, and a generous amount of freshly cracked black pepper.",
        "Once cooked, immediately transfer the drained hot pasta to the skillet with the bacon and its rendered fat. Toss to combine.",
        "Quickly pour the egg and cheese mixture over the pasta, stirring vigorously. The heat from the pasta will cook the eggs and create a creamy sauce.",
        "If the sauce is too thick, add a splash of the reserved pasta water until it reaches your desired consistency. Serve immediately."
    ], 
    {"calories": 800, "protein": 35, "carbs": 75, "fat": 40}, "Medium", 25, "Italian", img_carbonara, [], 'non-veg')

    add_recipe("Mushroom Risotto", {"rice": 200, "mushroom": 150, "vegetable broth": 500, "parmesan": 40, "onion": 50}, 
    [
        "In a saucepan, bring the vegetable broth to a simmer over low heat. Keep it warm.",
        "In a separate large pot or Dutch oven, melt a tablespoon of butter with olive oil over medium heat. Add the chopped onion and sauté until soft and translucent.",
        "Add the sliced mushrooms and cook until they have released their moisture and started to brown. Season with salt and pepper.",
        "Add the Arborio rice to the pot and stir for about 2 minutes until the grains are coated and the edges look translucent.",
        "Pour in a ladle of the warm broth and stir continuously until the liquid is almost fully absorbed.",
        "Continue adding the broth one ladle at a time, allowing each addition to be absorbed before adding the next. This process should take about 20-25 minutes.",
        "Once the rice is creamy but still has a slight bite (al dente), remove it from the heat. Stir in the grated Parmesan cheese and a final knob of butter. Serve immediately."
    ], 
    {"calories": 600, "protein": 18, "carbs": 90, "fat": 15}, "Hard", 45, "Italian", img_risotto, [], 'veg')

    add_recipe("Beef Lasagna", {"ground beef": 250, "lasagna noodles": 150, "tomato": 200, "mozzarella": 100, "onion": 50}, 
    [
        "Prepare the meat sauce: In a large skillet, brown the ground beef with chopped onion and garlic. Drain excess fat. Stir in tomato sauce, and seasonings like oregano and basil. Simmer for at least 30 minutes.",
        "While the sauce simmers, cook the lasagna noodles according to package directions. Drain and lay them flat to prevent sticking.",
        "Preheat your oven to 375°F (190°C). In a baking dish, begin assembling the lasagna.",
        "Spread a thin layer of meat sauce on the bottom of the dish. Arrange a single layer of noodles on top.",
        "Spread a layer of ricotta or béchamel sauce over the noodles, followed by a layer of meat sauce, and a sprinkle of mozzarella.",
        "Repeat the layers until all ingredients are used, finishing with a final layer of meat sauce and a generous topping of mozzarella cheese.",
        "Bake for 45-55 minutes, or until the top is golden and bubbly. Let it rest for 10-15 minutes before slicing and serving."
    ], 
    {"calories": 900, "protein": 45, "carbs": 80, "fat": 45}, "Hard", 90, "Italian", img_lasagna, [], 'non-veg')

    add_recipe("Chicken Fajitas", {"chicken": 200, "bell pepper": 150, "onion": 100, "corn tortillas": 4}, 
    [
        "Slice the chicken, bell peppers, and onion into thin, uniform strips. Toss the chicken with fajita seasoning.",
        "Heat a tablespoon of oil in a large skillet or cast-iron pan over medium-high heat until it shimmers.",
        "Add the seasoned chicken to the hot pan in a single layer. Cook for 3-5 minutes, stirring occasionally, until browned and cooked through. Remove the chicken from the skillet and set aside.",
        "Add the sliced peppers and onions to the same skillet. Cook, stirring frequently, for 5-7 minutes until they are tender-crisp and have a slight char.",
        "Return the cooked chicken to the skillet with the vegetables. Squeeze the juice of half a lime over everything and toss to combine.",
        "Warm the corn tortillas in a dry skillet or in the microwave.",
        "Serve the chicken and vegetable mixture immediately with the warm tortillas and your favorite toppings like salsa, guacamole, or sour cream."
    ], 
    {"calories": 550, "protein": 30, "carbs": 40, "fat": 28}, "Easy", 25, "Mexican", img_fajitas, [], 'non-veg')

    add_recipe("Veggie Burrito Bowl", {"rice": 150, "black beans": 100, "bell pepper": 100, "avocado": 50, "lime": 1}, 
    [
        "Cook the rice according to package directions. Once cooked, fluff it with a fork and stir in fresh cilantro and a generous squeeze of lime juice. Set aside.",
        "While the rice cooks, heat a little oil in a skillet over medium heat. Add diced bell peppers and onions and sauté until soft and slightly caramelized.",
        "Rinse and drain the canned black beans. You can warm them in the microwave or in a small saucepan.",
        "Prepare your toppings: slice the avocado, chop any additional veggies like lettuce or tomato, and have your salsa ready.",
        "To assemble the bowl, start with a base of the cilantro-lime rice.",
        "Top the rice with the sautéed vegetables, a scoop of black beans, and the sliced avocado.",
        "Serve immediately with a dollop of yogurt or sour cream, salsa, and extra lime wedges on the side."
    ], 
    {"calories": 500, "protein": 12, "carbs": 85, "fat": 15}, "Easy", 20, "Mexican", img_burrito_bowl, [], 'veg')

    add_recipe("Fish Tacos", {"fish": 200, "cabbage": 100, "lime": 1, "corn tortillas": 4, "yogurt": 50}, 
    [
        "Cut the fish fillets into 1-inch strips. Season them with chili powder, cumin, salt, and pepper.",
        "Heat a tablespoon of oil in a skillet over medium-high heat. Place the fish strips in the pan and cook for 2-3 minutes per side, until cooked through and flaky. Remove from skillet.",
        "Prepare a simple slaw by thinly shredding the cabbage and tossing it in a bowl with the juice of half a lime and a pinch of salt.",
        "In a small bowl, mix the yogurt with a squeeze of lime juice and a little salt to create a simple crema.",
        "Warm the corn tortillas in a dry skillet for about 30 seconds per side or wrap in a damp paper towel and microwave for 30 seconds.",
        "To assemble the tacos, place a piece of cooked fish in each warm tortilla.",
        "Top with the crunchy cabbage slaw and a drizzle of the yogurt crema. Serve immediately with extra lime wedges."
    ], 
    {"calories": 450, "protein": 30, "carbs": 35, "fat": 20}, "Easy", 20, "Mexican", img_fish_tacos, [], 'non-veg')

    add_recipe("Veggie Fried Rice", {"rice": 200, "egg": 1, "carrot": 50, "soy sauce": 30, "onion": 30}, 
    [
        "For best results, use cold, day-old cooked rice. This prevents the fried rice from becoming mushy.",
        "Heat a wok or large skillet over high heat. Add a tablespoon of sesame or vegetable oil.",
        "Add the diced carrots and onions. Stir-fry for 2-3 minutes until they begin to soften.",
        "Push the vegetables to one side of the wok. Pour a lightly beaten egg onto the empty side. Scramble it with your spatula until just cooked, then break it up and mix it in with the vegetables.",
        "Add the cold rice to the wok. Use your spatula to break up any clumps. Stir-fry for 3-4 minutes, tossing everything to combine and heat the rice through.",
        "Drizzle the soy sauce over the rice and continue to stir-fry until everything is evenly coated and colored.",
        "Serve hot, optionally garnished with sliced green onions."
    ], 
    {"calories": 450, "protein": 10, "carbs": 75, "fat": 12}, "Easy", 15, "Asian", img_fried_rice, [], 'veg')

    add_recipe("Pad Thai", {"noodles": 150, "shrimp": 100, "tofu": 50, "peanut": 20, "egg": 1}, 
    [
        "Soak the rice noodles in warm water for about 15-20 minutes, or until pliable but not mushy. Drain well.",
        "In a small bowl, whisk together the Pad Thai sauce ingredients: fish sauce, tamarind paste, sugar, and a little water.",
        "Heat a wok or large skillet over high heat with oil. Add the shrimp and cubed tofu, and stir-fry until the shrimp is pink and the tofu is golden. Push everything to one side of the wok.",
        "Add the drained noodles to the wok, tossing them in the oil for a minute. Pour the sauce over the noodles and stir-fry until the noodles have absorbed most of it.",
        "Push the noodles to one side. Crack an egg into the empty space and scramble it quickly. Once cooked, mix it into the noodles.",
        "Add bean sprouts and half of the crushed peanuts. Toss everything together for another minute.",
        "Serve immediately, garnished with the remaining crushed peanuts, fresh cilantro, and lime wedges."
    ], 
    {"calories": 700, "protein": 25, "carbs": 90, "fat": 25}, "Medium", 30, "Thai", img_pad_thai, [], 'non-veg')

    add_recipe("Mapo Tofu", {"tofu": 250, "pork": 50, "soy sauce": 30}, 
    [
        "Cut the soft tofu into 1-inch cubes. Handle gently to prevent breaking.",
        "Heat oil in a wok over medium-high heat. Add the ground pork (if using) and stir-fry until it's crispy and browned. Remove from wok and set aside.",
        "In the same wok, add chili bean paste (doubanjiang), fermented black beans, and minced garlic. Stir-fry for a minute until fragrant.",
        "Pour in chicken or vegetable broth and the soy sauce. Bring the mixture to a simmer.",
        "Gently slide the tofu cubes into the sauce. Nudge them gently to coat, but avoid vigorous stirring. Simmer for 5 minutes.",
        "In a small bowl, mix cornstarch with a little cold water to make a slurry. Stir it into the simmering sauce to thicken it.",
        "Return the cooked pork to the wok. Drizzle with sesame oil and sprinkle with ground Szechuan peppercorns and chopped scallions before serving."
    ], 
    {"calories": 400, "protein": 20, "carbs": 10, "fat": 30}, "Medium", 25, "Chinese", img_mapo_tofu, [], 'non-veg')

    add_recipe("Zucchini Stir-Fry", {"zucchini": 200, "garlic": 10, "soy sauce": 15, "onion": 30}, 
    [
        "Wash and slice the zucchini into half-moons. Thinly slice the onion and mince the garlic.",
        "Heat a wok or large skillet over high heat. Add a tablespoon of cooking oil.",
        "Once the oil is hot, add the minced garlic and sliced onions. Stir-fry for about 30 seconds until they become fragrant.",
        "Add the sliced zucchini to the wok. Stir-fry continuously for 3-5 minutes. You want the zucchini to be tender but still have a slight crunch.",
        "Drizzle the soy sauce over the zucchini and toss everything together to combine evenly.",
        "Cook for another 30 seconds.",
        "Serve immediately as a side dish."
    ], 
    {"calories": 150, "protein": 5, "carbs": 10, "fat": 10}, "Easy", 10, "Asian", img_zucchini, [], 'veg')

    add_recipe("Macaroni and Cheese", {"macaroni": 200, "cheddar cheese": 100, "milk": 150, "butter": 30, "all-purpose flour": 20}, 
    [
        "Cook the macaroni pasta in a large pot of salted boiling water according to package directions until al dente. Drain well and set aside.",
        "While the pasta cooks, melt the butter in a medium saucepan over medium heat.",
        "Whisk in the flour and cook for one minute, stirring constantly. This creates a 'roux' which will thicken the sauce.",
        "Gradually pour in the milk, whisking continuously to prevent lumps. Continue to cook, stirring, until the sauce thickens and coats the back of a spoon (about 5-7 minutes).",
        "Remove the saucepan from the heat. Add the shredded cheddar cheese and stir until it's completely melted and the sauce is smooth.",
        "Season the cheese sauce with salt and pepper to taste.",
        "Pour the cheese sauce over the cooked macaroni and stir until everything is well combined and creamy. Serve immediately."
    ], 
    {"calories": 800, "protein": 25, "carbs": 70, "fat": 45}, "Easy", 25, "American", img_mac_cheese, [], 'veg')

    add_recipe("Classic Cheeseburger", {"ground beef": 150, "bread": 1, "cheddar cheese": 30, "lettuce": 20, "tomato": 20}, 
    [
        "Gently form the ground beef into a patty that is slightly wider than your bun, as it will shrink during cooking. Press a small indent in the center to prevent it from puffing up. Season both sides generously with salt and pepper.",
        "Preheat a grill or a skillet over medium-high heat.",
        "Place the patty on the hot surface and cook for 3-5 minutes per side for a medium-rare burger. Do not press down on the patty as it cooks.",
        "During the last minute of cooking, place a slice of cheddar cheese on top of the patty to allow it to melt.",
        "While the patty cooks, lightly toast the inside of your bun on the grill or in the skillet.",
        "Assemble the burger: Place the cooked patty on the bottom bun, then top with lettuce, tomato slices, and any other desired condiments.",
        "Place the top bun on and serve immediately."
    ], 
    {"calories": 600, "protein": 30, "carbs": 35, "fat": 38}, "Easy", 20, "American", img_cheeseburger, [], 'non-veg')

    add_recipe("Grilled Salmon", {"salmon": 200, "lemon": 1, "olive oil": 10, "garlic": 5}, 
    [
        "Preheat your grill to medium-high heat and clean the grates well.",
        "Pat the salmon fillets completely dry with a paper towel. This is key to getting a crispy skin.",
        "In a small bowl, mix together the olive oil, minced garlic, salt, and pepper.",
        "Brush this mixture generously over both sides of the salmon fillets.",
        "Lightly oil the grill grates. Place the salmon skin-side down on the preheated grill.",
        "Cook for 4-6 minutes on the first side, depending on the thickness of the fillet. The salmon should release easily from the grill when it's ready to be flipped.",
        "Flip the salmon and cook for another 2-4 minutes until cooked to your desired doneness. The salmon is done when it flakes easily with a fork.",
        "Remove from the grill and serve immediately with fresh lemon wedges to squeeze over the top."
    ], 
    {"calories": 450, "protein": 40, "carbs": 2, "fat": 30}, "Easy", 15, "American", img_salmon, [], 'non-veg')

    add_recipe("Shepherd's Pie", {"lamb": 250, "potato": 300, "carrot": 100, "onion": 50, "vegetable broth": 100}, 
    [
        "Peel the potatoes, cut them into chunks, and place them in a pot of cold salted water. Bring to a boil and cook until tender. Drain well, then mash with butter and milk until creamy. Season with salt and pepper and set aside.",
        "Preheat your oven to 400°F (200°C).",
        "In a large skillet, brown the ground lamb (or beef) with chopped onions and carrots over medium-high heat. Break up the meat as it cooks. Drain any excess fat.",
        "Stir in a tablespoon of flour to coat the meat. Then, gradually stir in the vegetable broth, Worcestershire sauce, and seasonings like thyme and rosemary.",
        "Bring the mixture to a simmer and cook for about 5 minutes until the filling has thickened.",
        "Spread the meat filling evenly in the bottom of a baking dish.",
        "Carefully top the filling with the mashed potatoes, spreading them to the edges to create a seal. Use a fork to create decorative ridges on top.",
        "Bake for 20-25 minutes, or until the topping is golden brown and the filling is bubbly. Let it rest for a few minutes before serving."
    ], 
    {"calories": 750, "protein": 30, "carbs": 50, "fat": 45}, "Medium", 75, "European", img_shepherds_pie, [], 'non-veg')

    add_recipe("Broccoli Cheddar Soup", {"broccoli": 300, "cheddar cheese": 100, "milk": 200, "onion": 50, "carrot": 50}, 
    [
        "In a large pot or Dutch oven, melt butter over medium heat. Add the finely chopped onion and shredded carrots and sauté until softened, about 5-7 minutes.",
        "Add the broccoli florets and cover with vegetable broth. Bring the mixture to a boil.",
        "Reduce the heat, cover, and simmer for 10-15 minutes, or until the broccoli is very tender.",
        "Use an immersion blender to blend the soup until smooth, directly in the pot. Alternatively, carefully transfer the soup in batches to a regular blender and blend until smooth, then return it to the pot.",
        "Reduce the heat to low. Gradually stir in the milk and the shredded cheddar cheese.",
        "Continue to stir gently until the cheese is completely melted and the soup is heated through. Do not let the soup boil after adding the cheese, as it can cause it to curdle.",
        "Season with salt and pepper to taste before serving."
    ], 
    {"calories": 450, "protein": 15, "carbs": 20, "fat": 35}, "Easy", 30, "American", img_broccoli_soup, [], 'veg')

    add_recipe("Chicken Noodle Soup", {"chicken": 150, "noodles": 100, "carrot": 50, "onion": 50}, 
    [
        "In a large pot, combine the chicken, chopped carrots, onions, and celery. Cover with enough water or chicken broth.",
        "Bring to a boil, then reduce the heat and simmer for about 30 minutes, or until the chicken is cooked through and tender.",
        "Carefully remove the chicken from the pot and place it on a cutting board. Once cool enough to handle, shred the meat using two forks, discarding any bones or skin.",
        "Return the shredded chicken to the pot.",
        "Bring the soup back to a simmer and add the egg noodles.",
        "Cook for 7-10 minutes, or until the noodles are tender, according to package directions.",
        "Season the soup with salt, pepper, and fresh herbs like parsley or dill before serving."
    ], 
    {"calories": 350, "protein": 25, "carbs": 30, "fat": 15}, "Easy", 40, "American", img_chicken_noodle, [], 'non-veg')

    add_recipe("Greek Salad", {"tomato": 100, "lettuce": 150, "cheese": 50, "olive oil": 10, "onion": 30}, 
    [
        "Wash and chop the lettuce, tomatoes, and cucumbers. Thinly slice the red onion.",
        "In a large salad bowl, combine the chopped lettuce, tomatoes, cucumbers, and sliced red onion.",
        "Add Kalamata olives if you have them.",
        "Crumble a block of feta cheese generously over the top of the vegetables.",
        "In a small jar or bowl, prepare the dressing. Whisk together the olive oil, lemon juice (or red wine vinegar), a pinch of dried oregano, salt, and pepper.",
        "Just before serving, pour the dressing over the salad.",
        "Toss everything gently to combine and coat the vegetables evenly. Serve immediately."
    ], 
    {"calories": 300, "protein": 8, "carbs": 10, "fat": 25}, "Easy", 10, "Mediterranean", img_greek_salad, [], 'veg')

    add_recipe("French Onion Soup", {"onion": 400, "vegetable broth": 500, "bread": 2, "cheese": 50}, 
    [
        "Thinly slice a large amount of onions.",
        "In a large pot or Dutch oven, melt a generous amount of butter over medium-low heat. Add the onions and cook slowly for 25-30 minutes, stirring occasionally, until they are deeply caramelized, sweet, and jammy.",
        "Increase the heat and deglaze the pot with a splash of white wine or just add the vegetable (or beef) broth. Scrape up any browned bits from the bottom of the pot.",
        "Bring the soup to a simmer. Season with salt, pepper, and a sprig of thyme. Let it simmer for at least 15 more minutes to let the flavors meld.",
        "Preheat your broiler. Ladle the hot soup into oven-safe bowls.",
        "Top each bowl with a slice of toasted bread (like a baguette crouton).",
        "Cover the bread with a generous amount of grated Gruyère or Swiss cheese. Place the bowls under the broiler until the cheese is melted, bubbly, and golden brown. Serve carefully."
    ], 
    {"calories": 400, "protein": 15, "carbs": 45, "fat": 18}, "Medium", 60, "European", img_french_onion, [], 'veg')

    add_recipe("Classic Pancakes", {"all-purpose flour": 150, "egg": 1, "milk": 150, "sugar": 20, "butter": 20}, 
    [
        "In a large bowl, whisk together the flour, sugar, baking powder, and salt.",
        "In a separate medium bowl, whisk together the milk and the egg. Melt the butter and whisk it into the wet ingredients.",
        "Pour the wet ingredients into the dry ingredients. Stir with a spatula until just combined. It's important not to overmix; a few lumps in the batter are perfectly fine.",
        "Let the batter rest for 5 minutes.",
        "Heat a lightly oiled griddle or non-stick frying pan over medium-high heat.",
        "Pour or scoop about 1/4 cup of batter for each pancake onto the hot griddle.",
        "Cook for 2-3 minutes, or until bubbles appear on the surface and the edges look set. Flip and cook on the other side for another 1-2 minutes until golden brown. Serve warm with your favorite toppings."
    ], 
    {"calories": 400, "protein": 10, "carbs": 60, "fat": 12}, "Easy", 20, "American", img_pancakes, [], 'veg')

    add_recipe("Scrambled Eggs", {"egg": 3, "milk": 30, "butter": 10}, 
    [
        "Crack the eggs into a bowl. Add the milk, a pinch of salt, and a few grinds of black pepper.",
        "Whisk the mixture vigorously with a fork or whisk until it's uniform in color and slightly frothy.",
        "Melt the butter in a non-stick skillet over low to medium-low heat. Do not let the butter brown.",
        "Pour the egg mixture into the skillet. Let it sit undisturbed for about 20-30 seconds until the edges just begin to set.",
        "Using a spatula, gently push the eggs from the edges of the pan toward the center, creating large, soft curds.",
        "Continue this gentle pushing motion until the eggs are mostly set but still look slightly moist and glossy.",
        "Remove the skillet from the heat immediately to prevent overcooking. The residual heat will finish the job. Serve right away."
    ], 
    {"calories": 300, "protein": 20, "carbs": 2, "fat": 24}, "Easy", 5, "Universal", img_scrambled_eggs, [], 'veg')

    add_recipe("Avocado Toast", {"bread": 2, "avocado": 1, "lemon": 1, "egg": 1}, 
    [
        "Toast your slices of bread to your desired level of crispness.",
        "While the bread is toasting, cut the avocado in half, remove the pit, and scoop the flesh into a bowl.",
        "Mash the avocado with a fork to your desired consistency - chunky or smooth.",
        "Squeeze in some fresh lemon juice to prevent browning and add brightness. Season generously with salt, pepper, and optionally, a pinch of red pepper flakes. Mix well.",
        "Spread the mashed avocado mixture evenly over the warm toast.",
        "For extra protein and flavor, top your avocado toast with a fried or poached egg.",
        "Serve immediately."
    ], 
    {"calories": 350, "protein": 12, "carbs": 30, "fat": 20}, "Easy", 5, "Universal", img_avocado_toast, [], 'veg')

    add_recipe("Stuffed Bell Peppers", {"bell pepper": 2, "ground beef": 150, "rice": 50, "tomato": 50, "onion": 30}, 
    [
        "Preheat your oven to 375°F (190°C). Cut the bell peppers in half lengthwise and remove the seeds and membranes.",
        "Place the pepper halves in a baking dish and par-boil or roast them for about 10 minutes to soften them slightly.",
        "While the peppers are pre-cooking, prepare the filling. In a skillet, brown the ground beef with chopped onion over medium heat. Drain off any excess fat.",
        "Stir in pre-cooked rice, diced tomatoes, and seasonings like oregano, garlic powder, salt, and pepper.",
        "Spoon the filling mixture evenly into each of the softened pepper halves.",
        "Top with shredded cheese if desired.",
        "Bake for 20-25 minutes, or until the filling is heated through and the peppers are tender. Serve hot."
    ], 
    {"calories": 500, "protein": 28, "carbs": 40, "fat": 25}, "Medium", 60, "Mediterranean", img_stuffed_peppers, [], 'non-veg')

    add_recipe("Simple Cabbage Salad", {"cabbage": 200, "carrot": 50, "vinegar": 10, "olive oil": 10}, 
    [
        "Thinly shred the cabbage and carrots using a sharp knife, a mandoline slicer, or a food processor. Place them in a large bowl.",
        "In a small bowl or jar, prepare the vinaigrette. Whisk together the olive oil, vinegar (like apple cider or white wine vinegar), a pinch of sugar, salt, and pepper.",
        "Pour the dressing over the shredded vegetables.",
        "Toss everything together until the cabbage and carrots are well-coated.",
        "For the best flavor, let the salad sit for at least 15 minutes before serving. This allows the cabbage to soften slightly and absorb the flavors of the dressing.",
        "Toss again just before serving."
    ], 
    {"calories": 150, "protein": 2, "carbs": 15, "fat": 10}, "Easy", 10, "Universal", img_cabbage_salad, [], 'veg')