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
        """Создать нового пользователя"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                user = User(telegram_id=telegram_id, username=username, tz=tz)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user
