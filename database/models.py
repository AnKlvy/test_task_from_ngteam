"""
Модели SQLAlchemy для базы данных
"""
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Table, UniqueConstraint, Boolean, Index
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    tz = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(String(4096), nullable=False)
    deadline = Column(String(255))
    priority = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

# tasks
# id (PK)
# user_id (FK → users.id)
# text
# deadline (nullable)
# priority (int: 1, 2, 3)
# status (0 — активна, 1 — выполнена)
# created_at