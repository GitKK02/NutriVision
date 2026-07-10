from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import WeightStates
from keyboards.main import back_menu, main_menu
from database import add_weight, weight_history, get_user

router = Router()

@router.message(lambda m: m.text == "⚖️ Вес")
async def weight(message: Message, state: FSMContext):
    history = weight_history(message.from_user.id, 5)
    text = "⚖️ Вес\n\n"
    if history:
        text += f"Текущий: {history[0]['weight_kg']} кг\n\n"
        text += "Последние записи:\n" + "\n".join(
            f"{x['created_at'][:10]} — {x['weight_kg']} кг" for x in history
        )
    text += "\n\nВведите новый вес:"
    await state.set_state(WeightStates.value)
    await message.answer(text, reply_markup=back_menu)

@router.message(WeightStates.value)
async def save_weight(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(",", "."))
        if not 35 <= value <= 350:
            raise ValueError
    except Exception:
        await message.answer("Введите корректный вес.")
        return
    add_weight(message.from_user.id, value)
    await state.clear()
    await message.answer(f"✅ Вес сохранён: {value} кг", reply_markup=main_menu)
