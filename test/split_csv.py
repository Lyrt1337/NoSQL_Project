"""
Dieses skript teilt das originale csv in 4 neue auf. Dabei werden fehlende Daten
wie "Kategorie", "Preis" und weitere Angaben zur Bewertung hinzugefügt.
"""
import pandas as pd
import ast

# 📌 Original-Datei einlesen
df = pd.read_csv(r"test\original_files\recipes.csv")

# 🟠 Listen für die CSV-Dateien
recipes_data = []
ingredients_data = []
reviews_data = []
categories_data = []

# 🌍 Preiszuordnung für Zutaten (geschätzt)
price_estimates = {
    "granny smith apples": 0.50,
    "unsalted butter": 1.00,
    "all-purpose flour": 0.20,
    "white sugar": 0.80,
    "brown sugar": 0.90,
    "water": 0.00,  # Wasser ist kostenlos 😉
    "pie pastry": 2.50
}

# 🟢 Eindeutige IDs für Zutaten & Kategorien
ingredient_dict = {}  # Dictionary für Zutaten mit ID
ingredient_counter = 1  # Startwert für ingredient_id

category_dict = {}  # Dictionary für Kategorien mit ID
category_counter = 1  # Startwert für category_id

# 🏷️ Kategorierichtlinien
category_rules = {
    "Vegan": ["tofu", "soymilk", "chickpeas"],
    "Low-Carb": ["almond flour", "coconut flour"],
    "Dessert": ["sugar", "chocolate", "butter"],
    "Gluten-Free": ["almond flour", "cornstarch"]
}

# 🔄 Durch die Original-Daten iterieren
for index, row in df.iterrows():
    recipe_id = index + 1  # Rezept-ID festlegen
    
    # 🎯 Rezept speichern
    recipes_data.append({
        "recipe_id": recipe_id,
        "name": row["recipe_name"],
        "prep_time": row["prep_time"],
        "cook_time": row["cook_time"],
        "total_time": row["total_time"],
        "servings": row["servings"],
        "yield": row["yield"],
        "directions": row["directions"].replace("\n", "; "),  # Anweisungen als Liste speichern
        "rating": row["rating"],
        "url": row["url"],
        "cuisine_path": row["cuisine_path"],
        "image_url": row["img_src"]
    })

    # 🥕 Zutaten aufsplitten
    try:
        raw_ingredients = ast.literal_eval(row["ingredients"]) if isinstance(row["ingredients"], str) else row["ingredients"].split(", ")
    except:
        raw_ingredients = row["ingredients"].split(", ")
    
    ingredient_list = []
    for ingredient in raw_ingredients:
        ingredient_name = ingredient.strip().lower()

        # Prüfen, ob die Zutat bereits existiert, sonst neue ID vergeben
        if ingredient_name not in ingredient_dict:
            ingredient_dict[ingredient_name] = ingredient_counter
            ingredient_counter += 1  # ID hochzählen
        
        ingredient_id = ingredient_dict[ingredient_name]
        price = price_estimates.get(ingredient_name, 1.00)  # Falls unbekannt, Standardpreis
        ingredient_list.append(ingredient_name)

        ingredients_data.append({
            "ingredient_id": ingredient_id,
            "recipe_id": recipe_id,
            "name": ingredient_name,
            "price": price
        })

    # 🏷️ Kategorie zuweisen
    assigned_categories = [
        cat for cat, keywords in category_rules.items() if any(kw in " ".join(ingredient_list) for kw in keywords)
    ]
    if not assigned_categories:
        assigned_categories = ["Uncategorized"]

    # Kategorie-ID zuweisen
    category_ids = []
    for category in assigned_categories:
        if category not in category_dict:
            category_dict[category] = category_counter
            category_counter += 1
        
        category_ids.append(category_dict[category])

    # Speichere die erste Kategorie-ID (für 1:1-Zuordnung)
    recipes_data[-1]["category_id"] = category_ids[0]

    # ⭐ Bewertung speichern (mit eindeutiger review_id)
    review_id = len(reviews_data) + 1  # Fortlaufende Nummerierung für Reviews
    reviews_data.append({
        "review_id": review_id,
        "recipe_id": recipe_id,
        "user": "Anonymous",
        "rating": row["rating"],
        "comment": "No review available.",
        "date": "2025-01-01"
    })

# 📜 Kategorien speichern
for category, category_id in category_dict.items():
    categories_data.append({
        "category_id": category_id,
        "category_name": category
    })

# 📝 In CSV-Dateien speichern
pd.DataFrame(recipes_data).to_csv(r"test\files\recipes.csv", index=False)
pd.DataFrame(ingredients_data).to_csv(r"test\files\ingredients.csv", index=False)
pd.DataFrame(reviews_data).to_csv(r"test\files\reviews.csv", index=False)
pd.DataFrame(categories_data).to_csv(r"test\files\categories.csv", index=False)

print("✅ CSV-Dateien erfolgreich erstellt!")
