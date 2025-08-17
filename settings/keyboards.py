"""
Клавиатуры для настроек
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict


def get_settings_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню настроек"""
    keyboard = [
        [InlineKeyboardButton(text="🌍 Изменить таймзону", callback_data="change_timezone")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_timezone_selection_kb(timezones: Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора таймзоны
    
    Args:
        timezones: Словарь {timezone: display_name}
    """
    keyboard = []
    
    # Добавляем кнопки для каждой таймзоны
    for timezone, display_name in timezones.items():
        keyboard.append([
            InlineKeyboardButton(
                text=display_name, 
                callback_data=f"set_timezone_{timezone}"
            )
        ])
    
    # Кнопка назад
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="back_to_settings")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
