import numpy as np


def extract_optimal_values_by_column(matrix, benefit):
        # Array untuk menyimpan hasil optimal untuk setiap kolom
        optimal_values_by_column = []

        # Transpose matrix untuk mendapatkan kolom sebagai baris
        transposed_matrix = matrix.T

        # Iterasi melalui setiap kolom (sekarang sebagai baris dalam matriks yang ditranspos)
        for i, column in enumerate(transposed_matrix):
            if benefit[i]:  # Jika kolom adalah 'BENEFIT', cari nilai maksimum
                optimal_values_by_column.append(np.max(column))
            else:  # Jika kolom adalah 'COST', cari nilai minimum
                optimal_values_by_column.append(np.min(column))

        return np.array(optimal_values_by_column)  

def normalize_matrix(matrix, min_max_values, benefit):
    normalized_matrix = np.empty_like(matrix, dtype=float)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if benefit[j]:
                normalized_matrix[i, j] = matrix[i, j] / min_max_values[j]
            else:
                normalized_matrix[i, j] = min_max_values[j] / matrix[i, j]
    return normalized_matrix

def weight_normalized_matrix(normalized_matrix, weights):
    return normalized_matrix * weights
    # Mengalikan setiap kolom dalam matriks normalisasi dengan bobotnya yang bersesuaian
   

class SAW:
    def __init__(self) -> None:
        pass
     
    def start(self, m, w, b):
        weights = np.array(w)/100
        benefit = np.array(b)
        matrix = np.array(m)
        min_max_arr = extract_optimal_values_by_column(matrix, benefit)
        normalized_matrix = normalize_matrix(matrix, min_max_arr, benefit)
        weighted_normalized_matrix = weight_normalized_matrix(normalized_matrix, weights)
        final_scores = np.sum(weighted_normalized_matrix, axis=1)
        return normalized_matrix, weighted_normalized_matrix, final_scores

    