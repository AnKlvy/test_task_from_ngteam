from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.user_repository import UserRepository
from main.main_kb import get_menu_kb

router = Router()

class MainStates(StatesGroup):
    main = State()

@router.message(CommandStart())
async def student_start(message: Message, state: FSMContext):

    await state.clear()
    await show_main_menu(message, state=state)


async def show_main_menu(message, state):
    keyboard = get_menu_kb()
    await UserRepository.create(message.from_user.id, message.from_user.username, 'Almaty')
    await message.answer(
        "Привет",
        reply_markup=keyboard
    )

    await state.set_state(MainStates.main)

