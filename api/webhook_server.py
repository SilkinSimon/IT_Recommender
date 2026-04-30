from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types

from configuration import BOT_TOKEN
from bot.handlers import router
from database.connection import init_db


WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"

# ВНИМАНИЕ: Сюда нужно будет вписать реальный адрес твоего будущего сервера,
# который ты купишь или настроишь (например, https://my-recommender-domain.com)
SERVER_URL = "https://домен.ру"

# Инициализируем бота и диспетчер
if BOT_TOKEN:
    bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Функция управляет жизненным циклом сервера:
    код до 'yield' выполняется при старте, код после 'yield' — при выключении.
    """
    await init_db()

    webhook_url = f"{SERVER_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url)
    print(f"Вебхук успешно установлен на адрес: {webhook_url}")

    yield

    await bot.delete_webhook()
    await bot.session.close()
    print("Вебхук удален, сервер корректно остановлен.")

app = FastAPI(title="Рекомендательная система SVD", lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """
    Главная точка входа. Сюда серверы Telegram будут присылать 
    все сообщения пользователей в формате JSON.
    """
    update_data = await request.json()

    update = types.Update(**update_data)

    await dispatcher.feed_update(bot=bot, update=update)

    return {"status": "ok"}
