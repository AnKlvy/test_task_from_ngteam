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
    try:
        from settings.handlers import show_settings
        # Создаем фиктивный callback для совместимости
        class FakeCallback:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user

        fake_callback = FakeCallback(message)
        await show_settings(fake_callback, state)
    except ImportError:
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
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_menu_kb())


async def _perform_export(user_id: int, chat_id: int, bot):
    """Вспомогательная функция для выполнения экспорта"""
    from database.tasks_repository import TasksRepository
    from database.user_repository import UserRepository
    from tasks.services.csv_export import generate_csv_content, generate_filename
    from aiogram.types import BufferedInputFile
    from common.logger import get_logger

    logger = get_logger(__name__)
    logger.info(f"Начинаем экспорт для пользователя {user_id}")

    # Проверяем, существует ли пользователь в базе данных
    user = await UserRepository.get_by_telegram_id(user_id)
    if not user:
        await bot.send_message(chat_id, "❌ Пользователь не найден в базе данных. Попробуйте выполнить команду /start")
        return

    # Получаем все задачи пользователя
    tasks = await TasksRepository.get_all_by_user(user_id)
    logger.info(f"Получено {len(tasks) if tasks else 0} задач для пользователя {user_id}")

    if not tasks:
        logger.info(f"У пользователя {user_id} нет задач для экспорта")
        await bot.send_message(chat_id, f"📋 У вас пока нет задач для экспорта\n"
                             f"👤 Пользователь ID: {user.id}\n"
                             f"📱 Telegram ID: {user_id}")
        return

    # Генерируем CSV содержимое
    logger.info("Начинаем генерацию CSV содержимого")
    csv_content = await generate_csv_content(tasks)
    logger.info(f"CSV содержимое сгенерировано, размер: {len(csv_content)} символов")

    # Создаем файл для отправки
    filename = generate_filename(user_id)
    logger.info(f"Генерируем файл с именем: {filename}")


    csv_file = BufferedInputFile(
        csv_content.encode('utf-8-sig'),
        filename=filename
    )

    # Отправляем файл
    logger.info("Отправляем файл пользователю")
    await bot.send_document(
        chat_id=chat_id,
        document=csv_file,
        caption=f"📊 Экспорт задач завершен!\n\n"
               f"📋 Всего задач: {len(tasks)}\n"
               f"📅 Дата экспорта: {filename.split('_')[-1].replace('.csv', '')}"
    )
    logger.info("Файл успешно отправлен")


async def export_command(message: Message, state: FSMContext):
    """Обработчик команды /export"""
    try:
        await _perform_export(message.from_user.id, message.chat.id, message.bot)
    except Exception as e:
        await message.answer(f"❌ Ошибка при экспорте: {str(e)}")


@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Помощь"""
    await help_command(callback.message, state)
    await callback.answer()


@router.callback_query(lambda c: c.data == "export_csv")
async def export_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Экспорт CSV"""
    try:
        await _perform_export(callback.from_user.id, callback.message.chat.id, callback.bot)
        await callback.answer("✅ Файл отправлен!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при экспорте: {str(e)}")
        await callback.answer()
