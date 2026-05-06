from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_rating_keyboard(tool_id: int) -> InlineKeyboardMarkup:
    """Создает кнопки от 1 до 5 и кнопку пропуска."""

    rating_row = []
    for i in range(1, 6):
        rating_row.append(
            InlineKeyboardButton(
                text=str(i), callback_data=f"rate_{tool_id}_{i}")
        )

    skip_row = [
        InlineKeyboardButton(text="🤷‍♂️ Не знаком (Пропустить)",
                             callback_data=f"rate_{tool_id}_0")
    ]

    return InlineKeyboardMarkup(inline_keyboard=[rating_row, skip_row])
