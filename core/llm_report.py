import os
import anthropic

from datetime import date, timedelta
from core.models import User, Meal, Workout, BodyMeasurement


SYSTEM_PROMPT = """You are a strict coach and nutritionist reviewing a week of nutrition and training data.

Rules:
- Maximum 3 sentences. Be direct.
- State facts and numbers only. No encouragement, no consolation, no praise.
- Point out the largest gap between targets and actual intake.
- Note one pattern across days if there is one.
- If some days have no data, say so - never guess or fill gaps.
- Plain text only, no markdown."""

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_week_stats(user_id):
    user = User.objects.get(user_id=user_id)
    today = date.today()
    week_ago = today - timedelta(days=7)

    meals = (Meal.objects.filter(
        user=user, 
        date__gte=week_ago,
        date__lte=today,
    ).order_by("date"))

    daily = {}
    for meal in meals:
        d = meal.date
        if d not in daily:
            daily[d] = {"calories": 0, "protein": 0, "fats": 0, "carbs": 0}
        daily[d]["calories"] += meal.total_calories or 0
        daily[d]["protein"] += meal.total_protein or 0
        daily[d]["fats"] += meal.total_fats or 0
        daily[d]["carbs"] += meal.total_carbs or 0

    workouts = Workout.objects.filter(
        user=user, date__gte=week_ago, date__lte=today
    ).count()

    measurements = list(
        BodyMeasurement.objects
        .filter(user=user, date__gte=week_ago, weight__isnull=False)
        .order_by("date")
    )

    return {
        "user": user,
        "daily": daily,
        "workouts": workouts,
        "weight_start": measurements[0].weight if measurements else None,
        "weight_end": measurements[-1].weight if measurements else None,
    }


def build_prompt(stats):
    user = stats["user"]
    today = date.today()
    age = today.year - user.birth_day.year - (
        (today.month, today.day) < (user.birth_day.month, user.birth_day.day)
    )

    lines = [
        f"{user.get_gender_display()}, {age} y.o., {user.height} cm",
        f"Goal: {user.get_goal_display()}",
        f"Daily targets: {user.daily_calories_goal} kcal, "
        f"{user.daily_protein_goal}g protein, "
        f"{user.daily_fats_goal}g fats, "
        f"{user.daily_carbs_goal}g carbs",
        "",
        "Daily intake:",
    ]

    for day, totals in sorted(stats["daily"].items()):
        lines.append(
            f"{day.strftime('%a %Y-%m-%d')}: "
            f"{totals['calories']:.0f} kcal, "
            f"{totals['protein']:.0f}p, "
            f"{totals['fats']:.0f}f, "
            f"{totals['carbs']:.0f}c"
        )

    lines.append("")
    lines.append(f"Workouts: {stats['workouts']}")

    if stats["weight_start"] and stats["weight_end"]:
        lines.append(
            f"Weight: {stats['weight_start']} -> {stats['weight_end']} kg"
        )

    return "\n".join(lines)


def call_claude(prompt):
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text
    
    except Exception as e:
        print(f"Claude API error: {e}")
        return "Report is not available right now. Try again later"


def generate_report(user_id):
    stats = get_week_stats(user_id)

    if not stats["daily"]:
        return "No meals logged this week"

    prompt = build_prompt(stats)
    return call_claude(prompt)
