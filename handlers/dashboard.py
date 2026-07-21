from aiogram import Router
from aiogram.types import Message
from database import get_user

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

    if not user or not user.get("profile_completed"):
        await message.answer("Сначала заполните профиль 👤")
        return

    await message.answer(
        "📊 Сегодня\n\n"
        f"🔥 Калории\n{user.get('today_calories', 0)} / {user.get('calories_target', 0)}\n"
        f"{progress_bar(user.get('today_calories', 0), user.get('calories_target', 0))}\n\n"
        f"🥩 Белок\n{user.get('today_protein', 0)} / {user.get('protein_target', 0)} г\n"
        f"{progress_bar(user.get('today_protein', 0), user.get('protein_target', 0))}\n\n"
        f"💧 Вода\n{user.get('today_water', 0)} / {user.get('water_target', 0)} мл"
    )
