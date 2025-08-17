from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from database.tasks_repository import TasksRepository
from tasks.handlers.list_tasks import format_task_info
from tasks.keyboards.list_tasks import get_task_actions_kb
from tasks.keyboards.edit_task import get_edit_priority_kb

class EditTaskStates(StatesGroup):
    edit_text = State()
    edit_deadline = State()

router = Router()

@router.callback_query(F.data.startswith("edit_text_"))
async def edit_task_text(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование текста задачи"""
    task_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_task_id=task_id)
    await state.set_state(EditTaskStates.edit_text)

    text = "✏️ **Редактирование текста задачи**\n\n"
    text += "Введите новый текст задачи:"

    await callback.message.edit_text(text=text, parse_mode="Markdown")


@router.message(EditTaskStates.edit_text)
async def save_task_text(message: Message, state: FSMContext):
    """Сохранить новый текст задачи"""
    data = await state.get_data()
    task_id = data.get("edit_task_id")
    new_text = message.text.strip()

    if not new_text:
        await message.answer("❌ Текст задачи не может быть пустым. Попробуйте еще раз:")
        return

    success = await TasksRepository.update_task(task_id, message.from_user.id, text=new_text)

    if success:
        await state.clear()
        await message.answer("✅ Текст задачи успешно обновлен!")

        # Показываем обновленную задачу
        task = await TasksRepository.get_by_id(task_id, message.from_user.id)
        if task:
            text = format_task_info(task)
            await message.answer(
                text=text,
                reply_markup=get_task_actions_kb(task_id),
                parse_mode="Markdown"
            )
    else:
        await message.answer("❌ Ошибка при обновлении задачи")


@router.callback_query(F.data.startswith("edit_deadline_"))
async def edit_task_deadline(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование дедлайна задачи"""
    task_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_task_id=task_id)
    await state.set_state(EditTaskStates.edit_deadline)

    text = "📅 **Редактирование дедлайна задачи**\n\n"
    text += "Введите новый дедлайн в формате: **дд.мм.гггг чч:мм**\n"
    text += "Например: 25.12.2024 15:30"

    await callback.message.edit_text(text=text, parse_mode="Markdown")


@router.message(EditTaskStates.edit_deadline)
async def save_task_deadline(message: Message, state: FSMContext):
    """Сохранить новый дедлайн задачи"""
    data = await state.get_data()
    task_id = data.get("edit_task_id")
    new_deadline_str = message.text.strip()

    try:
        # Пытаемся парсить дату в формате "дд.мм.гггг чч:мм"
        new_deadline = datetime.strptime(new_deadline_str, "%d.%m.%Y %H:%M")

        success = await TasksRepository.update_task(task_id, message.from_user.id, deadline=new_deadline)

        if success:
            await state.clear()
            await message.answer("✅ Дедлайн задачи успешно обновлен!")

            # Показываем обновленную задачу
            task = await TasksRepository.get_by_id(task_id, message.from_user.id)
            if task:
                text = format_task_info(task)
                await message.answer(
                    text=text,
                    reply_markup=get_task_actions_kb(task_id),
                    parse_mode="Markdown"
                )
        else:
            await message.answer("❌ Ошибка при обновлении задачи")
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты!\n\n"
            "Используйте формат: **дд.мм.гггг чч:мм**\n"
            "Например: 25.12.2024 15:30\n\n"
            "Попробуйте еще раз:",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("edit_priority_"))
async def edit_task_priority(callback: CallbackQuery):
    """Показать меню выбора приоритета"""
    task_id = int(callback.data.split("_")[-1])

    text = "⚡ **Выбор приоритета задачи**\n\n"
    text += "Выберите новый приоритет:"

    await callback.message.edit_text(
        text=text,
        reply_markup=get_edit_priority_kb(task_id),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("set_priority_"))
async def set_task_priority(callback: CallbackQuery):
    """Установить новый приоритет задачи"""
    parts = callback.data.split("_")
    task_id = int(parts[2])
    priority = int(parts[3])

    success = await TasksRepository.update_task(task_id, callback.from_user.id, priority=priority)

    if success:
        await callback.answer("✅ Приоритет задачи обновлен!", show_alert=True)

        # Показываем обновленную задачу
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
