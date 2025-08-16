from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choose_priority_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Низкий", callback_data="create_priority_1")],
        [InlineKeyboardButton(text="Средний", callback_data="create_priority_2")],
        [InlineKeyboardButton(text="Высокий", callback_data="create_priority_3")],
    ])

def confirm_create_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать", callback_data="confirm_create_1")],
        [InlineKeyboardButton(text="Отмена", callback_data="confirm_create_2")],
    ])
