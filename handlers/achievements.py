from aiogram import Router
from aiogram.types import Message
from database import list_achievements

router = Router()

@router.message(lambda m: m.text == "🏆 Достижения")
async def achievements(message: Message):
    rows = list_achievements(message.from_user.id)
    if not rows:
        await message.answer("🏆 Пока нет достижений. Начни вести дневник.")
        return
    await message.answer("🏆 Достижения\n\n" + "\n".join(f"• {x['title']}" for x in rows))
