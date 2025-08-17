import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Настройка логирования ПЕРЕД импортом aiogram модулей
from common.logger import setup_clean_logging, get_logger

# Настраиваем логирование в самом начале
setup_clean_logging()
logger = get_logger(__name__)

from database.database import init_database
from main.commands import setup_commands, set_bot_commands
from tasks.handlers import router as tasks_router
from aiogramx import Calendar, TimeSelectorGrid
from main.main_handlers import router as main_router

load_dotenv()
API_TOKEN = getenv("BOT_TOKEN")
async def main() -> None:
    """Главная функция запуска бота"""
    try:
        bot = Bot(token=API_TOKEN)
        dp = Dispatcher()
        logger.info("Запуск в polling режиме")

        # Установка меню команд
        await set_bot_commands(bot)
        logger.info("✅ Меню команд установлено")

        await setup_commands(dp)

        # Регистрация виджетов aiogramx
        Calendar.register(dp)
        TimeSelectorGrid.register(dp)
        logger.info("✅ Виджеты aiogramx зарегистрированы")

        dp.include_router(main_router)
        dp.include_router(tasks_router)
        try:
            await init_database()
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации базы данных: {e}")
            logger.warning("⚠️ Продолжаем работу без базы данных")
        await dp.start_polling(bot)

    except Exception as e:
        print ("main: ",e)

if __name__ == "__main__":
    asyncio.run(main())