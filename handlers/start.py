from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import ensure_user, get_user, daily_summary
from keyboards.main import main_menu
from services.formatters import bar, goal_name

router = Router()

def dashboard(user, summary):
    return (
        f"👋 Привет, {user.get('first_name') or 'друг'}!\n\n"
        f"🎯 {goal_name(user.get('goal'))}\n\n"
        f"🔥 Калории\n{summary['calories']} / {user.get('calories_target') or 0}\n"
        f"{bar(summary['calories'], user.get('calories_target') or 1)}\n\n"
        f"💪 Белок\n{summary['protein_g']} / {user.get('protein_target') or 0} г\n"
        f"{bar(summary['protein_g'], user.get('protein_target') or 1)}\n\n"
        f"💧 Вода\n{summary['water_ml']} / {user.get('water_target') or 0} мл\n"
        f"{bar(summary['water_ml'], user.get('water_target') or 1)}\n\n"
        "Выбери действие 👇"
    )

@router.message(Command("start"))
async def start(message: Message):
    u = message.from_user
    ensure_user(u.id, u.first_name or "", u.username or "")
    user = get_user(u.id)
    await message.answer(dashboard(user, daily_summary(u.id)), reply_markup=main_menu)

@router.message(lambda m: m.text == "⬅️ Назад")
async def back(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(dashboard(user, daily_summary(message.from_user.id)), reply_markup=main_menu)
