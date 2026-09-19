from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .base import Tool


class DatasetQualityTool(Tool):
    """Measure deterministic structural and integrity properties of a CSV dataset."""

    NAME = "dataset_quality"
    VERSION = "0.1.0"
    DESCRIPTION = (
        "Audit deterministic structural and integrity properties "
        "of a CSV dataset."
    )

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

    @staticmethod
    def _column_kind(series: pd.Series) -> str:
        if pd.api.types.is_bool_dtype(series):
            return "boolean"

        if pd.api.types.is_numeric_dtype(series):
            return "numeric"

        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        return "categorical/text"

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        file_path = kwargs["file_path"]
        dataframe = pd.read_csv(Path(file_path))

        rows = int(len(dataframe))
        columns = int(len(dataframe.columns))

        columns_profile: dict[str, dict[str, Any]] = {}

        for column in dataframe.columns:
            series = dataframe[column]

            missing_count = int(series.isna().sum())
            missing_fraction = (
                float(missing_count / rows)
                if rows > 0
                else 0.0
            )

            unique_count = int(series.nunique(dropna=True))

            columns_profile[str(column)] = {
                "dtype": str(series.dtype),
                "kind": self._column_kind(series),
                "missing_count": missing_count,
                "missing_fraction": missing_fraction,
                "unique_count": unique_count,
                "is_constant": unique_count <= 1,
            }

        duplicate_row_count = int(dataframe.duplicated().sum())
        duplicate_row_fraction = (
            float(duplicate_row_count / rows)
            if rows > 0
            else 0.0
        )

        return {
            "rows": rows,
            "columns": columns,
            "column_names": list(dataframe.columns),
            "columns_profile": columns_profile,
            "duplicate_rows": {
                "count": duplicate_row_count,
                "fraction": duplicate_row_fraction,
            },
        }
