"""Pure chart-data preparation from the exact uploaded CSV bytes."""
from __future__ import annotations

import hashlib
from io import BytesIO

import numpy as np
import pandas as pd


def chart_data(raw_bytes: bytes, report: dict, column: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return histogram, row-index series with IQR bounds, and outlier rows.

    Quartiles and bounds are read from existing SciOS evidence, not recomputed.
    """
    if hashlib.sha256(raw_bytes).hexdigest() != report["dataset"]["sha256"]:
        raise ValueError("Uploaded CSV differs from the analyzed dataset.")
    if column not in report["result"]["outliers"]:
        raise ValueError("Column is not part of the analysis.")
    frame = pd.read_csv(BytesIO(raw_bytes))
    if column not in frame or not pd.api.types.is_numeric_dtype(frame[column]):
        raise ValueError("Select a numeric column.")
    values = frame[column].dropna().astype(float)
    values = values[np.isfinite(values)]
    if values.empty:
        return (pd.DataFrame(columns=["bin_center", "count"]),
                pd.DataFrame(columns=["value", "lower_bound", "upper_bound"]),
                pd.DataFrame(columns=["row_index", "value", "lower_bound", "upper_bound"]))
    n_bins = min(30, max(1, int(np.sqrt(len(values)))))
    counts, edges = np.histogram(values, bins=n_bins)
    histogram = pd.DataFrame({
        "bin_center": (edges[:-1] + edges[1:]) / 2,
        "count": counts,
    })
    evidence = report["result"]["outliers"][column]["evidence"]
    if evidence:
        lower = float(evidence[0]["lower_bound"])
        upper = float(evidence[0]["upper_bound"])
    else:
        # Without outliers the report contains no quartile/bound evidence.
        # Do not invent thresholds; the histogram remains valid.
        lower = upper = float("nan")
    series = pd.DataFrame({
        "value": frame[column].astype(float),
        "lower_bound": lower,
        "upper_bound": upper,
    })
    series.index.name = "row_index"
    outliers = pd.DataFrame(evidence, columns=[
        "index", "value", "q1", "q3", "iqr", "lower_bound", "upper_bound", "rule"
    ]).rename(columns={"index": "row_index"})
    return histogram, series, outliers
