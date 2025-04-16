"""
Dieses skript teilt das originale csv in 4 neue auf. Dabei werden fehlende Daten
wie "Kategorie", "Preis" und weitere Angaben zur Bewertung hinzugefügt.
"""
import pandas as pd
import ast
import re

# read original data
df = pd.read_csv(r"data\original_files\recipes.csv")

# prepare lists for csv split
recipes_data = []
ingredients_data = []
reviews_data = []
categories_data = []

# prepare ID's for ingredients and categories
ingredient_dict = {}
ingredient_counter = 1

category_dict = {}
category_counter = 1

# create categories
category_rules = {
    "Vegan": ["tofu", "soymilk", "chickpeas"],
    "Low-Carb": ["almond flour", "coconut flour"],
    "Dessert": ["sugar", "chocolate", "butter"],
    "Gluten-Free": ["almond flour", "cornstarch"]
}

for index, row in df.iterrows():
    recipe_id = index + 1
    
    # save recipe
    recipes_data.append({
        "recipe_id": recipe_id,
        "name": row["recipe_name"],
        "prep_time": row["prep_time"],
        "cook_time": row["cook_time"],
        "total_time": row["total_time"],
        "servings": row["servings"],
        "yield": row["yield"],
        "directions": re.sub(r'(;\s*){2,}', '; ', row["directions"].replace("\n", "; ")),  # Anweisungen als Liste speichern
        "image_url": row["img_src"]
    })

    # split ingredients
    try:
        raw_ingredients = ast.literal_eval(row["ingredients"]) if isinstance(row["ingredients"], str) else row["ingredients"].split(", ")
    except:
        raw_ingredients = row["ingredients"].split(", ")
    
    ingredient_list = []
    for ingredient in raw_ingredients:
        ingredient_name = ingredient.strip().lower()

        # check for existing ingredients, create new ID if not
        if ingredient_name not in ingredient_dict:
            ingredient_dict[ingredient_name] = ingredient_counter
            ingredient_counter += 1
        
        ingredient_id = ingredient_dict[ingredient_name]
        ingredient_list.append(ingredient_name)

        ingredients_data.append({
            "ingredient_id": ingredient_id,
            "recipe_id": recipe_id,
            "name": ingredient_name,
        })

    # assign category
    assigned_categories = [
        cat for cat, keywords in category_rules.items() if any(kw in " ".join(ingredient_list) for kw in keywords)
    ]
    if not assigned_categories:
        assigned_categories = ["Uncategorized"]

    # assign category-ID
    category_ids = []
    for category in assigned_categories:
        if category not in category_dict:
            category_dict[category] = category_counter
            category_counter += 1
        
        category_ids.append(category_dict[category])

    recipes_data[-1]["category_id"] = category_ids[0]

    # save reviews and ratings
    review_id = len(reviews_data) + 1
    reviews_data.append({
        "review_id": review_id,
        "recipe_id": recipe_id,
        "user": "Anonymous",
        "rating": row["rating"],
        "comment": "No review available.",
        "date": "2025-01-01"
    })

# save category
for category, category_id in category_dict.items():
    categories_data.append({
        "category_id": category_id,
        "category_name": category
    })

# export to csv
pd.DataFrame(recipes_data).to_csv(r"data\recipes.csv", index=False)
pd.DataFrame(ingredients_data).to_csv(r"data\ingredients.csv", index=False)
pd.DataFrame(reviews_data).to_csv(r"data\reviews.csv", index=False)
pd.DataFrame(categories_data).to_csv(r"data\categories.csv", index=False)

print("✅ CSV-Dateien erfolgreich erstellt!")
