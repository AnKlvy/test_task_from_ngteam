from datetime import datetime, date, timedelta, time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from database.tasks_repository import TasksRepository
from tasks.handlers.list_tasks import format_task_info
from tasks.keyboards.list_tasks import get_task_actions_kb
from tasks.keyboards.edit_task import get_edit_priority_kb
from aiogramx import Calendar
from aiogramx.time_selector import TimeSelectorModern

class EditTaskStates(StatesGroup):
    edit_text = State()
    edit_deadline = State()
    select_date = State()
    select_time = State()

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
    await state.set_state(EditTaskStates.select_date)

    async def on_select(cq: CallbackQuery, date_obj: date):
        # Сохраняем выбранную дату и переходим к выбору времени
        await state.update_data(selected_date=date_obj)
        await select_time_edit(cq, state)

    async def on_back(cq: CallbackQuery):
        # Возвращаемся к меню редактирования задачи
        task_id = (await state.get_data()).get("edit_task_id")
        await cq.message.edit_text(text="Редактирование отменено")
        await state.clear()

    c = Calendar(
        max_range=timedelta(weeks=12),
        show_quick_buttons=True,
        on_select=on_select,
        on_back=on_back,
    )
    await callback.message.edit_text(
        text="📅 Выберите новую дату дедлайна:",
        reply_markup=c.render_kb()
    )


async def select_time_edit(callback: CallbackQuery, state: FSMContext):
    """Выбор времени для редактирования дедлайна"""

    async def on_select(c: CallbackQuery, time_obj: time):
        # Получаем сохраненную дату и создаем datetime объект
        data = await state.get_data()
        selected_date = data.get("selected_date")
        task_id = data.get("edit_task_id")

        if selected_date:
            deadline_datetime = datetime.combine(selected_date, time_obj)

            # Сохраняем новый дедлайн в базе данных
            success = await TasksRepository.update_task(task_id, c.from_user.id, deadline=deadline_datetime)

            if success:
                await state.clear()
                await c.message.edit_text("✅ Дедлайн задачи успешно обновлен!")

                # Показываем обновленную задачу
                task = await TasksRepository.get_by_id(task_id, c.from_user.id)
                if task:
                    text = format_task_info(task)
                    await c.message.answer(
                        text=text,
                        reply_markup=get_task_actions_kb(task_id),
                        parse_mode="Markdown"
                    )
            else:
                await c.message.edit_text("❌ Ошибка при обновлении задачи")
                await state.clear()

    async def on_back(c: CallbackQuery):
        await c.message.edit_text("Редактирование отменено")
        await state.clear()

    ts_modern = TimeSelectorModern(
        carry_over=True,
        on_select=on_select,
        on_back=on_back,
        lang=callback.from_user.language_code,
    )

    await callback.message.edit_text(
        text="🕐 Выберите новое время дедлайна:",
        reply_markup=ts_modern.render_kb(offset_minutes=5),
    )

    await state.set_state(EditTaskStates.select_time)


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
