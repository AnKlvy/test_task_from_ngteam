from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from database.models import Tasks


def get_filters_kb() -> InlineKeyboardMarkup:
    """Клавиатура фильтров для списка задач"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Все", callback_data="filter_all")],
        [InlineKeyboardButton(text="📅 На сегодня", callback_data="filter_today")],
        [InlineKeyboardButton(text="📆 На неделю", callback_data="filter_week")],
        [InlineKeyboardButton(text="🔴 Высокий приоритет", callback_data="filter_priority_3")],
        [InlineKeyboardButton(text="🟡 Средний приоритет", callback_data="filter_priority_2")],
        [InlineKeyboardButton(text="🟢 Низкий приоритет", callback_data="filter_priority_1")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])


def get_task_actions_kb(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий для конкретной задачи"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнить", callback_data=f"complete_task_{task_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_task_{task_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_task_{task_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="list_tasks")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])


def get_tasks_list_kb(tasks: List[Tasks], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """Клавиатура со списком задач с пагинацией"""
    buttons = []
    
    # Вычисляем границы для текущей страницы
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_tasks = tasks[start_idx:end_idx]
    
    # Добавляем кнопки для задач на текущей странице
    for task in page_tasks:
        # Определяем эмодзи для приоритета
        priority_emoji = "🔴" if task.priority == 3 else "🟡" if task.priority == 2 else "🟢"
        
        # Определяем эмодзи для статуса
        status_emoji = "✅" if task.status == 1 else "⏳"
        
        # Обрезаем текст задачи для кнопки
        task_text = task.text[:30] + "..." if len(task.text) > 30 else task.text
        
        button_text = f"{status_emoji} {priority_emoji} {task_text}"
        buttons.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=f"view_task_{task.id}"
        )])
    
    # Добавляем кнопки навигации если нужно
    nav_buttons = []
    total_pages = (len(tasks) + per_page - 1) // per_page
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"tasks_page_{page-1}"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"tasks_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Добавляем кнопки управления
    buttons.extend([
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks")],
        [InlineKeyboardButton(text="🎛 Фильтры", callback_data="show_filters")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_delete_kb(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"confirm_delete_{task_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"view_task_{task_id}")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
