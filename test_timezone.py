"""
Тест для проверки определения таймзоны
"""
from common.timezone_utils import get_user_timezone, get_timezone_display_name, get_available_timezones


def test_timezone_detection():
    """Тест определения таймзоны по языковому коду"""
    
    # Тестируем различные языковые коды
    test_cases = [
        ('ru', 'Europe/Moscow'),
        ('kz', 'Asia/Almaty'),
        ('en', 'UTC'),
        ('de', 'Europe/Berlin'),
        ('unknown', 'UTC'),  # Неизвестный код должен возвращать UTC
        (None, 'UTC'),       # None должен возвращать UTC
    ]
    
    print("🧪 Тестирование определения таймзоны:")
    for language_code, expected_timezone in test_cases:
        result = get_user_timezone(language_code)
        status = "✅" if result == expected_timezone else "❌"
        print(f"{status} {language_code} -> {result} (ожидалось: {expected_timezone})")
    
    print("\n🌍 Доступные таймзоны:")
    timezones = get_available_timezones()
    for tz, display in timezones.items():
        print(f"  {tz}: {display}")
    
    print("\n📋 Примеры отображаемых названий:")
    examples = ['Europe/Moscow', 'Asia/Almaty', 'UTC', 'Asia/Tokyo']
    for tz in examples:
        display = get_timezone_display_name(tz)
        print(f"  {tz}: {display}")


if __name__ == "__main__":
    test_timezone_detection()
