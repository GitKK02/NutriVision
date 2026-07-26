from __future__ import annotations

from typing import Any


METRICS = (
    ("🔥", "Калории", "calories", "calories_target", "ккал", 30),
    ("💪", "Белок", "protein_g", "protein_target", "г", 25),
    ("🥑", "Жиры", "fat_g", "fat_target", "г", 15),
    ("🍞", "Углеводы", "carbs_g", "carbs_target", "г", 15),
    ("💧", "Вода", "water_ml", "water_target", "мл", 15),
)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _ratio(value: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return value / target


def _metric_score(ratio: float, weight: int) -> float:
    if ratio <= 0:
        return 0.0

    if ratio <= 1.0:
        return weight * ratio

    if ratio <= 1.10:
        return weight * (1.0 - (ratio - 1.0) * 2.0)

    if ratio <= 1.25:
        return weight * (0.80 - (ratio - 1.10) * 2.0)

    return max(0.0, weight * (0.50 - (ratio - 1.25)))


def _status_line(
    icon: str,
    name: str,
    value: float,
    target: float,
    unit: str,
) -> str:
    if target <= 0:
        return f"⚪ {name}: цель не настроена"

    ratio = _ratio(value, target)
    difference = target - value

    if 0.90 <= ratio <= 1.10:
        return f"🟢 {name}: хороший уровень"

    if ratio < 0.60:
        return f"🔴 {name}: не хватает {round(max(0, difference))} {unit}"

    if ratio < 0.90:
        return f"🟡 {name}: осталось {round(max(0, difference))} {unit}"

    if ratio <= 1.25:
        return f"🟡 {name}: превышение на {round(abs(difference))} {unit}"

    return f"🔴 {name}: превышение на {round(abs(difference))} {unit}"


def _advice(user: dict[str, Any], summary: dict[str, Any]) -> str:
    calories = _ratio(
        _number(summary.get("calories")),
        _number(user.get("calories_target")),
    )
    protein = _ratio(
        _number(summary.get("protein_g")),
        _number(user.get("protein_target")),
    )
    fat = _ratio(
        _number(summary.get("fat_g")),
        _number(user.get("fat_target")),
    )
    carbs = _ratio(
        _number(summary.get("carbs_g")),
        _number(user.get("carbs_target")),
    )
    water = _ratio(
        _number(summary.get("water_ml")),
        _number(user.get("water_target")),
    )

    if calories > 1.10:
        return (
            "Калорийность уже выше цели. Следующий приём пищи лучше сделать "
            "лёгким: нежирный белок, овощи и вода."
        )

    if fat > 1.15:
        return (
            "Жиры заметно выше цели. Выбирай блюда без жарки, масла и жирных соусов."
        )

    if protein < 0.65 and calories >= 0.55:
        return (
            "Белка пока мало относительно калорийности. Добавь курицу, рыбу, "
            "яйца, творог или другой нежирный белковый продукт."
        )

    if water < 0.70:
        return "Не забудь о воде — до дневной цели ещё есть заметный запас."

    if carbs < 0.65 and calories < 0.90:
        return (
            "Можно добавить сложные углеводы: крупу, картофель, "
            "цельнозерновой хлеб или фрукты."
        )

    return (
        "День выглядит сбалансированно. Сохраняй обычные порции "
        "и ориентируйся на чувство голода."
    )


def calculate_daily_score(
    user: dict[str, Any] | None,
    summary: dict[str, Any],
) -> dict[str, Any] | None:
    if not user:
        return None

    active_metrics = []
    total_score = 0.0
    total_weight = 0

    for icon, name, value_key, target_key, unit, weight in METRICS:
        target = _number(user.get(target_key))
        if target <= 0:
            continue

        value = _number(summary.get(value_key))
        ratio = _ratio(value, target)
        total_score += _metric_score(ratio, weight)
        total_weight += weight
        active_metrics.append(
            {
                "icon": icon,
                "name": name,
                "value": value,
                "target": target,
                "unit": unit,
                "status": _status_line(icon, name, value, target, unit),
            }
        )

    if total_weight <= 0:
        return {
            "score": 0,
            "lines": [],
            "advice": (
                "Заполни профиль и выбери цель, чтобы NutriVision "
                "мог рассчитывать дневную оценку."
            ),
            "configured": False,
        }

    normalized = round(max(0.0, min(100.0, total_score / total_weight * 100)))

    return {
        "score": normalized,
        "lines": [item["status"] for item in active_metrics],
        "advice": _advice(user, summary),
        "configured": True,
    }


def format_daily_score(
    user: dict[str, Any] | None,
    summary: dict[str, Any],
) -> str:
    result = calculate_daily_score(user, summary)

    if not result:
        return (
            "🥗 NutriVision Score\n\n"
            "Не удалось получить данные пользователя."
        )

    if not result["configured"]:
        return (
            "🥗 NutriVision Score — 0/100\n\n"
            f"{result['advice']}"
        )

    lines = [
        f"🥗 NutriVision Score — {result['score']}/100",
        "",
        *result["lines"],
        "",
        "💡 Совет дня",
        "",
        result["advice"],
    ]
    return "\n".join(lines)
