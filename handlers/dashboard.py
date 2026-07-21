from aiogram import Router
from aiogram.types import Message
from database import get_user, daily_summary

router = Router()


def progress_bar(value, target):
    if not target:
        return "░░░░░░░░░░ 0%"
    percent = min(100, round(value / target * 100))
    filled = round(percent / 10)
    return "█" * filled + "░" * (10 - filled) + f" {percent}%"


@router.message(lambda m: m.text == "📊 Сегодня")
async def today_dashboard(message: Message):
    user = get_user(message.from_user.id)
    summary = daily_summary(message.from_user.id)

    if not user or not user.get("profile_completed"):
        await message.answer("Сначала заполните профиль 👤")
        return
    
    await message.answer(
        "📊 Сегодня\n\n"
        f"🔥 Калории\n{summary['calories']} / {user.get('calories_target', 0)}\n\n"
        f"🥩 Белок\n{summary['protein_g']} / {user.get('protein_target', 0)} г\n\n"
        f"🥑 Жиры\n{summary['fat_g']} / {user.get('fat_target', 0)} г\n\n"
        f"🍞 Углеводы\n{summary['carbs_g']} / {user.get('carbs_target', 0)} г\n\n"
        f"💧 Вода\n{summary['water_ml']} / {user.get('water_target', 0)} мл"
    )
    
