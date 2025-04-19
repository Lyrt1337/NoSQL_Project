import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# MongoDB-connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client["nosql_project"]


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    selected = request.args.get("category", "").strip()
    recipe_name = request.args.get("recipe_name", "").strip()

    recipe_filter = {}

    # search category, ingredients, recipe name
    if selected:
        recipe_filter["category_id"] = selected

    if query:

        ingredient_matches = db.ingredients.find({"name": {"$regex": query, "$options": "i"}})
        recipe_ids = list({ing["recipe_id"] for ing in ingredient_matches})

        if recipe_ids:
            recipe_filter["_id"] = {"$in": recipe_ids}
        else:
            recipe_filter["_id"] = "__never_match__"


    if recipe_name:
        recipe_filter["name"] = {"$regex": recipe_name, "$options": "i"}


    recipes = list(db.recipes.find(recipe_filter))


    # add category for each recipe
    for recipe in recipes:
        # Kategorie hinzufügen
        if recipe.get("category_id"):
            category = db.categories.find_one({"_id": recipe["category_id"]})
            recipe["categories"] = category["category_name"] if category else ""
        else:
            recipe["categories"] = ""
        
        # get reviews for rating
        reviews = list(db.reviews.find({"recipe_id": recipe["_id"]}))
        
        # calc avg. rating
        if reviews:
            avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
            recipe["avg_rating"] = avg_rating
        else:
            recipe["avg_rating"] = None

    # all categories for dropdown
    categories = list(db.categories.find())

    return render_template(
        "index.html",
        recipes=recipes,
        query=query,
        categories=categories,
        selected=selected
    )


@app.route("/add", methods=["GET", "POST"])
def add_recipe():
    # load all categories for dropdown
    categories = list(db.categories.find())
    if request.method == "POST":
        # find id of last recipe to generate new id for new item
        last_recipe = db.recipes.find().sort("_id", -1).limit(1)
        try:
            last_id = int(next(last_recipe)["_id"])
        except (StopIteration, ValueError):
            new_id = "1"

        while db.recipes.find_one({"_id": str(last_id + 1)}):
            last_id += 1
        new_id = str(last_id + 1)

        # collect recipe data
        recipe = {
            "_id": new_id,
            "name": request.form.get("name"),
            "prep_time": request.form.get("prep_time") or "",
            "cook_time": request.form.get("cook_time") or "",
            "total_time": request.form.get("total_time") or "",
            "servings": request.form.get("servings") or "",
            "directions": request.form.get("directions") or "",
            "category_id": request.form.get("category_id") or "",
            "image_url": request.form.get("image_url") or "",
        }

        # save new recipe
        db.recipes.insert_one(recipe)

        # save ingredients of new recipe
        ingredients_text = request.form.get("ingredients", "")
        ingredients_list = [line.strip() for line in ingredients_text.split("\n") if line.strip()]
        for ing in ingredients_list:
            db.ingredients.insert_one({
                "recipe_id": new_id,
                "name": ing
            })

        return redirect("/")

    return render_template("add.html", categories=categories)



@app.route("/view/<id>")
def view_recipe(id):
    recipe = db.recipes.find_one({"_id": id})
    if not recipe:
        return "Rezept nicht gefunden", 404
    
    recipe['prep_time'] = str(recipe.get('prep_time', 'Nicht angegeben'))
    recipe['cook_time'] = str(recipe.get('cook_time', 'Nicht angegeben'))
    recipe['total_time'] = str(recipe.get('total_time', 'Nicht angegeben'))


    category = db.categories.find_one({"_id": recipe["category_id"]})
    recipe["categories"] = category["category_name"] if category else ""
    
    ingredients = db.ingredients.find({"recipe_id": id})
    recipe['ingredients'] = [ingredient['name'] for ingredient in ingredients]

    reviews = list(db.reviews.find({"recipe_id": id}))
    if reviews:
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
    else:
        avg_rating = None

    return render_template("view.html", recipe=recipe, reviews=reviews, avg_rating=avg_rating)


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_recipe(id):
    recipe = db.recipes.find_one({"_id": id})
    if not recipe:
        return "Rezept nicht gefunden", 404

    if request.method == "POST":
        # recipe changes for update
        updated_data = {
            "name": request.form["name"],
            "prep_time": request.form.get("prep_time", ""),
            "cook_time": request.form.get("cook_time", ""),
            "total_time": request.form.get("total_time", ""),
            "servings": request.form.get("servings", ""),
            "directions": request.form.get("directions", ""),
            "category_id": request.form.get("category_id", ""),
        }
        db.recipes.update_one({"_id": id}, {"$set": updated_data})

        # update
        new_ingredients = [i.strip() for i in request.form.get("ingredients", "").splitlines() if i.strip()]
        existing_ingredients = list(db.ingredients.find({"recipe_id": id}))
        existing_names = [ing["name"] for ing in existing_ingredients]

        for name in new_ingredients:
            if name not in existing_names:
                db.ingredients.insert_one({"recipe_id": id, "name": name})

        for ing in existing_ingredients:
            if ing["name"] not in new_ingredients:
                db.ingredients.delete_one({"_id": ing["_id"]})

        # update or delete reviews
        reviews = db.reviews.find({"recipe_id": id})
        for review in reviews:
            delete_field = f"delete_review_{review['_id']}"
            if delete_field in request.form:
                db.reviews.delete_one({"_id": review["_id"]})
                continue

            comment_field = f"comment_{review['_id']}"
            rating_field = f"rating_{review['_id']}"
            if comment_field in request.form and rating_field in request.form:
                updated_review = {
                    "comment": request.form[comment_field],
                    "rating": float(request.form[rating_field]) if request.form[rating_field] else None
                }
                db.reviews.update_one({"_id": review["_id"]}, {"$set": updated_review})


        return redirect(url_for("view_recipe", id=id))

    # GET: prepare current data
    ingredients_cursor = db.ingredients.find({"recipe_id": id})
    ingredients = "\n".join(i["name"] for i in ingredients_cursor)
    directions = recipe.get("directions", "")

    categories = list(db.categories.find())
    reviews = list(db.reviews.find({"recipe_id": id}))

    return render_template(
        "edit.html",
        recipe=recipe,
        ingredients=ingredients,
        directions=directions,
        categories=categories,
        reviews=reviews
    )



@app.route("/delete/<id>", methods=["GET", "POST"])
def delete_recipe(id):
    recipe = db.recipes.find_one({"_id": id})
    if not recipe:
        return "Rezept nicht gefunden", 404

    if request.method == "POST":
        db.recipes.delete_one({"_id": id})

        db.ingredients.delete_many({"recipe_id": id})

        db.reviews.delete_many({"recipe_id": id})

        return redirect("/")

    return render_template("delete.html", recipe=recipe)


@app.route("/review/<id>", methods=["GET", "POST"])
def write_review(id):
    recipe = db.recipes.find_one({"_id": id})
    if not recipe:
        return "Rezept nicht gefunden", 404

    if request.method == "POST":
        user = request.form.get("user", "Anonymous").strip()
        rating = float(request.form.get("rating", 0))
        comment = request.form.get("comment", "").strip()

        # generate review_id
        last_review = db.reviews.find().sort("review_id", -1).limit(1)
        try:
            last_id = int(next(last_review)["review_id"])
        except (StopIteration, ValueError):
            last_id = 0
        new_review_id = str(last_id + 1)

        review = {
            "review_id": new_review_id,
            "recipe_id": id,
            "user": user,
            "rating": rating,
            "comment": comment,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        db.reviews.insert_one(review)
        return redirect(url_for("view_recipe", id=id))

    return render_template("review.html", recipe=recipe)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

