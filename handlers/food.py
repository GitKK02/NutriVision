from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import FoodStates
from database import (
    add_food,
    today_food,
    delete_food,
    award,
    get_user,
    daily_summary,
)
from keyboards.main import (
    food_menu,
    confirm_food_keyboard,
    delete_food_keyboard,
    main_menu,
    today_actions_keyboard,
)
from services.openai_service import analyze_food_text, analyze_food_image, available

router = Router()
pending = {}

# Навигационные кнопки не должны восприниматься как названия блюд.
SYSTEM_BUTTONS = {
    "📸 Анализ еды", "🍽 Питание", "💧 Вода", "📊 Сегодня",
    "📊 Прогресс", "📈 Прогресс", "☰ Меню", "🤖 AI Coach",
    "📖 История", "📋 Дневник питания", "👤 Профиль",
    "🎯 Моя цель", "⚖️ Вес", "🏆 Достижения",
    "⏰ Напоминания", "⬅️ Назад",
}

def format_result(data):
    return (
        f"🍽 {data['title']}\n\n"
        f"🔥 {round(data['calories'])} ккал\n"
        f"💪 Белок: {round(data['protein_g'])} г\n"
        f"🥑 Жиры: {round(data['fat_g'])} г\n"
        f"🍞 Углеводы: {round(data['carbs_g'])} г\n\n"
        f"{data.get('comment','')}\n\nДобавить в дневник?"
    )

@router.message(lambda m: m.text in ["🍽 Питание", "📸 Анализ еды"])
async def food(message: Message, state: FSMContext):
    await state.set_state(FoodStates.waiting_text)
    await message.answer(
        "🍽 Добавь питание\n\nНапиши, что съел, или отправь фото еды.",
        reply_markup=food_menu
    )

@router.message(lambda m: m.text == "📋 Дневник питания")
async def diary(message: Message, user_id: int | None = None):
    actual_user_id = user_id or message.from_user.id
    rows = today_food(actual_user_id)
    if not rows:
        await message.answer("📋 Сегодня дневник пуст.")
        return
    await message.answer("📋 Дневник питания сегодня")
    for row in rows:
        await message.answer(
            f"• {row['title']}\n🔥 {round(row['calories'])} ккал",
            reply_markup=delete_food_keyboard(row["id"])
        )

@router.callback_query(lambda c: c.data == "today:add_food")
async def add_food_from_today(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await food(callback.message, state)


@router.callback_query(lambda c: c.data == "today:diary")
async def diary_from_today(callback: CallbackQuery):
    await callback.answer()
    await diary(callback.message, callback.from_user.id)


@router.message(FoodStates.waiting_text, lambda m: bool(m.photo))
async def photo(message: Message, state: FSMContext):
    if not available():
        await message.answer("⚠️ Добавь OPENAI_API_KEY в .env для анализа фото.")
        return

    await message.answer("🔎 Анализирую фото...")

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        downloaded = await message.bot.download_file(file.file_path)

        data = analyze_food_image(downloaded.read())

        pending[message.from_user.id] = data
        await state.clear()

        await message.answer(
            format_result(data),
            reply_markup=confirm_food_keyboard()
        )

    except Exception as exc:
        await message.answer(
            f"Не удалось проанализировать фото: {exc}"
        )


@router.message(
    FoodStates.waiting_text,
    lambda m: bool(m.text) and m.text not in SYSTEM_BUTTONS,
)
async def food_text(message: Message, state: FSMContext):
    if not message.text:
        return

    data = analyze_food_text(message.text)
    pending[message.from_user.id] = data

    await state.clear()

    await message.answer(
        format_result(data),
        reply_markup=confirm_food_keyboard()
    )

@router.callback_query(lambda c: c.data == "food:add")
async def add_pending(callback: CallbackQuery, state: FSMContext):
    data = pending.pop(callback.from_user.id, None)
    if not data:
        await callback.answer("Нет данных")
        return
    user_id = callback.from_user.id
    add_food(
        user_id,
        data["title"],
        data["calories"],
        data["protein_g"],
        data["fat_g"],
        data["carbs_g"],
        "ai",
    )
    award(user_id, "first_food", "🍽 Первая запись питания")
    await state.clear()

    await callback.message.answer(
        f"✅ {data['title']} добавлено в дневник.",
        reply_markup=main_menu,
    )

    # Немедленно перечитываем SQLite и показываем обновлённое «Сегодня».
    from services.formatters import dashboard

    user = get_user(user_id)
    summary = daily_summary(user_id)
    await callback.message.answer(
        dashboard(user, summary),
        reply_markup=today_actions_keyboard(),
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "food:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    pending.pop(callback.from_user.id, None)
    await state.clear()
    await callback.message.answer("Ок, не добавляю.", reply_markup=main_menu)
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("food:delete:"))
async def delete(callback: CallbackQuery):
    entry_id = int(callback.data.split(":")[-1])
    delete_food(callback.from_user.id, entry_id)
    await callback.message.edit_text("🗑 Запись удалена.")
    await callback.answer()
