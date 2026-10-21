from pathlib import Path

import pandas as pd
import pytest


FIXTURE_DIR = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "real_workflow"
    / "dataset_quality"
)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _column_kind(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    return "categorical/text"


def _oracle(path: Path) -> dict[str, object]:
    dataframe = _read_csv(path)

    rows = int(len(dataframe))
    columns = int(len(dataframe.columns))

    columns_profile: dict[str, dict[str, object]] = {}

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
            "kind": _column_kind(series),
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


def test_complete_quality_profile():
    result = _oracle(
        FIXTURE_DIR / "complete.csv"
    )

    assert result["rows"] == 5
    assert result["columns"] == 4
    assert result["column_names"] == [
        "id",
        "age",
        "group",
        "active",
    ]

    profile = result["columns_profile"]

    assert profile["id"]["kind"] == "numeric"
    assert profile["age"]["kind"] == "numeric"
    assert profile["group"]["kind"] == "categorical/text"
    assert profile["active"]["kind"] == "boolean"

    assert profile["id"]["missing_count"] == 0
    assert profile["age"]["missing_count"] == 0
    assert profile["group"]["missing_count"] == 0
    assert profile["active"]["missing_count"] == 0

    assert profile["id"]["unique_count"] == 5
    assert profile["age"]["unique_count"] == 5
    assert profile["group"]["unique_count"] == 2
    assert profile["active"]["unique_count"] == 2

    assert profile["id"]["is_constant"] is False
    assert profile["age"]["is_constant"] is False
    assert profile["group"]["is_constant"] is False
    assert profile["active"]["is_constant"] is False

    assert result["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_missing_values():
    result = _oracle(
        FIXTURE_DIR / "missing.csv"
    )

    assert result["rows"] == 5

    profile = result["columns_profile"]

    assert profile["age"]["missing_count"] == 2
    assert profile["age"]["missing_fraction"] == pytest.approx(0.4)

    assert profile["group"]["missing_count"] == 1
    assert profile["group"]["missing_fraction"] == pytest.approx(0.2)

    assert profile["id"]["missing_count"] == 0
    assert profile["id"]["missing_fraction"] == 0.0


def test_duplicate_rows():
    result = _oracle(
        FIXTURE_DIR / "duplicates.csv"
    )

    duplicate_rows = result["duplicate_rows"]

    assert duplicate_rows["count"] == 2
    assert duplicate_rows["fraction"] == pytest.approx(0.4)


def test_constant_columns():
    result = _oracle(
        FIXTURE_DIR / "constant.csv"
    )

    profile = result["columns_profile"]

    assert profile["constant"]["unique_count"] == 1
    assert profile["constant"]["is_constant"] is True

    assert profile["variable"]["unique_count"] == 4
    assert profile["variable"]["is_constant"] is False


def test_mixed_column_types():
    result = _oracle(
        FIXTURE_DIR / "mixed_types.csv"
    )

    profile = result["columns_profile"]

    assert profile["number"]["kind"] == "numeric"
    assert profile["flag"]["kind"] == "boolean"
    assert profile["label"]["kind"] == "categorical/text"


def test_empty_dataset():
    result = _oracle(
        FIXTURE_DIR / "empty.csv"
    )

    assert result["rows"] == 0
    assert result["columns"] == 3

    profile = result["columns_profile"]

    for column in ("id", "value", "label"):
        assert profile[column]["missing_count"] == 0
        assert profile[column]["missing_fraction"] == 0.0
        assert profile[column]["unique_count"] == 0
        assert profile[column]["is_constant"] is True

    assert result["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_quality_findings_are_measurement_based():
    result = _oracle(
        FIXTURE_DIR / "quality_findings.csv"
    )

    profile = result["columns_profile"]

    assert profile["value"]["missing_count"] == 2
    assert profile["value"]["missing_fraction"] == pytest.approx(0.5)

    assert profile["constant"]["is_constant"] is True

    assert result["duplicate_rows"]["count"] == 1
    assert result["duplicate_rows"]["fraction"] == pytest.approx(0.25)
