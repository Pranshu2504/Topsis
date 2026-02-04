import numpy as np
import pandas as pd

def run_topsis(df, weights, impacts):
    data = df.iloc[:, 1:].select_dtypes(include=[np.number])

    num_criteria = data.shape[1]

    if len(weights) != num_criteria or len(impacts) != num_criteria:
        raise ValueError(
            f"Number of weights ({len(weights)}) and impacts ({len(impacts)}) "
            f"must match number of numeric criteria columns ({num_criteria})"
        )

    matrix = data.values
    rss = np.sqrt(np.sum(matrix ** 2, axis=0))

    if (rss == 0).any():
        raise ValueError("One or more criteria columns have zero variance")

    normalized = matrix / rss
    weighted = normalized * weights

    ideal_best = []
    ideal_worst = []

    for i in range(num_criteria):
        if impacts[i] == "+":
            ideal_best.append(weighted[:, i].max())
            ideal_worst.append(weighted[:, i].min())
        else:
            ideal_best.append(weighted[:, i].min())
            ideal_worst.append(weighted[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    s_plus = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    s_minus = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    score = s_minus / (s_plus + s_minus)

    df["Topsis Score"] = score
    df["Rank"] = df["Topsis Score"].rank(ascending=False, method="min").astype(int)

    return df
