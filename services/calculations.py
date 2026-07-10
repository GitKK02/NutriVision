def calculate_targets(age: int, gender: str, height_cm: float, weight_kg: float, activity: str, goal: str):
    sex_const = 5 if gender == "male" else -161
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + sex_const
    factors = {"low": 1.2, "medium": 1.55, "high": 1.725}
    tdee = bmr * factors.get(activity, 1.55)

    if goal == "gain":
        calories = tdee + 300
    elif goal == "deficit":
        calories = tdee - 400
    else:
        calories = tdee

    calories = max(1200, round(calories))
    protein = round(weight_kg * (2.0 if goal == "deficit" else 1.8))
    fat = round(weight_kg * 0.9)
    carbs = round(max(0, (calories - protein * 4 - fat * 9) / 4))
    water = round(weight_kg * 35)

    return {
        "calories_target": calories,
        "protein_target": protein,
        "fat_target": fat,
        "carbs_target": carbs,
        "water_target": water,
    }
