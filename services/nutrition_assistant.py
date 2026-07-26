from __future__ import annotations

from typing import Any


NUTRIENTS = (
    ("🔥", "Калории", "calories", "calories_target", "ккал"),
    ("💪", "Белок", "protein_g", "protein_target", "г"),
    ("🥑", "Жиры", "fat_g", "fat_target", "г"),
    ("🍞", "Углеводы", "carbs_g", "carbs_target", "г"),
)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _round_value(value: float) -> int:
    return int(round(value))


def _remaining_line(value: float, target: float, unit: str) -> str:
    difference = target - value

    if difference > 0:
        return f"осталось {_round_value(difference)} {unit}"
    if difference < 0:
        return f"превышено на {_round_value(abs(difference))} {unit}"
    return "цель выполнена точно"


def _ratio(
    summary: dict[str, Any],
    user: dict[str, Any],
    key: str,
    target_key: str,
) -> float:
    target = _number(user.get(target_key))
    if target <= 0:
        return 0.0
    return _number(summary.get(key)) / target


def _build_advice(user: dict[str, Any], summary: dict[str, Any]) -> str:
    calories_ratio = _ratio(summary, user, "calories", "calories_target")
    protein_ratio = _ratio(summary, user, "protein_g", "protein_target")
    fat_ratio = _ratio(summary, user, "fat_g", "fat_target")
    carbs_ratio = _ratio(summary, user, "carbs_g", "carbs_target")

    if calories_ratio > 1.10:
        return (
            "Калорийность уже заметно выше цели. Следующий приём пищи лучше "
            "сделать максимально лёгким: нежирный белок, овощи и вода."
        )

    if fat_ratio > 1.10:
        return (
            "Жиры уже выше цели. Дальше лучше выбрать нежирный белок и блюдо "
            "без жарки, масла и жирных соусов."
        )

    if carbs_ratio > 1.15:
        return (
            "Углеводы уже выше цели. Следующий приём пищи лучше составить "
            "из белка и овощей без сладких напитков и выпечки."
        )

    if protein_ratio < 0.55 and calories_ratio >= 0.45:
        return (
            "Белка пока маловато относительно общей калорийности. Подойдут "
            "курица, рыба, яйца, творог или другой нежирный источник белка."
        )

    if protein_ratio < 0.75 and calories_ratio >= 0.70:
        return (
            "До цели по белку осталось больше, чем по калориям. Следующий "
            "приём пищи лучше сделать преимущественно белковым."
        )

    if carbs_ratio < 0.45 and calories_ratio >= 0.45:
        return (
            "Можно добавить сложные углеводы: крупу, картофель, цельнозерновой "
            "хлеб или фрукты — с учётом оставшихся калорий."
        )

    if calories_ratio >= 0.90 and protein_ratio >= 0.90:
        return (
            "Ты уже близко к дневным целям. Дальше выбирай небольшую порцию "
            "и ориентируйся на чувство голода."
        )

    if 0.75 <= protein_ratio <= 1.10 and 0.75 <= fat_ratio <= 1.10:
        return (
            "Баланс выглядит хорошо. Продолжай придерживаться обычных порций "
            "и не забывай о воде."
        )

    return (
        "Рацион пока укладывается в дневной план. Следующий приём пищи лучше "
        "собрать из белка, овощей и подходящего источника углеводов."
    )


def nutrition_assistant_message(
    user: dict[str, Any] | None,
    summary: dict[str, Any],
) -> str | None:
    """Возвращает персональный отчёт после добавления блюда."""
    if not user:
        return None

    available_targets = [
        _number(user.get(target_key))
        for _, _, _, target_key, _ in NUTRIENTS
    ]

    if not any(target > 0 for target in available_targets):
        return (
            "🤖 Совет NutriVision\n\n"
            "Заполни профиль и выбери цель — тогда после каждого блюда "
            "я буду показывать, сколько осталось до дневной нормы."
        )

    lines = ["🎯 До цели сегодня", ""]

    for icon, name, summary_key, target_key, unit in NUTRIENTS:
        target = _number(user.get(target_key))
        if target <= 0:
            continue

        value = _number(summary.get(summary_key))
        lines.append(f"{icon} {name}: {_remaining_line(value, target, unit)}")

    advice = _build_advice(user, summary)

    return "\n".join(lines) + f"\n\n🤖 Совет NutriVision\n\n{advice}"
