"""
generate_tables.py
Script to generate tables for the paper from datasets.

Usage:
    python generate_tables.py
"""

import pandas as pd
import os

# Paths
DATA_PATH = "../datasets/processed/training_set.csv"
OUTPUT_DIR = "../tables/"

def generate_performance_table():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Giả sử dataset có các cột: Model, Accuracy, F1_Score, Parameters, Training_Time
    table = df[["Model", "Accuracy", "F1_Score", "Parameters", "Training_Time"]]

    # Save table as CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "T-0001.csv")
    table.to_csv(output_file, index=False)
    print(f"Table saved to {output_file} - generate_tables.py:27")

if __name__ == "__main__":
    generate_performance_table()
