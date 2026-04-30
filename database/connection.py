import aiosqlite
import logging
import os

DB_NAME = "bot_database.db"


async def init_db():
    """
    Создает таблицы в базе данных и заполняет их, если они пустые.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS developer_tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS tool_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tool_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tool_id) REFERENCES developer_tools(id),
                UNIQUE(user_id, tool_id)
            )
        ''')

        async with db.execute(
                'SELECT COUNT(*) FROM developer_tools') as cursor:
            count = await cursor.fetchone()

            if count[0] == 0 and os.path.exists("init_database.sql"):
                with open("init_database.sql", "r", encoding="utf-8") as file:
                    sql_script = file.read()
                    await db.executescript(sql_script)
                logging.info(
                    "База данных автоматически заполнена!")

        await db.commit()
        logging.info("База данных успешно инициализирована.")
