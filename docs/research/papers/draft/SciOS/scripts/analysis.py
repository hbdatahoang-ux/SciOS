"""
analysis.py
Script to perform statistical analysis and model evaluation.

Usage:
    python analysis.py
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

# Paths
DATA_PATH = "../datasets/processed/validation_set.csv"

def evaluate_models():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Giả sử dataset có các cột: Model, y_true, y_pred
    models = df["Model"].unique()

    results = []
    for model in models:
        subset = df[df["Model"] == model]
        y_true = subset["y_true"]
        y_pred = subset["y_pred"]

        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="weighted")
        cm = confusion_matrix(y_true, y_pred)

        results.append({
            "Model": model,
            "Accuracy": acc,
            "F1_Score": f1,
            "Confusion_Matrix": cm.tolist()
        })

    return results

if __name__ == "__main__":
    analysis_results = evaluate_models()
    for res in analysis_results:
        print(f"Model: {res['Model']}")
        print(f"  Accuracy: {res['Accuracy']:.3f}")
        print(f"  F1 Score: {res['F1_Score']:.3f}")
        print(f"  Confusion Matrix: {res['Confusion_Matrix']}")
        print("-" * 40)
