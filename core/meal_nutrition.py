from datetime import date
from django.db.models import Sum


def daily_macros_goal(user, weight):

    today = date.today()
    age = today.year - user.birth_day.year - ((today.month, today.day) < (user.birth_day.month, user.birth_day.day))

    if user.gender == "m":
        bmr = 10*weight + 6.25*user.height - 5*age + 5

    else:
        bmr = 10*weight + 6.25*user.height - 5*age - 161

    if user.activity == "under_three":
        tdee = bmr*1.375
    elif user.activity == "three":
        tdee = bmr*1.55
    else:
        tdee = bmr*1.725

    if user.goal == "weight_loss":
        user_calories = tdee*0.85
        user_protein = weight*2
        user_fats = weight*0.8

    elif user.goal == "muscle_gain":
        user_calories = tdee*1.1
        user_protein = weight*1.8
        user_fats = weight*1
    else:
        user_calories = tdee*1.0
        user_protein = weight*1.6
        user_fats = weight*0.9

    user_carbs = (user_calories - user_protein*4 - user_fats*9)/4

    return {
        "calories": round(user_calories, 1),
        "protein": round(user_protein, 1),
        "carbs": round(user_carbs, 1),
        "fats": round(user_fats, 1), 
    }


def daily_total(user, field):
    eaten = user.meal_set.filter(date=date.today()).aggregate(total=Sum(f"total_{field}"))["total"] or 0
    goal = getattr(user, f"daily_{field}_goal")

    return round(goal - eaten, 1)


def format_total(value, unit="g"):
    if value >= 0:
        return f"{value}{unit} left"
    return f"Over goal: {abs(value)}{unit}"
