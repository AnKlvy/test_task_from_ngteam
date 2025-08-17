"""
Модуль для настройки логирования без цветного вывода
"""
import logging
import sys
import os


class NoColorFormatter(logging.Formatter):
    """Форматтер без цветов и ANSI-кодов"""
    
    def format(self, record):
        # Удаляем ANSI escape коды из сообщения
        message = super().format(record)
        # Простое удаление ANSI кодов
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', message)


def setup_clean_logging():
    """Настройка чистого логирования без цветов"""
    
    # Полностью очищаем все логгеры
    logging.getLogger().handlers.clear()
    
    # Отключаем цветной вывод в переменных окружения
    os.environ['NO_COLOR'] = '1'
    os.environ['FORCE_COLOR'] = '0'
    
    # Создаем простой обработчик
    handler = logging.StreamHandler(sys.stdout)
    
    # Используем наш форматтер без цветов
    formatter = NoColorFormatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Отключаем лишние логи
    logging.getLogger('aiogram').setLevel(logging.ERROR)
    logging.getLogger('aiogram.dispatcher').setLevel(logging.INFO)
    logging.getLogger('aiogram.event').setLevel(logging.INFO)
    logging.getLogger('aiogram.bot').setLevel(logging.ERROR)
    logging.getLogger('aiohttp').setLevel(logging.ERROR)
    
    return logging.getLogger(__name__)


def get_logger(name: str = None):
    """Получить логгер с правильными настройками"""
    if name is None:
        name = __name__
    return logging.getLogger(name)
