import openai

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, calculate_bmi, weight_class, calculate_bmr

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///database.db")

openai.api_key = 'your_actual_api_key'

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if not rows[0]["height"]:
        return redirect("/new")

    height = rows[0]["height"]
    weight = rows[0]["weight"]
    age = rows[0]["age"]
    gender = rows[0]["gender"]

    bmi = calculate_bmi(height / 100, weight)
    bmr = calculate_bmr(age, gender, height, weight)
    weightclass = weight_class(bmi)

    if request.method == "POST":
        activity = request.form.get("activity")
        if not activity:
            flash("Please select activity.", "danger")
            return redirect("/")

        calories = float(bmr) * float(activity)
        flash(f"You need {round(calories)} calories daily.", "primary")
        return redirect("/")

    return render_template("index.html", bmr=bmr, bmi=bmi, weightclass=weightclass)


@app.route("/meal", methods=["GET","POST"])
@login_required
def meal():
    if request.method == "POST":
        goal = request.form.get("goal")
        meal_time = request.form.get("meal_time")
        preferences = request.form.get("preferences", "no")
        allergies = request.form.get("allergies", "no")
        include_foods = request.form.get("include_foods", "any")
        exclude_foods = request.form.get("exclude_foods", "none")

        if not goal or not meal_time:
            flash("Select at least a goal and meal time.", "danger")
            return redirect("/meal")

        prompt = f"Generate a {goal} meal for {meal_time} with {preferences} preferences, {allergies} allergies. Include foods: {include_foods}, Exclude foods: {exclude_foods}. Provide an easy-to-follow intructions and nutritional information in the following format:\n\nMeal name \n\nInstructions:\n[Preparing instructions, maximum 7 lines]\n\nNutritional Information:\n[Nutritional facts, limit to only calories, protein, carbohydrates and fats, all in one line]. Do not add any information after the nutrition facts."


        response = openai.Completion.create(engine="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=200)

        meal_description = response.choices[0].text.strip()

        session["meal_time"] = meal_time
        session["goal"] = goal
        session["meal_description"] = meal_description

        return render_template("result.html", meal_description=meal_description)

    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not rows[0]["height"]:
            flash("You need to provide us with information to generate a meal.", "danger")
            return redirect("/new")

        return render_template("meal.html")


@app.route("/result", methods=["GET","POST"])
@login_required
def result():
    if request.method == "POST":
        if request.form.get("button") == "generate":
            return redirect("/meal")

        elif request.form.get("button") == "save":
            meal_time = session["meal_time"]
            goal = session["goal"]
            meal_description = session["meal_description"]

            db.execute("INSERT INTO meals (user_id, mealtime, goal, meal_description) VALUES (?, ?, ?, ?)", session["user_id"], meal_time, goal, meal_description)

            session.pop("meal_time", None)
            session.pop("goal", None)
            session.pop("meal_description", None)

            flash("Saved", "success")
            return redirect("/saved")
        else:
            flash("Error", "danger")
            return redirect("/")
    else:
        return redirect("/")


@app.route("/saved", methods=["GET", "POST"])
@login_required
def saved():
    meals = db.execute("SELECT * FROM meals WHERE user_id = ?", session["user_id"])
    if request.method == "POST":

        meal_id = request.form.get("meal_id")
        db.execute("DELETE FROM meals WHERE id = ?", meal_id)
        flash("Removed Successfuly", "success")
        return redirect("/saved")

    return render_template("saved.html", meals=meals)


@app.route("/account", methods=["GET", "POST"])
def account():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    username = rows[0]["username"]
    age = rows[0]["age"]
    height = rows[0]["height"]
    weight = rows[0]["weight"]

    if request.method == "POST":
        if request.form.get("old_password"):
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")
            verify_password = request.form.get("verify_password")

            if new_password != verify_password:
                flash("Passwords do not match.", "danger")
                return redirect("/account")

            if not check_password_hash(rows[0]["hash"], old_password):
                flash("Incorrect old password", "danger")
                return redirect("/account")

            else:
                hash_password = generate_password_hash(new_password)
                db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_password, session["user_id"])
                flash("Password changed.", "success")
                return redirect("/")
        else:
            new_age = request.form.get("age")
            new_height = request.form.get("height")
            new_weight = request.form.get("weight")

            if not new_age and not new_height and not new_weight:
                flash("Nothing changed.", "info")
                return redirect("/")

            if new_age == "":
                new_age = age

            if new_height == "":
                new_height = height

            if new_weight == "":
                new_weight = weight

            db.execute("UPDATE users SET age = ?, height = ?, weight = ? WHERE id = ?", int(new_age), int(new_height), int(new_weight), session["user_id"])

            flash("Information updated.", "success")
            return redirect("/")

    else:
        return render_template("account.html", username=username, age=age, height=height, weight=weight, rows=rows[0])

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    username = rows[0]["username"]

    if request.method == "POST":
        height = int(request.form.get("height"))
        weight = int(request.form.get("weight"))
        age = int(request.form.get("age"))
        gender = request.form.get("gender")

        if not height or not weight or not age or not gender:
            flash("Please fill all the required blanks.", "danger")
            return render_template("new.html")

        db.execute("UPDATE users SET height = ?, weight = ?, age = ?, gender = ? WHERE id = ?", height, weight, age, gender, session["user_id"])

        return redirect("/")

    return render_template("new.html", username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Must provide username and password", "danger")
            return render_template("login.html")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password", "danger")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("Passwords does not match.", "danger")
            return render_template("register.html")

        username_exists = db.execute("SELECT * FROM users WHERE username = ?", username)

        if username_exists:
            flash("This username already exist.", "danger")
            return render_template("register.html")
        else:
            hash_password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash_password)
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)

            session["user_id"] = rows[0]["id"]

            flash("Registration successful.", "success")
            return redirect("/")

    else:
        return render_template("register.html")
