from aiogram import Router
from aiogram.types import Message
from database import day_history

router = Router()

@router.message(lambda m: m.text in ["📅 История", "📖 История"])
async def history(message: Message):
    rows = day_history(message.from_user.id, 7)
    if not rows:
        await message.answer("📅 История пока пуста.")
        return
    text = "📅 Последние дни\n\n"
    for r in rows:
        text += f"{r['day']}\n🔥 {r['calories'] or 0} ккал · 💪 {r['protein_g'] or 0} г · 💧 {r['water_ml']} мл\n\n"
    await message.answer(text)
