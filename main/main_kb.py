from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="Список задач", callback_data="list_tasks")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="Экспорт CSV", callback_data="export_csv")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

