from typing import Union, Optional, Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup


async def safe_edit_or_send(
    query: Union[CallbackQuery, Message],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    set_state: Optional[Any] = None,
    state: Optional[FSMContext] = None
) -> None:
    """
    Универсальная функция для безопасной отправки/редактирования сообщений

    Args:
        query: CallbackQuery или Message объект
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        set_state: Состояние для установки (опционально)
        state: FSM контекст (опционально)
    """
    try:
        if set_state is not None and state is not None:
            await state.set_state(set_state)

        parse_mode = await choose_parse_mode(text)

        if isinstance(query, CallbackQuery):
            await query.message.edit_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        elif isinstance(query, Message):
            await query.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            raise ValueError("safe_edit_or_send: query must be CallbackQuery or Message")

    except Exception as e:
        await handle_telegram_bad_request(query, e, text, reply_markup)


async def handle_telegram_bad_request(
    query: Union[CallbackQuery, Message],
    exception: Exception,
    fallback_text: Optional[str] = None,
    fallback_markup: Optional[InlineKeyboardMarkup] = None
) -> None:
    """
    Универсальная обработка ошибок TelegramBadRequest

    Args:
        query: CallbackQuery или Message объект
        exception: Исключение для обработки
        fallback_text: Текст для отправки в случае ошибки
        fallback_markup: Клавиатура для отправки в случае ошибки
    """
    exception_str = str(exception)

    if isinstance(exception, TelegramBadRequest):
        if "message can't be edited" in exception_str:
            text = fallback_text or "Информация обновлена."
            parse_mode = await choose_parse_mode(text)

            if isinstance(query, CallbackQuery):
                await query.message.bot.send_message(
                    chat_id=query.message.chat.id,
                    text=text,
                    reply_markup=fallback_markup,
                    parse_mode=parse_mode
                )
            elif isinstance(query, Message):
                await query.answer(
                    text,
                    reply_markup=fallback_markup,
                    parse_mode=parse_mode
                )
        elif "can't parse entities" in exception_str or "Unsupported start tag" in exception_str:
            text = fallback_text or "Информация обновлена."

            if isinstance(query, CallbackQuery):
                await query.message.edit_text(text=text, reply_markup=fallback_markup)
            elif isinstance(query, Message):
                await query.answer(text, reply_markup=fallback_markup)
        else:
            raise exception
    else:
        raise exception


async def choose_parse_mode(text):
    use_html = "<b>" in text or "<i>" in text or "<code>" in text or "<pre>" in text or "<a>" in text
    use_markdown = "[" in text and "](" in text and ")" in text
    if use_html:
        parse_mode = "HTML"
    elif use_markdown:
        parse_mode = "Markdown"
    else:
        parse_mode = None
    return parse_mode


def get_priority_text(priority: int) -> str:
    """Получить текстовое представление приоритета"""
    priority_map = {1: "🟢 Низкий", 2: "🟡 Средний", 3: "🔴 Высокий"}
    return priority_map.get(priority, "Неизвестный")
