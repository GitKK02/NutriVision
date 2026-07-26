from __future__ import annotations

from datetime import date, datetime
from typing import Any

from services.daily_score import calculate_daily_score


WEEKDAY_NAMES = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _day_name(raw_day: str) -> str:
    try:
        parsed = date.fromisoformat(raw_day)
    except (TypeError, ValueError):
        return str(raw_day or "Неизвестный день")
    return WEEKDAY_NAMES.get(parsed.weekday(), parsed.strftime("%d.%m"))


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def build_weekly_report(
    user: dict[str, Any] | None,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not user:
        return {
            "configured": False,
            "days_logged": 0,
            "message": "Не удалось получить профиль пользователя.",
        }

    if not rows:
        return {
            "configured": True,
            "days_logged": 0,
            "message": (
                "За последние 7 дней пока нет записей питания. "
                "Добавь блюда хотя бы за несколько дней, чтобы появился отчёт."
            ),
        }

    scored_days = []
    calorie_values = []
    protein_values = []
    fat_values = []
    carbs_values = []
    water_values = []

    protein_target = _number(user.get("protein_target"))
    water_target = _number(user.get("water_target"))

    protein_goal_days = 0
    water_goal_days = 0

    for row in rows:
        summary = {
            "calories": _number(row.get("calories")),
            "protein_g": _number(row.get("protein_g")),
            "fat_g": _number(row.get("fat_g")),
            "carbs_g": _number(row.get("carbs_g")),
            "water_ml": _number(row.get("water_ml")),
            "food_count": int(row.get("food_count") or 0),
        }

        score_result = calculate_daily_score(user, summary)
        score = 0
        if score_result and score_result.get("configured"):
            score = int(score_result.get("score") or 0)

        scored_days.append(
            {
                "day": str(row.get("day") or ""),
                "day_name": _day_name(str(row.get("day") or "")),
                "score": score,
            }
        )

        calorie_values.append(summary["calories"])
        protein_values.append(summary["protein_g"])
        fat_values.append(summary["fat_g"])
        carbs_values.append(summary["carbs_g"])
        water_values.append(summary["water_ml"])

        if protein_target > 0 and summary["protein_g"] >= protein_target * 0.9:
            protein_goal_days += 1
        if water_target > 0 and summary["water_ml"] >= water_target * 0.9:
            water_goal_days += 1

    best_day = max(scored_days, key=lambda item: item["score"])
    weakest_day = min(scored_days, key=lambda item: item["score"])

    average_score = round(_average([item["score"] for item in scored_days]))
    average_calories = round(_average(calorie_values))
    average_protein = round(_average(protein_values))
    average_fat = round(_average(fat_values))
    average_carbs = round(_average(carbs_values))
    average_water = round(_average(water_values))

    calories_target = _number(user.get("calories_target"))
    calorie_delta_percent = 0
    if calories_target > 0:
        calorie_delta_percent = round(
            (average_calories - calories_target) / calories_target * 100
        )

    if average_score >= 85:
        conclusion = (
            "Неделя получилась стабильной. Продолжай удерживать текущий ритм "
            "и следи за регулярностью воды."
        )
    elif average_score >= 70:
        conclusion = (
            "Неделя в целом хорошая. Главная задача — уменьшить разброс между "
            "лучшими и слабыми днями."
        )
    elif protein_goal_days < max(1, len(rows) // 2):
        conclusion = (
            "Главная зона роста — белок. Постарайся добавлять белковый продукт "
            "в первую половину дня."
        )
    elif water_goal_days < max(1, len(rows) // 2):
        conclusion = (
            "Главная зона роста — вода. Поможет привычка выпивать стакан воды "
            "после пробуждения и перед каждым приёмом пищи."
        )
    else:
        conclusion = (
            "Питание пока нестабильно. Сфокусируйся на регулярных приёмах пищи "
            "и более точных порциях."
        )

    return {
        "configured": True,
        "days_logged": len(rows),
        "average_score": average_score,
        "best_day": best_day,
        "weakest_day": weakest_day,
        "average_calories": average_calories,
        "average_protein": average_protein,
        "average_fat": average_fat,
        "average_carbs": average_carbs,
        "average_water": average_water,
        "calorie_delta_percent": calorie_delta_percent,
        "protein_goal_days": protein_goal_days,
        "water_goal_days": water_goal_days,
        "conclusion": conclusion,
    }


def format_weekly_report(
    user: dict[str, Any] | None,
    rows: list[dict[str, Any]],
) -> str:
    report = build_weekly_report(user, rows)

    if not report.get("configured"):
        return f"📅 Отчёт за неделю\n\n{report.get('message')}"

    if report.get("days_logged", 0) == 0:
        return f"📅 Отчёт за неделю\n\n{report.get('message')}"

    calorie_delta = int(report["calorie_delta_percent"])
    if calorie_delta > 0:
        calorie_text = f"в среднем +{calorie_delta}% к цели"
    elif calorie_delta < 0:
        calorie_text = f"в среднем {calorie_delta}% от цели"
    else:
        calorie_text = "в среднем точно по цели"

    days = int(report["days_logged"])

    return (
        "📅 Отчёт за неделю\n\n"
        f"🥗 Средний NutriVision Score: {report['average_score']}/100\n\n"
        f"📈 Лучший день: {report['best_day']['day_name']} — "
        f"{report['best_day']['score']}/100\n"
        f"📉 Самый слабый день: {report['weakest_day']['day_name']} — "
        f"{report['weakest_day']['score']}/100\n\n"
        f"🔥 Калории: {calorie_text}\n"
        f"💪 Белок: цель выполнена в {report['protein_goal_days']} из {days} дней\n"
        f"💧 Вода: цель выполнена в {report['water_goal_days']} из {days} дней\n\n"
        "📊 Средние значения\n"
        f"🔥 {report['average_calories']} ккал\n"
        f"💪 {report['average_protein']} г белка\n"
        f"🥑 {report['average_fat']} г жиров\n"
        f"🍞 {report['average_carbs']} г углеводов\n"
        f"💧 {report['average_water']} мл воды\n\n"
        "🤖 Вывод NutriVision\n\n"
        f"{report['conclusion']}"
    )
