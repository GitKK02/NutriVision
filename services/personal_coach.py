from __future__ import annotations

from typing import Any

from services.weekly_report import build_weekly_report


GOAL_NAMES = {
    "gain": "набор массы",
    "maintain": "удержание веса",
    "deficit": "дефицит",
}


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _ratio(value: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return value / target


def _trend_flags(
    user: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    protein_target = _number(user.get("protein_target"))
    water_target = _number(user.get("water_target"))
    calories_target = _number(user.get("calories_target"))

    protein_low_days = 0
    water_low_days = 0
    calories_high_days = 0
    calories_low_days = 0

    calorie_values: list[float] = []

    for row in rows:
        protein = _number(row.get("protein_g"))
        water = _number(row.get("water_ml"))
        calories = _number(row.get("calories"))

        calorie_values.append(calories)

        if protein_target > 0 and protein < protein_target * 0.85:
            protein_low_days += 1
        if water_target > 0 and water < water_target * 0.85:
            water_low_days += 1
        if calories_target > 0 and calories > calories_target * 1.10:
            calories_high_days += 1
        if calories_target > 0 and calories < calories_target * 0.80:
            calories_low_days += 1

    calorie_spread = 0.0
    if len(calorie_values) >= 2:
        calorie_spread = max(calorie_values) - min(calorie_values)

    return {
        "protein_low_days": protein_low_days,
        "water_low_days": water_low_days,
        "calories_high_days": calories_high_days,
        "calories_low_days": calories_low_days,
        "calorie_spread": calorie_spread,
    }


def _next_meal_advice(
    user: dict[str, Any],
    today: dict[str, Any],
) -> str:
    calories_ratio = _ratio(
        _number(today.get("calories")),
        _number(user.get("calories_target")),
    )
    protein_ratio = _ratio(
        _number(today.get("protein_g")),
        _number(user.get("protein_target")),
    )
    fat_ratio = _ratio(
        _number(today.get("fat_g")),
        _number(user.get("fat_target")),
    )
    carbs_ratio = _ratio(
        _number(today.get("carbs_g")),
        _number(user.get("carbs_target")),
    )

    if calories_ratio > 1.05:
        return (
            "Лёгкий приём пищи: нежирный белок, овощи и вода. "
            "Избегай жарки, сладких напитков и жирных соусов."
        )

    if protein_ratio < 0.70:
        return (
            "Добавь нежирный белок: курицу, рыбу, яйца, творог "
            "или греческий йогурт."
        )

    if fat_ratio > 1.05:
        return (
            "Выбери блюдо с минимумом жира: белок + овощи, "
            "без масла и жирных соусов."
        )

    if carbs_ratio < 0.65 and calories_ratio < 0.90:
        return (
            "Подойдут сложные углеводы с белком: рис, гречка, картофель "
            "или цельнозерновой хлеб."
        )

    return (
        "Собери сбалансированный приём пищи: белок, овощи "
        "и умеренная порция углеводов."
    )


def _today_plan(
    user: dict[str, Any],
    today: dict[str, Any],
    trends: dict[str, Any],
) -> list[str]:
    plan: list[str] = []

    calories_target = _number(user.get("calories_target"))
    protein_target = _number(user.get("protein_target"))
    water_target = _number(user.get("water_target"))

    calories_left = max(0, round(calories_target - _number(today.get("calories"))))
    protein_left = max(0, round(protein_target - _number(today.get("protein_g"))))
    water_left = max(0, round(water_target - _number(today.get("water_ml"))))

    if trends["protein_low_days"] >= 3 or protein_left > protein_target * 0.30:
        plan.append(
            f"Добавить белок в ближайший приём пищи"
            + (f" — осталось около {protein_left} г" if protein_target > 0 else "")
        )

    if trends["water_low_days"] >= 3 or water_left > water_target * 0.30:
        plan.append(
            f"Распределить ещё {water_left} мл воды до конца дня"
            if water_target > 0
            else "Следить за регулярным питьевым режимом"
        )

    goal = str(user.get("goal") or "")
    if calories_target > 0:
        if goal == "deficit":
            plan.append(
                f"Удержать оставшуюся калорийность в пределах {calories_left} ккал"
            )
        elif goal == "gain":
            plan.append(
                f"Добрать около {calories_left} ккал питательной едой"
            )
        else:
            plan.append(
                f"Сохранить баланс в пределах оставшихся {calories_left} ккал"
            )

    if not plan:
        plan.append("Сохранять текущий ритм питания и обычные порции")

    return plan[:3]


def build_personal_coach_plan(
    user: dict[str, Any] | None,
    today: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not user:
        return {
            "configured": False,
            "message": "Не удалось получить профиль пользователя.",
        }

    weekly = build_weekly_report(user, rows)
    trends = _trend_flags(user, rows)

    if not rows:
        return {
            "configured": True,
            "days_logged": 0,
            "goal_name": GOAL_NAMES.get(
                str(user.get("goal") or ""),
                "цель не выбрана",
            ),
            "observations": [
                "Недостаточно истории для анализа привычек."
            ],
            "plan": _today_plan(user, today, trends),
            "next_meal": _next_meal_advice(user, today),
        }

    observations: list[str] = []

    if trends["protein_low_days"] > 0:
        observations.append(
            f"💪 Белок ниже цели в {trends['protein_low_days']} из {len(rows)} дней"
        )
    if trends["water_low_days"] > 0:
        observations.append(
            f"💧 Вода ниже цели в {trends['water_low_days']} из {len(rows)} дней"
        )
    if trends["calories_high_days"] > 0:
        observations.append(
            f"🔥 Калории выше цели в {trends['calories_high_days']} из {len(rows)} дней"
        )
    if trends["calories_low_days"] > 0:
        observations.append(
            f"📉 Калории заметно ниже цели в {trends['calories_low_days']} из {len(rows)} дней"
        )
    if trends["calorie_spread"] > _number(user.get("calories_target")) * 0.35:
        observations.append("📊 Калорийность заметно скачет между днями")

    if not observations:
        observations.append("✅ Основные показатели за неделю выглядят стабильно")

    return {
        "configured": True,
        "days_logged": len(rows),
        "goal_name": GOAL_NAMES.get(
            str(user.get("goal") or ""),
            "цель не выбрана",
        ),
        "average_score": weekly.get("average_score", 0),
        "observations": observations,
        "plan": _today_plan(user, today, trends),
        "next_meal": _next_meal_advice(user, today),
    }


def format_personal_coach_plan(
    user: dict[str, Any] | None,
    today: dict[str, Any],
    rows: list[dict[str, Any]],
) -> str:
    result = build_personal_coach_plan(user, today, rows)

    if not result.get("configured"):
        return f"🤖 Персональный план NutriVision\n\n{result.get('message')}"

    lines = [
        "🤖 Персональный план NutriVision",
        "",
        f"🎯 Твоя цель: {result['goal_name']}",
        "",
        "📊 Что я заметил",
        "",
        *result["observations"],
        "",
        "✅ План на сегодня",
        "",
    ]

    for index, item in enumerate(result["plan"], start=1):
        lines.append(f"{index}. {item}")

    lines.extend(
        [
            "",
            "🍽 Следующий приём пищи",
            "",
            result["next_meal"],
        ]
    )

    return "\n".join(lines)
