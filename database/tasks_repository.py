
from database import get_db_session
from database.models import Tasks
from database.user_repository import UserRepository


class TasksRepository:

    @staticmethod
    async def create(telegram_id: int, text: str, deadline: str, priority: int) -> Tasks:
        """Создать новую задачу"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            task = Tasks(
            user_id = user.id,
            text = text,
            deadline = deadline,
            priority = priority
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task
