"""
generate_figures.py
Script to generate figures for the paper from datasets.

Usage:
    python generate_figures.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
DATA_PATH = "../datasets/processed/training_set.csv"
OUTPUT_DIR = "../figures/"

def generate_accuracy_plot():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Assume dataset has columns: Model, Accuracy
    plt.figure(figsize=(8, 6))
    plt.bar(df["Model"], df["Accuracy"], color="skyblue")
    plt.title("Model Accuracy Comparison")
    plt.xlabel("Model")
    plt.ylabel("Accuracy")
    plt.ylim(0, 1)

    # Save figure
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "accuracy_comparison.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Figure saved to {output_file}")

if __name__ == "__main__":
    generate_accuracy_plot()
