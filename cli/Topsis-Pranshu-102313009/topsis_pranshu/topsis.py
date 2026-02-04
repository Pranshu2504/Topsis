import sys
import os
import pandas as pd
import numpy as np

def error(msg):
    print(f"Error: {msg}")
    sys.exit(1)

def main():
    if len(sys.argv) != 5:
        error("Wrong number of parameters. Usage: python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>")

    input_file = sys.argv[1]
    weights_str = sys.argv[2]
    impacts_str = sys.argv[3]
    output_file = sys.argv[4]

    if not os.path.exists(input_file):
        error(f"The file '{input_file}' was not found.")

    try:
        if input_file.lower().endswith(".csv"):
            df = pd.read_csv(input_file)
        elif input_file.lower().endswith(".xlsx") or input_file.lower().endswith(".xls"):
            df = pd.read_excel(input_file)
        else:
            error("Unsupported file format. Use .csv or .xlsx")
    except Exception as e:
        error(f"Error reading file: {e}")

    if df.shape[1] < 3:
        error("Input file must contain three or more columns.")

    data_df = df.iloc[:, 1:].copy()

    try:
        data_df = data_df.apply(pd.to_numeric)
    except:
        error("From 2nd to last columns must contain numeric values only.")

    if data_df.isnull().values.any():
        error("Input data contains non-numeric or missing values.")

    try:
        weights = [float(w) for w in weights_str.split(",")]
        impacts = impacts_str.split(",")
    except:
        error("Weights must be numeric and impacts must be comma-separated.")

    num_cols = data_df.shape[1]

    if len(weights) != num_cols or len(impacts) != num_cols:
        error("Number of weights, impacts and criteria columns must be the same.")

    if not all(i in ["+", "-"] for i in impacts):
        error("Impacts must be either '+' or '-'.")

    matrix = data_df.values
    rss = np.sqrt(np.sum(matrix ** 2, axis=0))

    if (rss == 0).any():
        error("Normalization failed due to zero variance column.")

    normalized_matrix = matrix / rss
    weighted_matrix = normalized_matrix * weights

    ideal_best = []
    ideal_worst = []

    for i in range(num_cols):
        if impacts[i] == "+":
            ideal_best.append(np.max(weighted_matrix[:, i]))
            ideal_worst.append(np.min(weighted_matrix[:, i]))
        else:
            ideal_best.append(np.min(weighted_matrix[:, i]))
            ideal_worst.append(np.max(weighted_matrix[:, i]))

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    s_plus = np.sqrt(np.sum((weighted_matrix - ideal_best) ** 2, axis=1))
    s_minus = np.sqrt(np.sum((weighted_matrix - ideal_worst) ** 2, axis=1))

    total_dist = s_plus + s_minus
    performance_score = np.divide(s_minus, total_dist, out=np.zeros_like(s_minus), where=total_dist != 0)

    df["Topsis Score"] = performance_score
    df["Rank"] = df["Topsis Score"].rank(ascending=False, method="min").astype(int)

    df.to_csv(output_file, index=False)
    print(f"Success: Result saved to {output_file}")

if __name__ == "__main__":
    main()
