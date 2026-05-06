import sqlite3

DB_NAME = "bot_database.db"


def seed_dummy_data():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # 1. Добавляем 3 фейковых пользователей (передаем только их tg_id)
        users = [(101,), (102,), (103,)]
        cursor.executemany(
            'INSERT OR IGNORE INTO users (tg_id) VALUES (?)', users)

        # Получаем их внутренние ID (ключом в словаре теперь будет сам tg_id)
        cursor.execute(
            "SELECT id, tg_id FROM users WHERE tg_id IN (101, 102, 103)")
        user_map = {row[1]: row[0] for row in cursor.fetchall()}

        # 2. Функция для поиска ID инструмента по названию
        def get_tool_id(name):
            cursor.execute(
                "SELECT id FROM developer_tools WHERE name = ?", (name,))
            res = cursor.fetchone()
            return res[0] if res else None

        # 3. Создаем паттерны оценок
        ratings = []

        # Паттерн Фронтендера (tg_id = 101)
        frontend_tools = {"JavaScript": 5, "TypeScript": 5,
                          "React": 5, "Figma": 4, "Tailwind CSS": 5, "Docker": 2}
        for tool, score in frontend_tools.items():
            t_id = get_tool_id(tool)
            if t_id:
                ratings.append((user_map[101], t_id, score))

        # Паттерн Бэкендера (tg_id = 102)
        backend_tools = {"Python": 5, "PostgreSQL": 5,
                         "Docker": 4, "Redis": 5, "Django": 4, "React": 1}
        for tool, score in backend_tools.items():
            t_id = get_tool_id(tool)
            if t_id:
                ratings.append((user_map[102], t_id, score))

        # Паттерн DevOps (tg_id = 103)
        devops_tools = {"Kubernetes": 5, "Docker": 5, "Terraform": 5,
                        "Grafana": 5, "Prometheus": 5, "JavaScript": 1}
        for tool, score in devops_tools.items():
            t_id = get_tool_id(tool)
            if t_id:
                ratings.append((user_map[103], t_id, score))

        # Заливаем оценки в базу
        cursor.executemany(
            'INSERT OR REPLACE INTO tool_ratings (user_id, tool_id, score) VALUES (?, ?, ?)', ratings)
        conn.commit()
        print("✅ Синтетические пользователи успешно добавлены! Теперь SVD будет работать.")


if __name__ == "__main__":
    seed_dummy_data()
