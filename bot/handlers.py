import numpy as np
from aiogram import Router, F
from aiogram.types import (Message, CallbackQuery,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.filters import Command
from database.queries import (add_user, get_user_id,
                              add_rating, build_rating_matrix, get_tool_by_id,
                              get_unrated_tool, get_user_rating_count)
from core.svd_algorithm import SVDRecommender
from bot.keyboards import get_rating_keyboard


router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐ Оценить инструменты")],
        [KeyboardButton(text="🎯 Получить рекомендацию")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)


@router.message(Command("start"))
async def command_start_handler(message: Message):
    """Обработка команды /start. Приветствие и регистрация пользователя."""
    if message.from_user:
        await add_user(message.from_user.id)
    else:
        await message.answer("Не удалось определить отправителя.")
        return

    welcome_text = (
        "Привет! Это система рекомендаций IT-инструментов.\n"
        "Чтобы алгоритм сингулярного разложения (SVD) смог подобрать для тебя"
        " интересный инструмент, нужно узнать твои предпочтения.\n\n"
        "Используй кнопки внизу экрана 👇"
    )
    await message.answer(welcome_text, reply_markup=main_keyboard)


@router.message(Command("rate"))
@router.message(F.text == "⭐ Оценить инструменты")
async def command_rate_handler(message: Message):
    if not message.from_user:
        return

    user_internal_id = await get_user_id(message.from_user.id)
    if not user_internal_id:
        await message.answer("Пожалуйста, сначала нажми /start")
        return

    # Проверяем прогресс
    rating_count = await get_user_rating_count(user_internal_id)

    if rating_count >= 15:
        prefix = (
            "✅ <b>Ты оценил уже достаточно инструментов!</b>\n"
            "Можешь нажимать «🎯 Получить рекомендацию» или продолжить:\n\n"
        )
    else:
        prefix = (
            f"📊 <i>Прогресс: {rating_count}/15 "
            f"(минимум для точного результата)</i>\n\n"
        )

    tool = await get_unrated_tool(user_internal_id)
    if not tool:
        await message.answer("Ты оценил абсолютно все инструменты в базе.")
        return

    tool_id, name, category = tool
    text = prefix + (
        f"Оцени инструмент от 1 (ужасно) до 5 (отлично).\n"
        f"Если не работал с ним — жми «Пропустить».\n\n"
        f"📌 <b>{name}</b>\n"
        f"📂 <i>{category}</i>"
    )

    await message.answer(
        text, reply_markup=get_rating_keyboard(tool_id), parse_mode="HTML")


@router.callback_query(F.data.startswith("rate_"))
async def process_rating_button(callback: CallbackQuery):
    if not callback.data:
        return

    parts = callback.data.split("_")
    tool_id = int(parts[1])
    score = int(parts[2])

    user_internal_id = await get_user_id(callback.from_user.id)
    if not user_internal_id:
        await callback.answer(
            "Пожалуйста, сначала отправь /start", show_alert=True)
        return

    await add_rating(user_id=user_internal_id, tool_id=tool_id, score=score)

    if isinstance(callback.message, Message):
        original_text = callback.message.html_text
        if score == 0:
            await callback.answer("Инструмент пропущен")
            await callback.message.edit_text(
                f"{original_text}\n\n🤷‍♂️ <b>ПРОПУЩЕНО</b>", parse_mode="HTML")
        else:
            await callback.answer(f"Оценка {score} сохранена!")
            await callback.message.edit_text(
                f"{original_text}\n\n✅ <b>ОЦЕНЕНО НА {score} ⭐</b>",
                parse_mode="HTML")


@router.message(Command("recommend"))
@router.message(F.text == "🎯 Получить рекомендацию")
async def command_recommend_handler(message: Message):
    if not message.from_user:
        return

    user_internal_id = await get_user_id(message.from_user.id)
    if not user_internal_id:
        await message.answer("Пожалуйста, сначала нажми /start")
        return

    matrix = await build_rating_matrix()
    if matrix is None or matrix.shape[0] < 2:
        await message.answer("В базе данных пока недостаточно информации.")
        return

    if user_internal_id >= matrix.shape[0]:
        await message.answer("Ты пока не оценил ни одного инструмента!")
        return

    user_original_ratings = matrix[user_internal_id]
    if np.max(user_original_ratings) == 0:
        await message.answer("Ты  не поставил ни одной оценки! Оцени хотя "
                             "бы 2-3 технологии, чтобы алгоритм заработал.")
        return

    await message.answer("Запускаю алгоритм малорангового приближения...")

    recommender = SVDRecommender(k_factors=3)
    predicted_matrix = recommender.fit_predict(matrix)

    user_predicted_ratings = predicted_matrix[user_internal_id]

    best_tool_id = -1
    highest_score = -1.0

    for tool_index in range(1, len(user_original_ratings)):
        if user_original_ratings[tool_index] == 0:
            if user_predicted_ratings[tool_index] > highest_score:
                highest_score = user_predicted_ratings[tool_index]
                best_tool_id = tool_index

    if best_tool_id != -1:
        tool_data = await get_tool_by_id(best_tool_id)
        if tool_data:
            name, category, description = tool_data
            result_text = (
                f"🎯 <b>Тебе может подойти инструмент:</b>\n\n"
                f"📌 <b>Название:</b> {name}\n"
                f"📂 <b>Категория:</b> {category}\n"
                f"💡 <b>Описание:</b> {description}\n\n"
                f"📊 <i>Предсказанная оценка: {highest_score:.2f} / 5.00</i>"
            )
            await message.answer(result_text, parse_mode="HTML")
    else:
        await message.answer("Кажется, ты уже оценил все инструменты!")
