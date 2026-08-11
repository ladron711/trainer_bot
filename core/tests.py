from datetime import date

from core.models import User
from core.meal_nutrition import daily_macros_goal, format_total


def make_user(**kwargs):
    defaults = {
        "gender": "m",
        "height": 172,
        "birth_day": date(1990, 1, 1),
        "activity": "more_three",
        "goal": "weight_loss",
    }

    defaults.update(kwargs)
    return User(**defaults)

def test_protein_depends_on_weight():
    macros = daily_macros_goal(make_user(), 85)
    assert macros["protein"] == 170

def test_muscle_gain_has_more_calories_than_weight_loss():
    loss = daily_macros_goal(make_user(goal="weight_loss"), 85)
    gain = daily_macros_goal(make_user(goal="muscle_gain"), 85)
    assert gain["calories"] > loss["calories"]

def test_female_gets_fewer_calories():
    male = daily_macros_goal(make_user(gender="m"), 85)
    female = daily_macros_goal(make_user(gender="f"), 85)
    assert female["calories"] < male["calories"]

def test_all_macros_positive():
    macros = daily_macros_goal(make_user(), 85)
    assert all(value > 0 for value in macros.values())

def test_format_total_shows_remaining():
    assert "left" in format_total(250)

def test_format_total_shows_excess():
    assert "Over goal" in format_total(-30)
