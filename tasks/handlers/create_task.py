import logging
from datetime import date, timedelta, time

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.utils import get_priority_text
from database.tasks_repository import TasksRepository
from main.main_kb import get_menu_kb
from tasks.keyboards.create_task import confirm_create_kb, choose_priority_kb
from aiogramx import Calendar

from aiogramx.time_selector import TimeSelectorModern

router = Router()

class CreateTaskStates(StatesGroup):
    enter_text = State()
    select_time = State()
    enter_priority = State()
    confirm = State()
    create_task= State()


@router.callback_query(F.data == "create_task")
async def enter_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введите текст задачи",
    )
    await state.set_state(CreateTaskStates.enter_text)

@router.message(CreateTaskStates.enter_text)
async def select_date(message: Message, state: FSMContext):
    logging.info(f"create select_date: message={message.text}, state={await state.get_state()}")

    # Сохраняем текст задачи
    await state.update_data(text=message.text)

    async def on_select(cq: CallbackQuery, date_obj: date):
        # Сохраняем выбранную дату и переходим к выбору времени
        await state.update_data(selected_date=date_obj)
        await select_time(cq, state)

    async def on_back(cq: CallbackQuery):
        await cq.message.edit_text(text="Canceled", reply_markup=get_menu_kb())

    c = Calendar(
        max_range=timedelta(weeks=12),
        show_quick_buttons=True,
        on_select=on_select,
        on_back=on_back,
    )
    await message.answer(
        text="Выберите дату дедлайна:",
        reply_markup=c.render_kb()
    )

async def select_time(callback: CallbackQuery, state: FSMContext):
    logging.info(f"create select_time: message={callback.data}, state={await state.get_state()}")

    async def on_select(c: CallbackQuery, time_obj: time):
        # Получаем сохраненную дату и создаем datetime объект
        data = await state.get_data()
        selected_date = data.get("selected_date")

        if selected_date:
            from datetime import datetime
            deadline_datetime = datetime.combine(selected_date, time_obj)
            await state.update_data(deadline_datetime=deadline_datetime)

        await enter_priority(c, state)

    async def on_back(c: CallbackQuery):
        await c.message.edit_text(text="Operation Canceled")
        await c.answer()

    ts_modern = TimeSelectorModern(
        carry_over=True,
        on_select=on_select,
        on_back=on_back,
        lang=callback.from_user.language_code,
    )

    await callback.message.edit_text(
        text="Выберите время дедлайна:",
        reply_markup=ts_modern.render_kb(offset_minutes=5),
    )

    await state.set_state(CreateTaskStates.select_time)


async def enter_priority(callback: CallbackQuery, state: FSMContext):
    logging.info(f"create enter_priority: callback={callback.data}, state={await state.get_state()}")

    await state.set_state(CreateTaskStates.enter_priority)
    await callback.message.edit_text(
        text="Выберите приоритет задачи",
        reply_markup=choose_priority_kb()
    )


@router.callback_query(CreateTaskStates.enter_priority, F.data.startswith("create_priority_"))
async def confirm(callback: CallbackQuery, state: FSMContext):
    priority = int(callback.data.replace("create_priority_", ""))
    priority_text = get_priority_text(priority)
    logging.info(f"create confirm: callback={callback.data}, state={await state.get_state()}")

    data = await state.get_data()
    text = data.get("text")
    deadline_datetime = data.get("deadline_datetime")
    await state.update_data(priority=priority)

    # Форматируем дату и время для отображения
    deadline_str = deadline_datetime.strftime("%d.%m.%Y в %H:%M")

    await callback.message.edit_text(
        text=(f"📝 Создать задачу: {text[:50]}\n"
              f"📅 Дедлайн: {deadline_str}\n"
              f"🎯 Приоритет: {priority_text}"),
        reply_markup=confirm_create_kb()
    )

    await state.set_state(CreateTaskStates.confirm)


@router.callback_query(CreateTaskStates.confirm, F.data.startswith("confirm_create_"))
async def create_task(callback: CallbackQuery, state: FSMContext):
    logging.info(f"create create_task: callback={callback.data}, state={await state.get_state()}")

    is_confirm = callback.data.replace("confirm_create_", "") == "1"
    if not is_confirm:
        answer_text = "❌ Создание задачи отменено"
    else:
        data = await state.get_data()
        text = data.get("text")
        deadline_datetime = data.get("deadline_datetime")
        priority = data.get("priority")
        priority_text = get_priority_text(priority)

        # Форматируем дату и время для отображения
        deadline_display = deadline_datetime.strftime("%d.%m.%Y в %H:%M")

        answer_text = (f"✅ Задача успешно создана!\n\n"
                       f"📝 {text[:50]}\n"
                       f"📅 Дедлайн: {deadline_display}\n"
                       f"🎯 Приоритет: {priority_text}")

        await TasksRepository.create(callback.from_user.id, text, deadline_datetime, int(priority))

    await callback.message.edit_text(
        text=answer_text,
        reply_markup=get_menu_kb()
    )

    await state.clear()
