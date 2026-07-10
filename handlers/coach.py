from aiogram import Router
from aiogram.types import Message
from database import get_user, daily_summary
from services.openai_service import coach

router = Router()

@router.message(lambda m: m.text == "🤖 AI Coach")
async def ai_coach(message: Message):
    user = get_user(message.from_user.id)
    summary = daily_summary(message.from_user.id)
    await message.answer(coach(summary, user))
