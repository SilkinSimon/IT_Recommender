import numpy as np
import matplotlib.pyplot as plt

from svd_algorithm import SVDRecommender

if __name__ == "__main__":
    # 1. Генерация синтетических данных 100x100
    np.random.seed(42)

    # Создаем матрицу на базе 5 паттернов
    U_true = np.random.rand(100, 5)
    V_true = np.random.rand(5, 100)
    perfect_matrix = np.dot(U_true, V_true) * 5

    # 70% оценок отсутствуют
    mask = np.random.rand(100, 100) > 0.7
    sparse_matrix = perfect_matrix * mask

    # 2. Применение алгоритма
    recommender = SVDRecommender(k_factors=5)
    predicted_matrix = recommender.fit_predict(sparse_matrix)

    print(f"Матрица 100x100. Погрешность: {recommender.error:.4f}")

    # 3. Визуализация
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Левый график - разреженные данные
    im1 = axes[0].imshow(sparse_matrix, cmap='viridis',
                         aspect='auto', vmin=0, vmax=15)
    axes[0].set_title('Разреженная матрица (шум и пропуски)')
    axes[0].set_xlabel('Инструменты')
    axes[0].set_ylabel('Пользователи')
    fig.colorbar(im1, ax=axes[0])

    # Правый график - восстановленные значения алгоритмом
    im2 = axes[1].imshow(predicted_matrix, cmap='viridis',
                         aspect='auto', vmin=0, vmax=15)
    axes[1].set_title(f'Восстановленная матрица (k={recommender.k})')
    axes[1].set_xlabel('Инструменты')
    fig.colorbar(im2, ax=axes[1])

    plt.tight_layout()
    plt.show()
