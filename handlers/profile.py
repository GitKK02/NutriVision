from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import ProfileStates
from keyboards.main import back_menu, gender_menu, activity_menu, main_menu
from database import get_user, update_user
from services.calculations import calculate_targets
from services.formatters import goal_name

router = Router()

@router.message(lambda m: m.text == "👤 Профиль")
async def profile(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if user and user.get("profile_completed"):
        await message.answer(
            "👤 Профиль\n\n"
            f"Возраст: {user['age']}\n"
            f"Пол: {'Мужской' if user['gender']=='male' else 'Женский'}\n"
            f"Рост: {user['height_cm']} см\n"
            f"Вес: {user['weight_kg']} кг\n"
            f"Целевой вес: {user['target_weight_kg']} кг\n"
            f"Активность: {user['activity']}\n"
            f"Цель: {goal_name(user.get('goal'))}\n\n"
            "Чтобы изменить профиль, отправь /profile_reset"
        )
        return
    await state.set_state(ProfileStates.age)
    await message.answer("Введите возраст:", reply_markup=back_menu)

@router.message(lambda m: m.text == "/profile_reset")
async def reset_profile(message: Message, state: FSMContext):
    await state.set_state(ProfileStates.age)
    await message.answer("Введите возраст:", reply_markup=back_menu)

@router.message(ProfileStates.age)
async def age(message: Message, state: FSMContext):
    try:
        value = int(message.text)
        if not 14 <= value <= 100:
            raise ValueError
    except Exception:
        await message.answer("Введите возраст числом от 14 до 100.")
        return
    await state.update_data(age=value)
    await state.set_state(ProfileStates.gender)
    await message.answer("Выберите пол:", reply_markup=gender_menu)

@router.message(ProfileStates.gender)
async def gender(message: Message, state: FSMContext):
    mapping = {"Мужской":"male","Женский":"female"}
    if message.text not in mapping:
        await message.answer("Выберите вариант кнопкой.")
        return
    await state.update_data(gender=mapping[message.text])
    await state.set_state(ProfileStates.height)
    await message.answer("Введите рост в сантиметрах:", reply_markup=back_menu)

@router.message(ProfileStates.height)
async def height(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(",", "."))
        if not 120 <= value <= 230:
            raise ValueError
    except Exception:
        await message.answer("Введите рост от 120 до 230 см.")
        return
    await state.update_data(height_cm=value)
    await state.set_state(ProfileStates.weight)
    await message.answer("Введите текущий вес в кг:")

@router.message(ProfileStates.weight)
async def weight(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(",", "."))
        if not 35 <= value <= 350:
            raise ValueError
    except Exception:
        await message.answer("Введите корректный вес.")
        return
    await state.update_data(weight_kg=value)
    await state.set_state(ProfileStates.target_weight)
    await message.answer("Введите желаемый вес в кг:")

@router.message(ProfileStates.target_weight)
async def target_weight(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(",", "."))
        if not 35 <= value <= 350:
            raise ValueError
    except Exception:
        await message.answer("Введите корректный желаемый вес.")
        return
    await state.update_data(target_weight_kg=value)
    await state.set_state(ProfileStates.activity)
    await message.answer("Выберите активность:", reply_markup=activity_menu)

@router.message(ProfileStates.activity)
async def activity(message: Message, state: FSMContext):
    mapping = {"🚶 Низкая":"low","🏃 Средняя":"medium","🔥 Высокая":"high"}
    if message.text not in mapping:
        await message.answer("Выберите вариант кнопкой.")
        return
    data = await state.get_data()
    data["activity"] = mapping[message.text]
    update_user(message.from_user.id, **data, profile_completed=1)
    user = get_user(message.from_user.id)

    if user and user.get("goal"):
        update_user(message.from_user.id, **calculate_targets(
            user["age"], user["gender"], user["height_cm"],
            user["weight_kg"], user["activity"], user["goal"]
        ))
    await state.clear()
    await message.answer("✅ Профиль сохранён.", reply_markup=main_menu)
