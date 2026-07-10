from aiogram import Router
from aiogram.types import Message
from database import get_user, update_user
from keyboards.main import goal_menu, main_menu
from services.calculations import calculate_targets
from services.formatters import goal_name

router = Router()

@router.message(lambda m: m.text == "🎯 Моя цель")
async def goals(message: Message):
    user = get_user(message.from_user.id)
    if user and user.get("goal"):
        await message.answer(f"Текущая цель: {goal_name(user['goal'])}\n\nМожно выбрать другую:", reply_markup=goal_menu)
    else:
        await message.answer("Выберите цель:", reply_markup=goal_menu)

@router.message(lambda m: m.text in {"💪 Набор массы","⚖️ Удержание","🔥 Дефицит"})
async def save_goal(message: Message):
    mapping = {"💪 Набор массы":"gain","⚖️ Удержание":"maintain","🔥 Дефицит":"deficit"}
    goal = mapping[message.text]
    update_user(message.from_user.id, goal=goal)
    user = get_user(message.from_user.id)
    if user.get("profile_completed"):
        targets = calculate_targets(
            user["age"], user["gender"], user["height_cm"],
            user["weight_kg"], user["activity"], goal
        )
        update_user(message.from_user.id, **targets)
        user = get_user(message.from_user.id)
        await message.answer(
            f"✅ Цель сохранена: {goal_name(goal)}\n\n"
            f"🔥 {user['calories_target']} ккал\n"
            f"💪 {user['protein_target']} г\n"
            f"🥑 {user['fat_target']} г\n"
            f"🍞 {user['carbs_target']} г",
            reply_markup=main_menu
        )
    else:
        await message.answer("✅ Цель сохранена. Теперь заполни профиль.", reply_markup=main_menu)
