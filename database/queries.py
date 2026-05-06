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
        await db.execute('''
            INSERT OR REPLACE INTO tool_ratings (user_id, tool_id, score)
            VALUES (?, ?, ?)
        ''', (user_id, tool_id, score))
        await db.commit()


async def build_rating_matrix():
    """
    Выгружает все оценки и строит двумерную матрицу (numpy array).
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT MAX(id) FROM users') as cursor:
            max_user_id = (await cursor.fetchone())[0] or 0

        async with db.execute('SELECT MAX(id) FROM developer_tools') as cursor:
            max_tool_id = (await cursor.fetchone())[0] or 0

        if max_user_id == 0 or max_tool_id == 0:
            return None

        matrix = np.zeros((max_user_id + 1, max_tool_id + 1), dtype=float)

        async with db.execute(
            'SELECT user_id, tool_id, score FROM tool_ratings'
        ) as cursor:
            async for row in cursor:
                u_id, t_id, score = row
                matrix[u_id, t_id] = score

        return matrix


async def get_tool_by_id(tool_id: int):
    """Возвращает название, категорию и описание инструмента по его ID."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT name, category, description FROM developer_tools WHERE id = ?',
            (tool_id,)
        ) as cursor:
            return await cursor.fetchone()


async def get_unrated_tool(user_id: int):
    """
    Возвращает один случайный инструмент, который пользователь еще не оценил.
    Если все инструменты оценены, возвращает None.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT id, name, category 
            FROM developer_tools 
            WHERE id NOT IN (
                SELECT tool_id FROM tool_ratings WHERE user_id = ?
            )
            ORDER BY RANDOM() LIMIT 1
        ''', (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_user_rating_count(user_id: int) -> int:
    """Считает, сколько инструментов пользователь оценил (оценка > 0)."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT COUNT(*) FROM tool_ratings WHERE user_id = ? AND score > 0', 
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
