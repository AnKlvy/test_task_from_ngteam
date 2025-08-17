"""
Утилиты для работы с таймзонами пользователей
"""
from typing import Optional


def get_user_timezone(language_code: Optional[str] = None) -> str:
    """
    Определить таймзону пользователя на основе языкового кода
    
    Args:
        language_code: Код языка пользователя из Telegram (например, 'ru', 'en', 'kz')
    
    Returns:
        str: Название таймзоны (например, 'Europe/Moscow', 'UTC')
    """
    # Маппинг языковых кодов на таймзоны
    language_to_timezone = {
        'ru': 'Europe/Moscow',          # Русский -> Москва
        'kz': 'Asia/Almaty',           # Казахский -> Алматы  
        'uz': 'Asia/Tashkent',         # Узбекский -> Ташкент
        'ky': 'Asia/Bishkek',          # Киргизский -> Бишкек
        'tj': 'Asia/Dushanbe',         # Таджикский -> Душанбе
        'az': 'Asia/Baku',             # Азербайджанский -> Баку
        'am': 'Asia/Yerevan',          # Армянский -> Ереван
        'ka': 'Asia/Tbilisi',          # Грузинский -> Тбилиси
        'be': 'Europe/Minsk',          # Белорусский -> Минск
        'uk': 'Europe/Kiev',           # Украинский -> Киев
        'en': 'UTC',                   # Английский -> UTC
        'de': 'Europe/Berlin',         # Немецкий -> Берлин
        'fr': 'Europe/Paris',          # Французский -> Париж
        'es': 'Europe/Madrid',         # Испанский -> Мадрид
        'it': 'Europe/Rome',           # Итальянский -> Рим
        'pt': 'Europe/Lisbon',         # Португальский -> Лиссабон
        'pl': 'Europe/Warsaw',         # Польский -> Варшава
        'tr': 'Europe/Istanbul',       # Турецкий -> Стамбул
        'ar': 'Asia/Dubai',            # Арабский -> Дубай
        'fa': 'Asia/Tehran',           # Персидский -> Тегеран
        'hi': 'Asia/Kolkata',          # Хинди -> Калькутта
        'zh': 'Asia/Shanghai',         # Китайский -> Шанхай
        'ja': 'Asia/Tokyo',            # Японский -> Токио
        'ko': 'Asia/Seoul',            # Корейский -> Сеул
    }
    
    if language_code and language_code in language_to_timezone:
        return language_to_timezone[language_code]
    
    # По умолчанию возвращаем UTC
    return 'UTC'


def get_timezone_display_name(timezone: str) -> str:
    """
    Получить отображаемое название таймзоны
    
    Args:
        timezone: Название таймзоны (например, 'Europe/Moscow')
    
    Returns:
        str: Отображаемое название (например, 'Москва (UTC+3)')
    """
    timezone_names = {
        'Europe/Moscow': 'Москва (UTC+3)',
        'Asia/Almaty': 'Алматы (UTC+6)',
        'Asia/Tashkent': 'Ташкент (UTC+5)',
        'Asia/Bishkek': 'Бишкек (UTC+6)',
        'Asia/Dushanbe': 'Душанбе (UTC+5)',
        'Asia/Baku': 'Баку (UTC+4)',
        'Asia/Yerevan': 'Ереван (UTC+4)',
        'Asia/Tbilisi': 'Тбилиси (UTC+4)',
        'Europe/Minsk': 'Минск (UTC+3)',
        'Europe/Kiev': 'Киев (UTC+2)',
        'UTC': 'UTC (UTC+0)',
        'Europe/Berlin': 'Берлин (UTC+1)',
        'Europe/Paris': 'Париж (UTC+1)',
        'Europe/Madrid': 'Мадрид (UTC+1)',
        'Europe/Rome': 'Рим (UTC+1)',
        'Europe/Lisbon': 'Лиссабон (UTC+0)',
        'Europe/Warsaw': 'Варшава (UTC+1)',
        'Europe/Istanbul': 'Стамбул (UTC+3)',
        'Asia/Dubai': 'Дубай (UTC+4)',
        'Asia/Tehran': 'Тегеран (UTC+3:30)',
        'Asia/Kolkata': 'Калькутта (UTC+5:30)',
        'Asia/Shanghai': 'Шанхай (UTC+8)',
        'Asia/Tokyo': 'Токио (UTC+9)',
        'Asia/Seoul': 'Сеул (UTC+9)',
    }
    
    return timezone_names.get(timezone, f'{timezone} (неизвестно)')


def get_available_timezones() -> dict:
    """
    Получить список доступных таймзон для настроек
    
    Returns:
        dict: Словарь {timezone: display_name}
    """
    timezones = [
        'Europe/Moscow',
        'Asia/Almaty', 
        'Asia/Tashkent',
        'Asia/Bishkek',
        'Asia/Dushanbe',
        'Asia/Baku',
        'Asia/Yerevan',
        'Asia/Tbilisi',
        'Europe/Minsk',
        'Europe/Kiev',
        'UTC',
        'Europe/Berlin',
        'Europe/Paris',
        'Asia/Dubai',
        'Asia/Tokyo',
    ]
    
    return {tz: get_timezone_display_name(tz) for tz in timezones}
