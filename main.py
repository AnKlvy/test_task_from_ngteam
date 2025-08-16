import asyncio
import logging

from aiogram import Bot, Dispatcher

from database.database import init_database
from main.commands import setup_commands
from tasks.handlers import router as tasks_router

API_TOKEN = '7347393174:AAF7-W2t-6DfTLNW77EoRlEPVFBmWNknnnQ'

from main.main_handlers import router as main_router

# Configure logging
logging.basicConfig(level=logging.INFO)
async def main() -> None:
    """Главная функция запуска бота"""
    try:
        bot = Bot(token=API_TOKEN)
        dp = Dispatcher()
        logging.info("Запуск в polling режиме")
        await setup_commands(dp)
        dp.include_router(main_router)
        dp.include_router(tasks_router)
        try:
            await init_database()
            logging.info("✅ База данных инициализирована")
        except Exception as e:
            logging.error(f"❌ Ошибка инициализации базы данных: {e}")
            logging.warning("⚠️ Продолжаем работу без базы данных")
        await dp.start_polling(bot)

    except Exception as e:
        print ("main: ",e)

if __name__ == "__main__":
    asyncio.run(main())