"""
SciOS Time-Series Change Analysis Tool
=======================================

Deterministic time-series change evidence for SciOS.

Python 3.11+
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .base import Tool


__all__ = [
    "TimeSeriesChangeTool",
]


class TimeSeriesChangeTool(Tool):
    """Analyze a single-value time series and detect significant changes."""

    NAME = "time_series_change"
    DESCRIPTION = (
        "Analyze a time series and detect significant changes "
        "using deterministic delta-based IQR evidence."
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

        required_columns = {"timestamp", "value"}

        if not required_columns.issubset(dataframe.columns):
            raise ValueError(
                "Time-series CSV must contain 'timestamp' and 'value' columns."
            )

        timestamps = pd.to_datetime(
            dataframe["timestamp"],
            errors="raise",
        )

        values = pd.to_numeric(
            dataframe["value"],
            errors="coerce",
        )

        if timestamps.duplicated().any():
            raise ValueError(
                "Time-series CSV contains duplicate timestamps."
            )

        ordered = (
            pd.DataFrame(
                {
                    "timestamp": timestamps,
                    "value": values,
                }
            )
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        transitions: list[dict[str, Any]] = []
        deltas: list[float] = []

        for index in range(1, len(ordered)):
            previous_value = ordered.at[index - 1, "value"]
            value = ordered.at[index, "value"]

            if pd.isna(previous_value) or pd.isna(value):
                continue

            previous_timestamp = ordered.at[
                index - 1, "timestamp"
            ]
            timestamp = ordered.at[index, "timestamp"]

            delta = float(value - previous_value)
            absolute_delta = abs(delta)

            if delta > 0:
                direction = "increase"
            elif delta < 0:
                direction = "decrease"
            else:
                direction = "unchanged"

            if previous_value == 0:
                relative_change = None
            else:
                relative_change = float(
                    delta / abs(previous_value)
                )

            transitions.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "previous_timestamp": (
                        previous_timestamp.isoformat()
                    ),
                    "previous_value": float(previous_value),
                    "value": float(value),
                    "delta": delta,
                    "absolute_delta": absolute_delta,
                    "relative_change": relative_change,
                    "direction": direction,
                }
            )

            deltas.append(absolute_delta)

        if deltas:
            absolute_delta_series = pd.Series(
                deltas,
                dtype="float64",
            )

            q1 = float(
                absolute_delta_series.quantile(
                    0.25,
                    interpolation="linear",
                )
            )

            q3 = float(
                absolute_delta_series.quantile(
                    0.75,
                    interpolation="linear",
                )
            )

            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
        else:
            q1 = None
            q3 = None
            iqr = None
            upper_bound = None

        evidenced_transitions: list[dict[str, Any]] = []

        for transition in transitions:
            significant = (
                transition["absolute_delta"] > upper_bound
                if upper_bound is not None
                else False
            )

            evidenced_transition = {
                **transition,
                "significant_change": significant,
                "q1_delta": q1,
                "q3_delta": q3,
                "iqr_delta": iqr,
                "upper_delta_bound": upper_bound,
                "rule": "IQR_DELTA",
            }

            evidenced_transitions.append(
                evidenced_transition
            )

        changes = [
            transition
            for transition in evidenced_transitions
            if transition["significant_change"]
        ]

        return {
            "rows": int(len(dataframe)),
            "columns": int(len(dataframe.columns)),
            "column_names": list(dataframe.columns),
            "timestamp_column": "timestamp",
            "value_column": "value",
            "time_start": (
                ordered["timestamp"].iloc[0].isoformat()
                if not ordered.empty
                else None
            ),
            "time_end": (
                ordered["timestamp"].iloc[-1].isoformat()
                if not ordered.empty
                else None
            ),
            "q1_delta": q1,
            "q3_delta": q3,
            "iqr_delta": iqr,
            "upper_delta_bound": upper_bound,
            "transitions": evidenced_transitions,
            "changes": changes,
        }
