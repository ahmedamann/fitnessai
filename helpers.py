from flask import redirect, session
from functools import wraps

def calculate_bmi(height, weight):
    return round((weight / height ** 2), 2)

def weight_class(bmi):
    if bmi <= 18.5:
        x = "Underweight"
    elif 18.5 < bmi <= 24.9:
        x = "Normal"
    elif 25 < bmi <= 29.29:
        x = "Overweight"
    else:
        x = "Obese"
    return x

def calculate_bmr(age, gender, height, weight):
    if gender == "male":
        return (10 * weight + 6.25 * height - 5 * age + 5)
    else:
        return (10 * weight + 6.25 * height - 5 * age - 161)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
