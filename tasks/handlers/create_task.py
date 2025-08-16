import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.tasks_repository import TasksRepository
from database.user_repository import UserRepository
from main.main_kb import get_menu_kb
from tasks.keyboards.create_task import choose_priority_kb, confirm_create_kb

router = Router()

class CreateTaskStates(StatesGroup):
    enter_text = State()
    enter_deadline = State()
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
async def enter_deadline(message: Message, state: FSMContext):
    text = message.text.strip()
    await state.update_data(text=text)
    await message.answer(
        text="Введите дедлайн",
    )

    await state.set_state(CreateTaskStates.enter_deadline)

@router.message(CreateTaskStates.enter_deadline)
async def enter_priority(message: Message, state: FSMContext):
    logging.info(f"create enter_priority: callback={message.text}, state={await state.get_state()}")

    deadline = message.text.strip()
    await state.update_data(deadline=deadline)
    await state.set_state(CreateTaskStates.enter_priority)
    await message.answer(
        text="Выберите приоритет задачи",
        reply_markup=choose_priority_kb()
    )


@router.callback_query(CreateTaskStates.enter_priority, F.data.startswith("create_priority_"))
async def confirm(callback: CallbackQuery, state: FSMContext):
    priority = int(callback.data.replace("create_priority_", ""))
    priority_text = await get_priority(priority)
    logging.info(f"create confirm: callback={callback.data}, state={await state.get_state()}")


    data = await state.get_data()
    text= data.get("text")
    deadline = data.get("deadline")
    await state.update_data(priority=priority)

    await callback.message.edit_text(
        text=(f"Создать задачу: {text[:50]}\n"
                       f"Дедлайн: {deadline}\n"
                       f"Приоритет: {priority_text}"),
        reply_markup=confirm_create_kb()
    )

    await state.set_state(CreateTaskStates.confirm)


async def get_priority(priority):
    if priority == 1:
        priority_text = "Низкий"
    elif priority == 2:
        priority_text = "Средний"
    else:
        priority_text = "Высокий"
    return priority_text


@router.callback_query(CreateTaskStates.confirm, F.data.startswith("confirm_create_"))
async def create_task(callback: CallbackQuery, state: FSMContext):
    logging.info(f"create create_task: callback={callback.data}, state={await state.get_state()}")

    is_confirm = bool(callback.data.replace("confirm_create_", ""))
    if not is_confirm:
        answer_text = "Отмена создания"
    else:
        data = await state.get_data()
        text= data.get("text")
        deadline = data.get("deadline")
        priority = data.get("priority")
        priority_text = await get_priority(priority)
        answer_text = (f"Задача успешно создана! {text[:50]}\n"
                       f"Дедлайн: {deadline}\n"
                       f"Приоритет: {priority_text}")

        await TasksRepository.create(callback.from_user.id, text, deadline, int(priority))

    await callback.message.edit_text(
        text=answer_text,
        reply_markup=get_menu_kb()
    )

    await state.set_state(CreateTaskStates.confirm)