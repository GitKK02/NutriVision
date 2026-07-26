from aiogram import Router
from aiogram.types import Message

from database import get_user, daily_summary, weekly_history
from services.openai_service import coach
from services.personal_coach import format_personal_coach_plan


router = Router()


@router.message(lambda m: m.text == "🤖 AI Coach")
async def ai_coach(message: Message):
    user = get_user(message.from_user.id)
    summary = daily_summary(message.from_user.id)
    await message.answer(coach(summary, user))


@router.message(lambda m: m.text == "🤖 Личный план")
async def personal_plan(message: Message):
    user = get_user(message.from_user.id)
    today = daily_summary(message.from_user.id)
    rows = weekly_history(message.from_user.id, 7)

    await message.answer(
        format_personal_coach_plan(user, today, rows)
    )
