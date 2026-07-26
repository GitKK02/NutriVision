from __future__ import annotations

from datetime import datetime
from typing import Any


MEAL_GROUPS = (
    ("🌅 Завтрак", 5, 11),
    ("☀️ Обед", 11, 16),
    ("🍎 Перекус", 16, 18),
    ("🌙 Ужин", 18, 24),
    ("🌙 Поздний приём пищи", 0, 5),
)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _created_at(row: dict[str, Any]) -> datetime:
    raw = str(row.get("created_at") or "")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return datetime.min


def meal_group_name(row: dict[str, Any]) -> str:
    hour = _created_at(row).hour
    for title, start_hour, end_hour in MEAL_GROUPS:
        if start_hour <= hour < end_hour:
            return title
    return "🍽 Приём пищи"


def group_food_entries(
    rows: list[dict[str, Any]],
) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for row in rows:
        title = meal_group_name(row)
        grouped.setdefault(title, []).append(row)

    result: list[tuple[str, list[dict[str, Any]]]] = []
    for title, _, _ in MEAL_GROUPS:
        entries = grouped.get(title)
        if entries:
            result.append((title, entries))

    fallback = grouped.get("🍽 Приём пищи")
    if fallback:
        result.append(("🍽 Приём пищи", fallback))

    return result


def format_diary_entry(row: dict[str, Any]) -> str:
    created = _created_at(row)
    time_text = created.strftime("%H:%M") if created != datetime.min else "--:--"

    return (
        f"🍽 {row.get('title') or 'Блюдо'}\n"
        f"🕒 {time_text}\n\n"
        f"🔥 {round(_number(row.get('calories')))} ккал\n"
        f"💪 Белок: {round(_number(row.get('protein_g')))} г\n"
        f"🥑 Жиры: {round(_number(row.get('fat_g')))} г\n"
        f"🍞 Углеводы: {round(_number(row.get('carbs_g')))} г"
    )


def format_diary_summary(summary: dict[str, Any]) -> str:
    return (
        "📊 Итоги за сегодня\n\n"
        f"🍽 Блюд: {int(summary.get('food_count') or 0)}\n"
        f"🔥 Калории: {round(_number(summary.get('calories')))} ккал\n"
        f"💪 Белок: {round(_number(summary.get('protein_g')))} г\n"
        f"🥑 Жиры: {round(_number(summary.get('fat_g')))} г\n"
        f"🍞 Углеводы: {round(_number(summary.get('carbs_g')))} г\n"
        f"💧 Вода: {round(_number(summary.get('water_ml')))} мл"
    )
