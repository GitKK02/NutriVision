from aiogram import Router
from aiogram.types import Message
from database import get_user, daily_summary
from keyboards.main import today_actions_keyboard

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

    calories_target = user.get("calories_target", 0)
    protein_target = user.get("protein_target", 0)
    fat_target = user.get("fat_target", 0)
    carbs_target = user.get("carbs_target", 0)
    water_target = user.get("water_target", 0)

    await message.answer(
        "📊 Сегодня\n\n"
        f"🔥 Калории\n{summary['calories']} / {calories_target} ккал\n"
        f"{progress_bar(summary['calories'], calories_target)}\n\n"
        f"🥩 Белок\n{summary['protein_g']} / {protein_target} г\n"
        f"{progress_bar(summary['protein_g'], protein_target)}\n\n"
        f"🥑 Жиры\n{summary['fat_g']} / {fat_target} г\n"
        f"{progress_bar(summary['fat_g'], fat_target)}\n\n"
        f"🍞 Углеводы\n{summary['carbs_g']} / {carbs_target} г\n"
        f"{progress_bar(summary['carbs_g'], carbs_target)}\n\n"
        f"💧 Вода\n{summary['water_ml']} / {water_target} мл\n"
        f"{progress_bar(summary['water_ml'], water_target)}",
        reply_markup=today_actions_keyboard(),
    )
