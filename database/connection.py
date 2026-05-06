import aiosqlite
import logging
import os

DB_NAME = "bot_database.db"
SQL_FILE = os.path.join("database", "init_database.sql")


async def init_db():
    """
    Создает таблицы в базе данных и автоматически заполняет их,
    если они пустые.
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

            if count[0] == 0:
                logging.info(
                    "Таблица инструментов пуста. Начинаю загрузку базы...")

                if os.path.exists(SQL_FILE):
                    with open(SQL_FILE, "r", encoding="utf-8") as file:
                        sql_script = file.read()
                        await db.executescript(sql_script)
                    logging.info(
                        "База данных автоматически заполнена.")
                else:
                    logging.error(
                        f"Ошибка: Файл {SQL_FILE} не найден! Заполнения нет.")

        await db.commit()
        logging.info("База данных успешно инициализирована и готова к работе.")
