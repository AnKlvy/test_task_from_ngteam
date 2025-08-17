from aiogram import Dispatcher, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message, CallbackQuery

from main.main_handlers import show_main_menu, router
from main.main_kb import get_menu_kb, get_main_menu_kb


async def start_command(message, state):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    await state.clear()
    await show_main_menu(message, state=state)

async def new_command(message, state):
    """Обработчик команды /new - создать задачу"""
    try:
        from tasks.handlers.create_task import start_create_task
        await start_create_task(message, state)
    except ImportError:
        await message.answer("📝 Функция создания задач пока не реализована")

async def list_command(message, state):
    """Обработчик команды /list - список задач"""
    try:
        from tasks.handlers.list_tasks import show_tasks_list
        await show_tasks_list(message, state)
    except ImportError:
        await message.answer("📋 Функция списка задач пока не реализована")

async def settings_command(message, state):
    """Обработчик команды /settings - настройки"""
    await message.answer("⚙️ Настройки пока не реализованы")

async def set_bot_commands(bot: Bot):
    """Установка меню команд бота"""
    commands = [
        BotCommand(command="start", description="Запуск и приветствие"),
        BotCommand(command="new", description="Создать задачу"),
        BotCommand(command="list", description="Список задач"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="export", description="Выгрузка CSV"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)

async def setup_commands(dp: Dispatcher):
    """Настройка команд бота"""
    dp.message.register(start_command, CommandStart())
    dp.message.register(new_command, Command("new"))
    dp.message.register(list_command, Command("list"))
    dp.message.register(settings_command, Command("settings"))
    dp.message.register(export_command, Command("export"))
    dp.message.register(help_command, Command("help"))


async def help_command(message: Message, state: FSMContext):
    """Обработчик команды /help"""
    help_text = (
        "🤖 **Справка по Task Manager**\n\n"
        "**Доступные команды:**\n"
        "/start — запуск и приветствие\n"
        "/new — создать новую задачу\n"
        "/list — показать список задач\n"
        "/settings — настройки бота\n"
        "/export — выгрузка задач в CSV\n"
        "/help — показать эту справку\n\n"
        "**Возможности бота:**\n"
        "• Создание задач с дедлайнами\n"
        "• Управление приоритетами\n"
        "• Отслеживание выполнения\n"
        "• Экспорт данных в CSV\n\n"
        "Используйте кнопки меню или команды для навигации!"
    )
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_menu_kb())


async def export_command(message: Message, state: FSMContext):
    """Обработчик команды /export"""
    await message.answer("📊 Экспорт в CSV пока не реализован")


@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Помощь"""
    await help_command(callback.message, state)
    await callback.answer()


@router.callback_query(lambda c: c.data == "export_csv")
async def export_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Экспорт CSV"""
    await export_command(callback.message, state)
    await callback.answer()
