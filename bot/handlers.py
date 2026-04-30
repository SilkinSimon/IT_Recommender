import numpy as np
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.queries import (add_user, get_user_id,
                              add_rating, build_rating_matrix)
from core.svd_algorithm import SVDRecommender
from bot.keyboards import get_rating_keyboard


router = Router()


@router.message(Command("start"))
async def command_start_handler(message: Message):
    """Обработка команды /start. Приветствие и регистрация пользователя."""

    if message.from_user:
        await add_user(message.from_user.id)
    else:
        await message.answer("Не удалось определить отправителя.")

    welcome_text = (
        "Это система рекомендаций профессиональных инструментов.\n"
        "Чтобы алгоритм смог подобрать для тебя идеальный "
        "инструмент, необходимо узнать твои предпочтения.\n\n"
        "Используй команду /rate, чтобы оценить несколько технологий, "
        "а затем нажми /recommend для получения результата."
    )
    await message.answer(welcome_text)


@router.message(Command("recommend"))
async def command_recommend_handler(message: Message):
    """
    Главная функция. 
    Выгружает матрицу, запускает математику и выдает результат.
    """
    if message.from_user:
        user_internal_id = await get_user_id(message.from_user.id)
    else:
        await message.answer("Не удалось определить отправителя.")

    if not user_internal_id:
        await message.answer("Пожалуйста, сначала нажми /start")
        return

    matrix = await build_rating_matrix()
    if matrix is None or matrix.shape[0] < 2:
        await message.answer(
            "В базе данных пока недостаточно информации для вычислений."
        )
        return

    await message.answer("Запускаю алгоритм малорангового приближения...")

    recommender = SVDRecommender(k_factors=3)

    predicted_matrix = recommender.fit_predict(matrix)

    user_original_ratings = matrix[user_internal_id]
    user_predicted_ratings = predicted_matrix[user_internal_id]

    best_tool_id = -1
    highest_score = -1.0

    for tool_index in range(1, len(user_original_ratings)):
        if user_original_ratings[tool_index] == 0:
            if user_predicted_ratings[tool_index] > highest_score:
                highest_score = user_predicted_ratings[tool_index]
                best_tool_id = tool_index

    if best_tool_id != -1:
        await message.answer(
            f"Математика подсказывает, что тебе определенно стоит попробовать "
            f"инструмент под номером {best_tool_id}! "
            f"Предсказанная оценка: {highest_score:.2f} из 5.00"
        )
    else:
        await message.answer(
            "Уже оценены все доступные инструменты в базе данных"
        )


@router.callback_query(F.data.startswith("rate_"))
async def process_rating_button(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку с оценкой.
    """
    if not callback.data:
        await callback.answer("Некорректный запрос")
        return
    parts = callback.data.split("_")
    tool_id = int(parts[1])
    score = int(parts[2])

    user_internal_id = await get_user_id(callback.from_user.id)

    if not user_internal_id:
        await callback.answer(
            "Пожалуйста, сначала отправь команду /start", show_alert=True
            )
        return

    await add_rating(user_id=user_internal_id, tool_id=tool_id, score=score)

    await callback.answer(f"Оценка {score} успешно сохранена!")

    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)
