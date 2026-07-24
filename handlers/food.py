import asyncio
from contextlib import suppress

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
from services.openai_service import (
    analyze_food_text, analyze_food_image, recalculate_food_portion,
    reanalyze_food_text, reanalyze_food_image, available,
)

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


async def animate_analysis(status_message: Message, stages: list[str], delay: float = 1.0):
    """Обновляет одно сообщение, пока AI выполняет анализ."""
    index = 0
    while True:
        stage = stages[min(index, len(stages) - 1)]
        try:
            await status_message.edit_text(stage)
        except Exception:
            pass
        index += 1
        await asyncio.sleep(delay)


async def finish_analysis(animation_task: asyncio.Task, status_message: Message, text: str):
    animation_task.cancel()
    with suppress(asyncio.CancelledError):
        await animation_task
    try:
        await status_message.edit_text(text)
    except Exception:
        pass

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

    status_message = await message.answer("📷 Фото получено")
    animation_task = asyncio.create_task(
        animate_analysis(
            status_message,
            [
                "📷 Фото получено\n\nПодготавливаю изображение...",
                "🔎 Распознаю продукты...",
                "🍽 Определяю состав блюда...",
                "⚖️ Оцениваю размер порции...",
                "🧠 Рассчитываю калории и БЖУ...",
                "✨ Проверяю результат...",
            ],
        )
    )

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        downloaded = await message.bot.download_file(file.file_path)

        image_bytes = downloaded.read()
        data = await asyncio.to_thread(analyze_food_image, image_bytes)

        pending[message.from_user.id] = {
            **data, "_source": "photo", "_image_bytes": image_bytes
        }
        await state.clear()
        await finish_analysis(animation_task, status_message, "✅ Анализ завершён")

        await message.answer(
            format_result(data),
            reply_markup=confirm_food_keyboard()
        )

    except Exception as exc:
        await finish_analysis(animation_task, status_message, "❌ Не удалось завершить анализ")
        await message.answer(f"Не удалось проанализировать фото: {exc}")


@router.message(
    FoodStates.waiting_text,
    lambda m: bool(m.text) and m.text not in SYSTEM_BUTTONS,
)
async def food_text(message: Message, state: FSMContext):
    if not message.text:
        return

    original_text = message.text.strip()
    status_message = await message.answer("📝 Описание получено")
    animation_task = asyncio.create_task(
        animate_analysis(
            status_message,
            [
                "📝 Описание получено\n\nИзучаю состав блюда...",
                "🔎 Анализирую продукты...",
                "⚖️ Оцениваю порцию...",
                "🧠 Рассчитываю калории и БЖУ...",
                "✨ Проверяю результат...",
            ],
        )
    )

    try:
        data = await asyncio.to_thread(analyze_food_text, original_text)
        pending[message.from_user.id] = {
            **data, "_source": "text", "_original_text": original_text
        }

        await state.clear()
        await finish_analysis(animation_task, status_message, "✅ Анализ завершён")

        await message.answer(
            format_result(data),
            reply_markup=confirm_food_keyboard()
        )
    except Exception as exc:
        await finish_analysis(animation_task, status_message, "❌ Не удалось завершить анализ")
        await message.answer(f"Не удалось проанализировать описание: {exc}")


@router.callback_query(lambda c: c.data == "food:portion")
async def request_portion(callback: CallbackQuery, state: FSMContext):
    if not pending.get(callback.from_user.id):
        await callback.answer("Результат анализа уже недоступен.", show_alert=True)
        return
    await state.set_state(FoodStates.waiting_portion)
    await callback.message.answer(
        "✏️ Укажи новую порцию.\n\n"
        "Например:\n• 150 г\n• 250 грамм\n• 2 порции\n• половина порции"
    )
    await callback.answer()


@router.message(
    FoodStates.waiting_portion,
    lambda m: bool(m.text) and m.text not in SYSTEM_BUTTONS,
)
async def update_portion(message: Message, state: FSMContext):
    current = pending.get(message.from_user.id)
    if not current:
        await state.clear()
        await message.answer(
            "Результат анализа уже недоступен. Запусти анализ заново.",
            reply_markup=main_menu,
        )
        return

    status_message = await message.answer("⚖️ Новая порция получена")
    animation_task = asyncio.create_task(
        animate_analysis(
            status_message,
            [
                "⚖️ Уточняю размер порции...",
                "🧠 Пересчитываю калории и БЖУ...",
                "✨ Проверяю новые значения...",
            ],
            delay=0.9,
        )
    )
    try:
        metadata = {k: v for k, v in current.items() if k.startswith("_")}
        nutrition = {k: v for k, v in current.items() if not k.startswith("_")}
        updated = await asyncio.to_thread(
            recalculate_food_portion,
            nutrition,
            message.text.strip(),
        )
        pending[message.from_user.id] = {**updated, **metadata}
        await state.clear()
        await finish_analysis(animation_task, status_message, "✅ Порция пересчитана")
        await message.answer(format_result(updated), reply_markup=confirm_food_keyboard())
    except Exception as exc:
        await finish_analysis(animation_task, status_message, "❌ Не удалось пересчитать порцию")
        await message.answer(
            f"Не удалось пересчитать порцию: {exc}\n\n"
            "Попробуй: 150 г, 2 порции или половина порции."
        )


@router.callback_query(lambda c: c.data == "food:reanalyze")
async def reanalyze_pending(callback: CallbackQuery, state: FSMContext):
    current = pending.get(callback.from_user.id)
    if not current:
        await callback.answer("Результат анализа уже недоступен.", show_alert=True)
        return

    await callback.answer()
    status_message = await callback.message.answer("🔄 Запускаю повторный анализ")
    animation_task = asyncio.create_task(
        animate_analysis(
            status_message,
            [
                "🔄 Повторно изучаю блюдо...",
                "🔎 Проверяю распознанные продукты...",
                "⚖️ Уточняю размер порции...",
                "🧠 Пересчитываю калории и БЖУ...",
                "✨ Сравниваю результат...",
            ],
        )
    )

    try:
        if current.get("_source") == "photo":
            image_bytes = current.get("_image_bytes")
            if not image_bytes:
                raise RuntimeError("Исходное фото не найдено")
            updated = await asyncio.to_thread(reanalyze_food_image, image_bytes)
            pending[callback.from_user.id] = {
                **updated, "_source": "photo", "_image_bytes": image_bytes
            }
        elif current.get("_source") == "text":
            original_text = current.get("_original_text")
            if not original_text:
                raise RuntimeError("Исходное описание не найдено")
            updated = await asyncio.to_thread(reanalyze_food_text, original_text)
            pending[callback.from_user.id] = {
                **updated, "_source": "text", "_original_text": original_text
            }
        else:
            raise RuntimeError("Неизвестный источник анализа")

        await state.clear()
        await finish_analysis(animation_task, status_message, "✅ Повторный анализ завершён")
        await callback.message.answer(format_result(updated), reply_markup=confirm_food_keyboard())
    except Exception as exc:
        await finish_analysis(animation_task, status_message, "❌ Повторный анализ не завершён")
        await callback.message.answer(f"Не удалось повторить анализ: {exc}")

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
