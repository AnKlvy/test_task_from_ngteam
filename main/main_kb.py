from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="Список задач", callback_data="list_tasks")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

