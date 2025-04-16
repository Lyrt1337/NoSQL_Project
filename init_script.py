import csv
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["nosql_project"]

# drop entire existing database to avoid conflict
db.categories.drop()
db.recipes.drop()
db.ingredients.drop()
db.reviews.drop()

# categories
with open("data/categories.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    categories = []
    for row in reader:
        row["_id"] = str(row["category_id"])
        del row["category_id"]
        categories.append(row)
    db.categories.insert_many(categories)

# recipes
with open("data/recipes.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    recipes = []
    for row in reader:
        row["_id"] = str(row["recipe_id"])
        del row["recipe_id"]

        row["category_id"] = str(row["category_id"]) if row["category_id"] else None

        for key in ["prep_time", "cook_time", "total_time", "servings", "rating"]:
            if row.get(key):
                try:
                    row[key] = float(row[key]) if '.' in row[key] else int(row[key])
                except ValueError:
                    row[key] = str(row[key])

        recipes.append(row)
    db.recipes.insert_many(recipes)

# ingredients
with open("data/ingredients.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    ingredients = []
    for row in reader:
        row["recipe_id"] = str(row["recipe_id"])
        if "price" in row and row["price"]:
            try:
                row["price"] = float(row["price"])
            except ValueError:
                row["price"] = None
        ingredients.append(row)
    db.ingredients.insert_many(ingredients)

# reviews
with open("data/reviews.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    reviews = []
    for row in reader:
        row["recipe_id"] = str(row["recipe_id"])
        if "rating" in row and row["rating"]:
            try:
                row["rating"] = float(row["rating"])
            except ValueError:
                row["rating"] = None
        reviews.append(row)
    db.reviews.insert_many(reviews)

print("✅ Alle Daten wurden erfolgreich in die Datenbank geladen.")
