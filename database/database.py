"""
Конфигурация подключения к базе данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from os import getenv
from dotenv import load_dotenv
from .models import Base

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = getenv("POSTGRES_DB", "testbot")
POSTGRES_HOST = getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = None
async_session = None

def _get_engine():
    """Получить или создать движок базы данных"""
    global engine
    if engine is None:
        engine = create_async_engine(DATABASE_URL, echo=False)
    return engine

def _get_session_maker():
    """Получить или создать фабрику сессий"""
    global async_session
    if async_session is None:
        async_session = async_sessionmaker(_get_engine(), class_=AsyncSession, expire_on_commit=False)
    return async_session


async def init_database():
    """Инициализация базы данных - создание всех таблиц"""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Закрытие соединения с базой данных"""
    global engine
    if engine:
        await engine.dispose()
        engine = None
    print("🔌 Соединение с базой данных закрыто")

def get_db_session() -> AsyncSession:
    """Получить сессию базы данных"""
    session_maker = _get_session_maker()
    return session_maker()
