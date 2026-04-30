import asyncio
import logging

from aiogram import Bot, Dispatcher
from bot.handlers import router
from database.connection import init_db

from configuration import BOT_TOKEN


async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_router(router)

    logging.info("Бот запущен и готов к работе!")

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
