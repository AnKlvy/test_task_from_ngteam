from aiogram import Dispatcher
from aiogram.filters import CommandStart

from main.main_handlers import show_main_menu


async def start_command(message, state):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    await state.clear()
    await show_main_menu(message, state=state)

async def setup_commands(dp: Dispatcher):
    """Настройка команд бота"""
    dp.message.register(start_command, CommandStart())

