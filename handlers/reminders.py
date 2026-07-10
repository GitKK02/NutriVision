from aiogram import Router
from aiogram.types import Message
from database import get_user, update_user

router = Router()

@router.message(lambda m: m.text == "⏰ Напоминания")
async def reminders(message: Message):
    user = get_user(message.from_user.id)
    enabled = bool(user.get("reminders_enabled"))
    update_user(message.from_user.id, reminders_enabled=0 if enabled else 1)
    await message.answer("⏰ Напоминания " + ("выключены" if enabled else "включены"))
