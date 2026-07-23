from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Анализ еды"), KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="📊 Сегодня"), KeyboardButton(text="☰ Меню")],
    ],
    resize_keyboard=True
)

extended_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 AI Coach"), KeyboardButton(text="📈 Прогресс")],
        [KeyboardButton(text="📖 История"), KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="🎯 Моя цель"), KeyboardButton(text="⚖️ Вес")],
        [KeyboardButton(text="🏆 Достижения"), KeyboardButton(text="⏰ Напоминания")],
        [KeyboardButton(text="🏠 Главное меню")],
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Добавить", callback_data="food:add")],
        [
            InlineKeyboardButton(text="✏️ Изменить порцию", callback_data="food:portion"),
            InlineKeyboardButton(text="🔄 Анализировать ещё", callback_data="food:reanalyze"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")],
    ])

def today_actions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽 Добавить еду", callback_data="today:add_food"),
            InlineKeyboardButton(text="💧 Добавить воду", callback_data="today:add_water"),
        ],
        [
            InlineKeyboardButton(text="📖 Дневник", callback_data="today:diary")
        ]
    ])

def delete_food_keyboard(entry_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"food:delete:{entry_id}")
    ]])
