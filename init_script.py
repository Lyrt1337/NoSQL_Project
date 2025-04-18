import csv
import os
from pymongo import MongoClient

# Stelle sicher, dass der Pfad zu den CSV-Dateien korrekt ist
data_path = "data"  # Passe diesen Pfad an, je nachdem, wo die CSV-Dateien im Container liegen

# Überprüfe, ob der Pfad existiert
if not os.path.exists(data_path):
    print(f"Das Verzeichnis {data_path} existiert nicht!")
    exit(1)

# MongoDB-Verbindung herstellen
try:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["nosql_project"]
    print("MongoDB-Verbindung erfolgreich!")
    print(client.server_info())  # Teste die Verbindung
except Exception as e:
    print(f"Fehler beim Verbinden mit MongoDB: {e}")
    exit(1)

# Datenbank leeren
db.categories.drop()
db.recipes.drop()
db.ingredients.drop()
db.reviews.drop()

# categories
try:
    with open(os.path.join(data_path, "categories.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        categories = []
        for row in reader:
            row["_id"] = str(row["category_id"])
            del row["category_id"]
            categories.append(row)
        db.categories.insert_many(categories)
    print("✅ Kategorien wurden erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden von categories.csv: {e}")

# recipes
try:
    with open(os.path.join(data_path, "recipes.csv"), encoding="utf-8") as f:
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
    print("✅ Rezepte wurden erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden von recipes.csv: {e}")

# ingredients
try:
    with open(os.path.join(data_path, "ingredients.csv"), encoding="utf-8") as f:
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
    print("✅ Zutaten wurden erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden von ingredients.csv: {e}")

# reviews
try:
    with open(os.path.join(data_path, "reviews.csv"), encoding="utf-8") as f:
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
    print("✅ Bewertungen wurden erfolgreich geladen.")
except Exception as e:
    print(f"Fehler beim Laden von reviews.csv: {e}")

print("✅ Alle Daten wurden erfolgreich in die Datenbank geladen.")
