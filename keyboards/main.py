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
        [
            KeyboardButton(text="📋 Дневник питания"),
            KeyboardButton(text="⭐ Избранное"),
        ],
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

def recent_foods_keyboard(rows):
    buttons = []
    for row in rows:
        title = str(row.get("title") or "Блюдо").strip()
        if len(title) > 30:
            title = title[:27].rstrip() + "..."
        buttons.append([
            InlineKeyboardButton(
                text=f"➕ {title}",
                callback_data=f"food:quick_add:{row['id']}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

def diary_entry_keyboard(entry_id: int, is_favorite: bool = False):
    favorite_text = "★ Убрать из избранного" if is_favorite else "⭐ В избранное"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=favorite_text,
                callback_data=f"food:favorite_toggle:{entry_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Изменить порцию",
                callback_data=f"food:edit:{entry_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔁 Повторить",
                callback_data=f"food:repeat:{entry_id}",
            ),
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"food:delete:{entry_id}",
            ),
        ],
    ])


def favorite_meals_keyboard(rows):
    buttons = []

    for row in rows:
        title = str(row.get("title") or "Блюдо").strip()
        if len(title) > 28:
            title = title[:25].rstrip() + "..."

        buttons.append([
            InlineKeyboardButton(
                text=f"➕ {title}",
                callback_data=f"food:favorite_add:{row['id']}",
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text=f"★ Удалить {title}",
                callback_data=f"food:favorite_remove:{row['id']}",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def saved_food_edit_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="food:edit_cancel")]
    ])


def delete_food_keyboard(entry_id: int):
    return diary_entry_keyboard(entry_id)
