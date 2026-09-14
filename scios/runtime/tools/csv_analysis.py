"""
SciOS CSV Analysis Tool
=======================

Deterministic CSV dataset analysis for SciOS AI productization.

Python 3.11+
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .base import Tool


__all__ = [
    "CSVAnalysisTool",
]


class CSVAnalysisTool(Tool):
    """Analyze a CSV dataset and detect basic numeric outliers."""

    NAME = "csv_analysis"
    DESCRIPTION = (
        "Analyze a CSV dataset and detect basic numeric outliers."
    )
    VERSION = "0.1.0"

    def validate(self, **kwargs: Any) -> bool:
        file_path = kwargs.get("file_path")

        return (
            isinstance(file_path, str)
            and bool(file_path.strip())
        )

    def schema(self) -> dict[str, Any]:
        return {
            "required": ["file_path"],
            "properties": {
                "file_path": {
                    "type": "string",
                },
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        file_path = kwargs["file_path"]
        path = Path(file_path)

        dataframe = pd.read_csv(path)

        missing = {
            column: int(dataframe[column].isna().sum())
            for column in dataframe.columns
        }

        numeric = dataframe.select_dtypes(
            include="number"
        )

        numeric_summary: dict[str, dict[str, Any]] = {}

        for column in numeric.columns:
            series = numeric[column].dropna()

            numeric_summary[column] = {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
            }

        outliers: dict[str, dict[str, Any]] = {}

        for column in numeric.columns:
            series = numeric[column].dropna()

            if series.empty:
                indices: list[int] = []
            else:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1

                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                mask = (
                    (dataframe[column] < lower)
                    | (dataframe[column] > upper)
                )

                indices = [
                    int(index)
                    for index in dataframe.index[mask]
                ]

            outliers[column] = {
                "count": len(indices),
                "indices": indices,
            }

        return {
            "rows": int(len(dataframe)),
            "columns": int(len(dataframe.columns)),
            "column_names": list(dataframe.columns),
            "missing": missing,
            "numeric_summary": numeric_summary,
            "outliers": outliers,
        }
