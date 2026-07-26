from aiogram import Router
from aiogram.types import Message

from database import day_history, get_user, weekly_history
from services.weekly_report import format_weekly_report


router = Router()


@router.message(lambda m: m.text in ["📅 История", "📖 История"])
async def history(message: Message):
    rows = day_history(message.from_user.id, 7)
    if not rows:
        await message.answer("📅 История пока пуста.")
        return

    text = "📅 Последние дни\n\n"
    for row in rows:
        text += (
            f"{row['day']}\n"
            f"🔥 {row['calories'] or 0} ккал · "
            f"💪 {row['protein_g'] or 0} г · "
            f"💧 {row['water_ml']} мл\n\n"
        )
    await message.answer(text)


@router.message(lambda m: m.text == "📅 Отчёт за неделю")
async def weekly_report(message: Message):
    user = get_user(message.from_user.id)
    rows = weekly_history(message.from_user.id, 7)
    await message.answer(format_weekly_report(user, rows))
