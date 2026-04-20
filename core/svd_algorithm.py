import numpy as np
import math


class SVDRecommender:
    """
    Класс для построения рекомендательной системы на основе 
    малорангового приближения матриц при помощи сингулярного разложения.
    """

    def __init__(self, k_factors):
        """
        Инициализация рекомендательной системы.

        Параметры:
        k_factors (int): Ранг матрицы приближения.
        """
        self.k = k_factors
        self.singular_values = None
        self.approximation_error = None

    def _jacobi_eigen(self, symmetric_matrix, tolerance=1e-9, max_iter=1000):
        """
        Приватный метод для вычисления собственных значений
        и собственных векторов
        симметричной матрицы методом вращений Якоби.
        """
        n = symmetric_matrix.shape[0]
        V = symmetric_matrix.copy()
        eigenvectors = np.eye(n)

        for iter in range(max_iter):
            # Поиск максимального внедиагонального элемента
            max_val = 0.0
            p, q = 0, 0
            for i in range(n):
                for j in range(i + 1, n):
                    if abs(V[i, j]) > max_val:
                        max_val = abs(V[i, j])
                        p, q = i, j

            if max_val < tolerance:
                break

            # Вычисление угла поворота
            if V[p, p] == V[q, q]:
                theta = math.pi / 4.0 if V[p, q] > 0 else -math.pi / 4.0
            else:
                theta = 0.5 * math.atan(2.0 * V[p, q] / (V[p, p] - V[q, q]))

            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)

            # Вращение
            V_pp = cos_theta**2 * V[p, p] - 2.0 * sin_theta * \
                cos_theta * V[p, q] + sin_theta**2 * V[q, q]
            V_qq = sin_theta**2 * V[p, p] + 2.0 * sin_theta * \
                cos_theta * V[p, q] + cos_theta**2 * V[q, q]

            V[p, q] = V[q, p] = 0.0

            for k in range(n):
                if k != p and k != q:
                    V_kp = cos_theta * V[k, p] - sin_theta * V[k, q]
                    V_kq = sin_theta * V[k, p] + cos_theta * V[k, q]
                    V[k, p] = V[p, k] = V_kp
                    V[k, q] = V[q, k] = V_kq

            V[p, p] = V_pp
            V[q, q] = V_qq

            for k in range(n):
                e_kp = cos_theta * \
                    eigenvectors[k, p] - sin_theta * eigenvectors[k, q]
                e_kq = sin_theta * \
                    eigenvectors[k, p] + cos_theta * eigenvectors[k, q]
                eigenvectors[k, p] = e_kp
                eigenvectors[k, q] = e_kq

        # Сортировка собственных значений и векторов по убыванию
        eigenvalues = np.diag(V)
        sorted_indices = np.argsort(eigenvalues)[::-1]

        return eigenvalues[sorted_indices], eigenvectors[:, sorted_indices]

    def fit_predict(self, source_matrix):
        """
        Главный метод. Принимает разреженную матрицу оценок,
        вычисляет малоранговое приближение
        и возвращает плотную матрицу с предсказаниями.
        """
        m, n = source_matrix.shape

        # 1. Переход к симметричной матрице A^T * A
        ATA = np.dot(source_matrix.T, source_matrix)

        # 2. Поиск собственных векторов
        # (правые сингулярные вектора e) и значений
        eigenvalues, E = self._jacobi_eigen(ATA)

        # 3. Вычисление сингулярных чисел
        self.singular_values = np.sqrt(np.maximum(eigenvalues, 0))

        # Оценка теоретической погрешности
        # (первое отброшенное сингулярное число)
        if len(self.singular_values) > self.k:
            self.approximation_error = self.singular_values[self.k]
        else:
            self.approximation_error = 0.0

        # 4. Сборка малорангового приближения (тензорное представление)
        predicted_matrix = np.zeros((m, n))
        k_actual = min(self.k, np.sum(self.singular_values > 1e-10))

        for j in range(k_actual):
            sigma_j = self.singular_values[j]
            e_j = E[:, j]

            # Вычисление левого сингулярного вектора q
            q_j = np.dot(source_matrix, e_j) / sigma_j

            # Тензорное умножение и сложение
            predicted_matrix += sigma_j * np.outer(q_j, e_j)

        return predicted_matrix


# Пример использования класса
if __name__ == "__main__":
    # Представим, что у нас есть небольшая матрица: 4 пользователя оценили
    # 5 инструментов 0 означает, что пользователь не знает этот инструмент
    initial_ratings = np.array([
        [5, 4, 0, 0, 1],
        [4, 5, 0, 1, 0],
        [0, 0, 5, 4, 0],
        [0, 1, 4, 5, 0]
    ], dtype=float)

    print("Исходная матрица с пропусками (0):")
    print(initial_ratings)

    # Создаем экземпляр нашего класса,
    # просим оставить только 2 главных скрытых фактора
    recommender = SVDRecommender(k_factors=2)

    # Запускаем вычисления
    predicted_ratings = recommender.fit_predict(initial_ratings)

    print(f"\nВосстановленная матрица предсказаний (k={recommender.k}):")
    # Округляем до двух знаков после запятой для красоты
    print(np.round(predicted_ratings, 2))

    print(f"\nСингулярные числа: {np.round(recommender.singular_values, 2)}")
    print(
        f"Теорет погрешн аппроксимации: {recommender.approximation_error:.2f}")
