"""
export.py
Script to export figures and tables into publication-ready formats.

Usage:
    python export.py
"""

import os
import shutil
import pandas as pd

# Paths
FIGURES_DIR = "../figures/"
TABLES_DIR = "../tables/"
EXPORT_DIR = "../review/export/"

def export_figures():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    figures = [f for f in os.listdir(FIGURES_DIR) if f.endswith((".png", ".jpg", ".pdf"))]
    for fig in figures:
        src = os.path.join(FIGURES_DIR, fig)
        dst = os.path.join(EXPORT_DIR, fig)
        shutil.copy(src, dst)
    print(f"Exported {len(figures)} figures to {EXPORT_DIR}")

def export_tables():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    tables = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
    for tbl in tables:
        src = os.path.join(TABLES_DIR, tbl)
        dst = os.path.join(EXPORT_DIR, tbl)
        shutil.copy(src, dst)

        # Optional: also export to Excel for submission
        df = pd.read_csv(src)
        excel_file = os.path.join(EXPORT_DIR, tbl.replace(".csv", ".xlsx"))
        df.to_excel(excel_file, index=False)
    print(f"Exported {len(tables)} tables to {EXPORT_DIR}")

if __name__ == "__main__":
    export_figures()
    export_tables()
