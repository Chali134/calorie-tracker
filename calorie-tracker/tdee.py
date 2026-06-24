"""
TDEE & macro target calculation using Mifflin-St Jeor equation.
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_ADJUSTMENTS = {
    "lose": 0.8,
    "maintain": 1.0,
    "gain": 1.15,
}

MACRO_SPLIT = {
    "protein": 0.30,
    "carbs": 0.40,
    "fat": 0.30,
}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier)


def adjust_for_goal(tdee: int, goal_type: str) -> int:
    adjustment = GOAL_ADJUSTMENTS.get(goal_type, 1.0)
    return round(tdee * adjustment)


def calculate_macros(calories: int) -> dict:
    protein_g = round(calories * MACRO_SPLIT["protein"] / 4)
    carbs_g = round(calories * MACRO_SPLIT["carbs"] / 4)
    fat_g = round(calories * MACRO_SPLIT["fat"] / 9)
    return {
        "protein": protein_g,
        "carbs": carbs_g,
        "fat": fat_g,
    }


def calculate_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal_type: str,
) -> dict:
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    adjusted_calories = adjust_for_goal(tdee, goal_type)
    macros = calculate_macros(adjusted_calories)
    return {
        "tdee": tdee,
        "calorie_target": adjusted_calories,
        "protein_target": macros["protein"],
        "carbs_target": macros["carbs"],
        "fat_target": macros["fat"],
    }
