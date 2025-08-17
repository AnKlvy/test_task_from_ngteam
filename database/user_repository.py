"""
Репозиторий для работы с пользователями
"""
from typing import Optional, List

from sqlalchemy import select

from database import get_db_session
from database.models import User


class UserRepository:
    """Репозиторий для работы с пользователями"""

    @staticmethod
    async def get_all() -> List[User]:
        """Получить всех пользователей"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).order_by(User.username)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create(telegram_id: int, username: str, tz: str) -> User:
        """Создать нового пользователя или обновить существующего"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                # Создаем нового пользователя
                user = User(telegram_id=telegram_id, username=username, tz=tz)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                # Обновляем данные существующего пользователя при необходимости
                updated = False
                if user.username != username:
                    user.username = username
                    updated = True
                if user.tz != tz:
                    user.tz = tz
                    updated = True

                if updated:
                    await session.commit()
                    await session.refresh(user)

            return user

    @staticmethod
    async def update_timezone(telegram_id: int, new_timezone: str) -> bool:
        """Обновить таймзону пользователя"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if user:
                user.tz = new_timezone
                await session.commit()
                return True
            return False
