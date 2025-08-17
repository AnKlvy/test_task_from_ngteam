"""
Обработчики настроек пользователя
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.timezone_utils import get_available_timezones, get_timezone_display_name
from database.user_repository import UserRepository
from settings.keyboards import get_settings_kb, get_timezone_selection_kb
from main.main_kb import get_main_menu_kb

router = Router()


class SettingsStates(StatesGroup):
    main = State()
    timezone_selection = State()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    """Показать меню настроек"""
    await state.clear()
    
    # Получаем текущие настройки пользователя
    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    current_timezone_display = get_timezone_display_name(user.tz)
    
    text = (
        "⚙️ **Настройки**\n\n"
        f"👤 **Пользователь:** {user.username or 'Не указано'}\n"
        f"🌍 **Таймзона:** {current_timezone_display}\n\n"
        "Выберите настройку для изменения:"
    )
    
    # Проверяем, есть ли у объекта метод edit_text (CallbackQuery) или это Message
    if hasattr(callback, 'message') and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            text=text,
            reply_markup=get_settings_kb(),
            parse_mode="Markdown"
        )
    else:
        # Это обычное сообщение
        await callback.answer(
            text=text,
            reply_markup=get_settings_kb(),
            parse_mode="Markdown"
        )
    
    await state.set_state(SettingsStates.main)


@router.callback_query(F.data == "change_timezone")
async def show_timezone_selection(callback: CallbackQuery, state: FSMContext):
    """Показать выбор таймзоны"""
    available_timezones = get_available_timezones()
    
    text = (
        "🌍 **Выбор таймзоны**\n\n"
        "Выберите вашу таймзону из списка ниже.\n"
        "Это поможет корректно отображать время дедлайнов:"
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_timezone_selection_kb(available_timezones),
        parse_mode="Markdown"
    )
    
    await state.set_state(SettingsStates.timezone_selection)


@router.callback_query(F.data.startswith("set_timezone_"))
async def set_timezone(callback: CallbackQuery, state: FSMContext):
    """Установить выбранную таймзону"""
    timezone = callback.data.replace("set_timezone_", "")
    
    # Обновляем таймзону пользователя
    success = await UserRepository.update_timezone(callback.from_user.id, timezone)
    
    if success:
        timezone_display = get_timezone_display_name(timezone)
        await callback.answer(f"✅ Таймзона изменена на {timezone_display}", show_alert=True)
        
        # Возвращаемся к настройкам
        await show_settings(callback, state)
    else:
        await callback.answer("❌ Ошибка при обновлении таймзоны", show_alert=True)


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Вернуться к настройкам"""
    await show_settings(callback, state)
