
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy import select, and_

from database import get_db_session
from database.models import Tasks
from database.user_repository import UserRepository


class TasksRepository:

    @staticmethod
    async def create(telegram_id: int, text: str, deadline: datetime, priority: int) -> Tasks:
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

    @staticmethod
    async def get_all_by_user(telegram_id: int) -> List[Tasks]:
        """Получить все задачи пользователя"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return []

            result = await session.execute(
                select(Tasks)
                .where(Tasks.user_id == user.id)
                .order_by(Tasks.priority.desc(), Tasks.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_today_tasks(telegram_id: int) -> List[Tasks]:
        """Получить задачи на сегодня"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return []

            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.user_id == user.id,
                    Tasks.deadline >= start_of_day,
                    Tasks.deadline <= end_of_day
                ))
                .order_by(Tasks.priority.desc(), Tasks.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_week_tasks(telegram_id: int) -> List[Tasks]:
        """Получить задачи на неделю"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return []

            # Получаем задачи на ближайшие 7 дней
            today = date.today()
            start_of_week = datetime.combine(today, datetime.min.time())
            end_of_week = datetime.combine(today + timedelta(days=7), datetime.max.time())

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.user_id == user.id,
                    Tasks.deadline >= start_of_week,
                    Tasks.deadline <= end_of_week
                ))
                .order_by(Tasks.priority.desc(), Tasks.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_priority(telegram_id: int, priority: int) -> List[Tasks]:
        """Получить задачи по приоритету"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return []

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.user_id == user.id,
                    Tasks.priority == priority
                ))
                .order_by(Tasks.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(task_id: int, telegram_id: int) -> Optional[Tasks]:
        """Получить задачу по ID для конкретного пользователя"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return None

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.id == task_id,
                    Tasks.user_id == user.id
                ))
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update_status(task_id: int, telegram_id: int, status: int) -> bool:
        """Обновить статус задачи"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return False

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.id == task_id,
                    Tasks.user_id == user.id
                ))
            )
            task = result.scalar_one_or_none()
            if task:
                task.status = status
                await session.commit()
                return True
            return False

    @staticmethod
    async def update_task(task_id: int, telegram_id: int, text: str = None,
                         deadline: datetime = None, priority: int = None) -> bool:
        """Обновить задачу"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return False

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.id == task_id,
                    Tasks.user_id == user.id
                ))
            )
            task = result.scalar_one_or_none()
            if task:
                if text is not None:
                    task.text = text
                if deadline is not None:
                    task.deadline = deadline
                if priority is not None:
                    task.priority = priority
                await session.commit()
                return True
            return False

    @staticmethod
    async def delete_task(task_id: int, telegram_id: int) -> bool:
        """Удалить задачу"""
        async with get_db_session() as session:
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                return False

            result = await session.execute(
                select(Tasks)
                .where(and_(
                    Tasks.id == task_id,
                    Tasks.user_id == user.id
                ))
            )
            task = result.scalar_one_or_none()
            if task:
                await session.delete(task)
                await session.commit()
                return True
            return False
