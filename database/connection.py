import aiosqlite
import logging

DB_NAME = "bot_database.db"


async def init_db():
    """
    Создает таблицы в базе данных, если они еще не существуют.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица пользователей (сохраняем Telegram ID)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL
            )
        ''')

        # Таблица инструментов (Linux, Python, Docker и т.д.)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Таблица оценок (Связь: кто, что и на сколько оценил)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER,
                tool_id INTEGER,
                score INTEGER NOT NULL,
                PRIMARY KEY (user_id, tool_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tool_id) REFERENCES tools(id)
            )
        ''')

        await db.commit()
        logging.info("База данных успешно инициализирована.")
