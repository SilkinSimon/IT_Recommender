import numpy as np

from svd_algorithm import SVDRecommender

if __name__ == "__main__":
    np.set_printoptions(precision=2, suppress=True)

    A = np.array([
        [5.0, 5.0, 0.0, 0.0, 1.0],
        [4.0, 5.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 5.0, 4.0, 5.0],
        [1.0, 0.0, 4.0, 5.0, 4.0]
    ])

    print("1. ИСХОДНАЯ РАЗРЕЖЕННАЯ МАТРИЦА")
    print(A)
    print("\n")

    k_factors = 2
    recommender = SVDRecommender(k_factors=k_factors)

    predicted_A = recommender.fit_predict(A)

    print(f"2. ЗАПУСК АЛГОРИТМА (Сжатие до k={k_factors})")
    print("Вычисленные сингулярные числа (Sigma):")
    print(recommender.singular_values)

    print(f"\nТеоретическая погрешность: {recommender.error:.4f}")
    print("\n")

    print("3. ВОССТАНОВЛЕННАЯ МАТРИЦА")
    print(predicted_A)
