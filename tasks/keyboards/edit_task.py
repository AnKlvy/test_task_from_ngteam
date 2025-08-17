from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_edit_task_kb(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования задачи"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить текст", callback_data=f"edit_text_{task_id}")],
        [InlineKeyboardButton(text="📅 Изменить дедлайн", callback_data=f"edit_deadline_{task_id}")],
        [InlineKeyboardButton(text="⚡ Изменить приоритет", callback_data=f"edit_priority_{task_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"view_task_{task_id}")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])


def get_edit_priority_kb(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора нового приоритета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Высокий", callback_data=f"set_priority_{task_id}_3")],
        [InlineKeyboardButton(text="🟡 Средний", callback_data=f"set_priority_{task_id}_2")],
        [InlineKeyboardButton(text="🟢 Низкий", callback_data=f"set_priority_{task_id}_1")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"edit_task_{task_id}")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
