from typing import List

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.utils import get_priority_text
from database.tasks_repository import TasksRepository
from database.models import Tasks
from tasks.keyboards.list_tasks import (
    get_filters_kb, get_task_actions_kb, get_tasks_list_kb,
    get_confirm_delete_kb
)
from tasks.keyboards.edit_task import get_edit_task_kb

router = Router()


def get_status_text(status: int) -> str:
    """Получить текстовое представление статуса"""
    return "✅ Выполнена" if status == 1 else "⏳ Активна"


def format_task_info(task: Tasks) -> str:
    """Форматировать информацию о задаче"""
    priority_text = get_priority_text(task.priority)
    status_text = get_status_text(task.status)

    # Форматируем дедлайн
    deadline_text = "Не установлен"
    if task.deadline:
        deadline_text = task.deadline.strftime('%d.%m.%Y в %H:%M')

    text = f"📋 **Задача #{task.id}**\n\n"
    text += f"📝 **Текст:** {task.text}\n"
    text += f"📅 **Дедлайн:** {deadline_text}\n"
    text += f"⚡ **Приоритет:** {priority_text}\n"
    text += f"📊 **Статус:** {status_text}\n"
    text += f"🕐 **Создана:** {task.created_at.strftime('%d.%m.%Y %H:%M')}"

    return text


def format_tasks_list(tasks: List[Tasks], filter_name: str = "Все задачи") -> str:
    """Форматировать список задач"""
    if not tasks:
        return f"📋 **{filter_name}**\n\n❌ Задач не найдено"
    
    text = f"📋 **{filter_name}** (найдено: {len(tasks)})\n\n"
    text += "Выберите задачу для просмотра:"
    
    return text


@router.callback_query(F.data == "list_tasks")
async def show_tasks_list(callback: CallbackQuery, state: FSMContext):
    """Показать список всех задач"""
    await state.clear()
    
    tasks = await TasksRepository.get_all_by_user(callback.from_user.id)
    
    text = format_tasks_list(tasks, "Все задачи")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "show_filters")
async def show_filters(callback: CallbackQuery):
    """Показать фильтры"""
    text = "🎛 **Фильтры задач**\n\nВыберите фильтр для отображения задач:"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_filters_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "filter_all")
async def filter_all_tasks(callback: CallbackQuery):
    """Фильтр: все задачи"""
    tasks = await TasksRepository.get_all_by_user(callback.from_user.id)
    text = format_tasks_list(tasks, "Все задачи")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "filter_today")
async def filter_today_tasks(callback: CallbackQuery):
    """Фильтр: задачи на сегодня"""
    tasks = await TasksRepository.get_today_tasks(callback.from_user.id)
    text = format_tasks_list(tasks, "Задачи на сегодня")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "filter_week")
async def filter_week_tasks(callback: CallbackQuery):
    """Фильтр: задачи на неделю"""
    tasks = await TasksRepository.get_week_tasks(callback.from_user.id)
    text = format_tasks_list(tasks, "Задачи на неделю")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("filter_priority_"))
async def filter_priority_tasks(callback: CallbackQuery):
    """Фильтр: задачи по приоритету"""
    priority = int(callback.data.split("_")[-1])
    tasks = await TasksRepository.get_by_priority(callback.from_user.id, priority)
    
    priority_names = {1: "Низкий приоритет", 2: "Средний приоритет", 3: "Высокий приоритет"}
    filter_name = priority_names.get(priority, "Неизвестный приоритет")
    
    text = format_tasks_list(tasks, filter_name)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("view_task_"))
async def view_task(callback: CallbackQuery):
    """Просмотр конкретной задачи"""
    task_id = int(callback.data.split("_")[-1])
    task = await TasksRepository.get_by_id(task_id, callback.from_user.id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    text = format_task_info(task)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_task_actions_kb(task_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task(callback: CallbackQuery):
    """Отметить задачу как выполненную"""
    task_id = int(callback.data.split("_")[-1])
    
    success = await TasksRepository.update_status(task_id, callback.from_user.id, 1)
    
    if success:
        await callback.answer("✅ Задача отмечена как выполненная!", show_alert=True)
        # Обновляем отображение задачи
        task = await TasksRepository.get_by_id(task_id, callback.from_user.id)
        if task:
            text = format_task_info(task)
            await callback.message.edit_text(
                text=text,
                reply_markup=get_task_actions_kb(task_id),
                parse_mode="Markdown"
            )
    else:
        await callback.answer("❌ Ошибка при обновлении задачи", show_alert=True)


@router.callback_query(F.data.startswith("edit_task_"))
async def edit_task_menu(callback: CallbackQuery):
    """Меню редактирования задачи"""
    task_id = int(callback.data.split("_")[-1])
    task = await TasksRepository.get_by_id(task_id, callback.from_user.id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    # Форматируем дедлайн
    deadline_text = "Не установлен"
    if task.deadline:
        deadline_text = task.deadline.strftime('%d.%m.%Y в %H:%M')

    text = f"✏️ **Редактирование задачи #{task_id}**\n\n"
    text += f"📝 **Текущий текст:** {task.text}\n"
    text += f"📅 **Текущий дедлайн:** {deadline_text}\n"
    text += f"⚡ **Текущий приоритет:** {get_priority_text(task.priority)}\n\n"
    text += "Выберите, что хотите изменить:"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_edit_task_kb(task_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task_confirm(callback: CallbackQuery):
    """Подтверждение удаления задачи"""
    task_id = int(callback.data.split("_")[-1])
    task = await TasksRepository.get_by_id(task_id, callback.from_user.id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    text = f"🗑 **Удаление задачи #{task_id}**\n\n"
    text += f"📝 **Текст:** {task.text[:100]}{'...' if len(task.text) > 100 else ''}\n\n"
    text += "⚠️ **Вы уверены, что хотите удалить эту задачу?**\n"
    text += "Это действие нельзя отменить."
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_confirm_delete_kb(task_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_task(callback: CallbackQuery):
    """Подтвердить удаление задачи"""
    task_id = int(callback.data.split("_")[-1])
    
    success = await TasksRepository.delete_task(task_id, callback.from_user.id)
    
    if success:
        await callback.answer("🗑 Задача успешно удалена!", show_alert=True)
        # Возвращаемся к списку задач
        tasks = await TasksRepository.get_all_by_user(callback.from_user.id)
        text = format_tasks_list(tasks, "Все задачи")
        
        await callback.message.edit_text(
            text=text,
            reply_markup=get_tasks_list_kb(tasks),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Ошибка при удалении задачи", show_alert=True)


@router.callback_query(F.data == "refresh_tasks")
async def refresh_tasks(callback: CallbackQuery):
    """Обновить список задач"""
    tasks = await TasksRepository.get_all_by_user(callback.from_user.id)
    text = format_tasks_list(tasks, "Все задачи")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_tasks_list_kb(tasks),
        parse_mode="Markdown"
    )
    
    await callback.answer("🔄 Список обновлен!")


