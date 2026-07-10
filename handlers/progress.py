from aiogram import Router
from aiogram.types import Message
from database import get_user, daily_summary
from services.formatters import bar, goal_name

router = Router()

@router.message(lambda m: m.text == "📊 Прогресс")
async def progress(message: Message):
    user = get_user(message.from_user.id)
    s = daily_summary(message.from_user.id)
    await message.answer(
        "📊 Прогресс сегодня\n\n"
        f"🎯 {goal_name(user.get('goal'))}\n\n"
        f"🔥 Калории: {s['calories']} / {user.get('calories_target') or 0}\n"
        f"{bar(s['calories'], user.get('calories_target') or 1)}\n\n"
        f"💪 Белок: {s['protein_g']} / {user.get('protein_target') or 0} г\n"
        f"{bar(s['protein_g'], user.get('protein_target') or 1)}\n\n"
        f"🥑 Жиры: {s['fat_g']} / {user.get('fat_target') or 0} г\n"
        f"{bar(s['fat_g'], user.get('fat_target') or 1)}\n\n"
        f"🍞 Углеводы: {s['carbs_g']} / {user.get('carbs_target') or 0} г\n"
        f"{bar(s['carbs_g'], user.get('carbs_target') or 1)}\n\n"
        f"💧 Вода: {s['water_ml']} / {user.get('water_target') or 0} мл\n"
        f"{bar(s['water_ml'], user.get('water_target') or 1)}"
    )
