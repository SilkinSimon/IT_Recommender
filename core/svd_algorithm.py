import numpy as np


class SVDRecommender:
    """
    Класс для построения рекомендательной системы на основе
    малорангового приближения матриц при помощи сингулярного разложения.
    """

    def __init__(self, k_factors):
        """
        Инициализация рекомендательной системы.

        Параметры:
        k_factors (int): Количество скрытых факторов (ранг приближения), 
                         которое необходимо оставить для вычислений.
        """
        self.k = k_factors
        self.singular_values = None
        self.error = None

    def fit_predict(self, source_matrix):
        """
        Вычисляет малоранговое приближение для исходной матрицы оценок.

        Параметры:
        source_matrix (numpy.ndarray): Исходная матрица с оценками.

        Возвращает:
        numpy.ndarray: Восстановленная матрица с предсказанными оценками.
        """

        m = source_matrix.shape[0]  # Количество пользователей
        n = source_matrix.shape[1]  # Количество инструментов

        symmetric_matrix = np.dot(source_matrix.T, source_matrix)

        eigenvalues, eigenvectors = np.linalg.eigh(symmetric_matrix)

        sorted_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices]

        # Вычисление сингулярных чисел
        self.singular_values = np.sqrt(np.maximum(eigenvalues, 0))

        # Оценка теоретической погрешности приближения
        if len(self.singular_values) > self.k:
            self.error = self.singular_values[self.k]
        else:
            self.error = 0.0

        predicted_matrix = np.zeros((m, n))

        # Вычисление фактического количества факторов для работы
        # (отсечение тех значений, которые практически равны нулю)
        actual_k = 0
        for value in self.singular_values:
            if value > 1e-10:
                actual_k += 1
        actual_k = min(self.k, actual_k)

        # Сборка малорангового приближения
        for j in range(actual_k):
            sigma = self.singular_values[j]
            e_vector = eigenvectors[:, j]

            # Вычисление левого сингулярного вектора
            q_vector = np.dot(source_matrix, e_vector) / sigma

            # Вычисление тензорного произведения векторов
            tensor_product = np.outer(q_vector, e_vector)

            predicted_matrix += sigma * tensor_product

        return predicted_matrix
