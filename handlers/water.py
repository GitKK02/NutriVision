from aiogram import Router
from aiogram.types import Message, CallbackQuery
from database import add_water, today_water, get_user, award
from keyboards.main import water_menu
from services.formatters import bar

router = Router()

@router.message(lambda m: m.text == "💧 Вода")
async def water(message: Message, user_id: int | None = None):
    actual_user_id = user_id or message.from_user.id
    user = get_user(actual_user_id)
    target = user.get("water_target") or 2500
    value = today_water(actual_user_id)
    await message.answer(
        f"💧 Вода\n\nСегодня: {value} / {target} мл\n{bar(value,target)}",
        reply_markup=water_menu
    )

@router.callback_query(lambda c: c.data == "today:add_water")
async def add_water_from_today(callback: CallbackQuery):
    await callback.answer()
    await water(callback.message, callback.from_user.id)


@router.message(lambda m: m.text in {"+250 мл","+500 мл","+750 мл","+1000 мл"})
async def add(message: Message):
    amount = int(message.text.split()[0].replace("+",""))
    add_water(message.from_user.id, amount)
    user = get_user(message.from_user.id)
    target = user.get("water_target") or 2500
    value = today_water(message.from_user.id)
    if value >= target:
        award(message.from_user.id, "water_goal", "💧 Выполнена цель по воде")
    await message.answer(
        f"✅ Добавлено {amount} мл\n\nСегодня: {value} / {target} мл\n{bar(value,target)}",
        reply_markup=water_menu
    )
