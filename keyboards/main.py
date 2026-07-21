from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Анализ еды"), KeyboardButton(text="📊 Сегодня")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📈 Прогресс")],
        [KeyboardButton(text="📖 История"), KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="🤖 AI Coach"), KeyboardButton(text="🏆 Достижения")],
        [KeyboardButton(text="🎯 Моя цель"), KeyboardButton(text="⚖️ Вес")],
        [KeyboardButton(text="⏰ Напоминания")]
    ],
    resize_keyboard=True
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад")]],
    resize_keyboard=True
)

goal_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💪 Набор массы")],
        [KeyboardButton(text="⚖️ Удержание")],
        [KeyboardButton(text="🔥 Дефицит")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

activity_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚶 Низкая")],
        [KeyboardButton(text="🏃 Средняя")],
        [KeyboardButton(text="🔥 Высокая")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

water_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="+250 мл"), KeyboardButton(text="+500 мл")],
        [KeyboardButton(text="+750 мл"), KeyboardButton(text="+1000 мл")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

food_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Дневник питания")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

def confirm_food_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Добавить", callback_data="food:add"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")
    ]])

def delete_food_keyboard(entry_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"food:delete:{entry_id}")
    ]])
