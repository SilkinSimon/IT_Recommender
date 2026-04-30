from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_rating_keyboard(tool_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с оценками от 1 до 5 для конкретного инструмента.
    Данные в кнопке (callback_data) будут содержать ID инструмента и саму оценку.
    """
    builder = InlineKeyboardBuilder()

    for score in range(1, 6):
        callback_data = f"rate_{tool_id}_{score}"
        button = InlineKeyboardButton(
            text=str(score), callback_data=callback_data)
        builder.add(button)

    builder.adjust(5)
    return builder.as_markup()
