import aiosqlite
import numpy as np
from database.connection import DB_NAME


async def add_user(tg_id: int):
    """Добавляет нового пользователя по его Telegram ID."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (tg_id) VALUES (?)', (tg_id,))
        await db.commit()


async def get_user_id(tg_id: int) -> int:
    """Получает внутренний ID пользователя в базе."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT id FROM users WHERE tg_id = ?',
                              (tg_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None


async def add_rating(user_id: int, tool_id: int, score: int):
    """Сохраняет оценку инструмента (от 1 до 5)."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Используем REPLACE, чтобы пользователь мог изменить оценку
        await db.execute('''
            INSERT OR REPLACE INTO ratings (user_id, tool_id, score)
            VALUES (?, ?, ?)
        ''', (user_id, tool_id, score))
        await db.commit()


async def build_rating_matrix():
    """
    Самая важная функция для связи с ядром SVD!
    Выгружает все оценки и строит двумерную матрицу (numpy array).
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # Узнаем размерности матрицы (кол-во пользователей и инструментов)
        async with db.execute('SELECT MAX(id) FROM users') as cursor:
            max_user_id = (await cursor.fetchone())[0] or 0

        async with db.execute('SELECT MAX(id) FROM tools') as cursor:
            max_tool_id = (await cursor.fetchone())[0] or 0

        if max_user_id == 0 or max_tool_id == 0:
            return None  # База пуста

        # Создаем матрицу, заполненную нулями
        # (размер: пользователи x инструменты)
        matrix = np.zeros((max_user_id + 1, max_tool_id + 1), dtype=float)

        # Заполняем матрицу реальными оценками
        async with db.execute(
            'SELECT user_id, tool_id, score FROM ratings'
                              ) as cursor:
            async for row in cursor:
                u_id, t_id, score = row
                matrix[u_id, t_id] = score

        return matrix
