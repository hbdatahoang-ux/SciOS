from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "data" / "real_workflow" / "time_series"


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURE_DIR / name)


def _ordered_numeric_series(name: str) -> pd.DataFrame:
    frame = _read_csv(name)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame.sort_values("timestamp").reset_index(drop=True)


def _oracle(name: str) -> dict:
    frame = _ordered_numeric_series(name)

    deltas = []
    transitions = []

    for index in range(1, len(frame)):
        previous = frame.iloc[index - 1]
        current = frame.iloc[index]

        if pd.isna(previous["value"]) or pd.isna(current["value"]):
            continue

        delta = float(current["value"] - previous["value"])
        absolute_delta = abs(delta)

        if delta > 0:
            direction = "increase"
        elif delta < 0:
            direction = "decrease"
        else:
            direction = "unchanged"

        if previous["value"] == 0:
            relative_change = None
        else:
            relative_change = delta / abs(float(previous["value"]))

        deltas.append(absolute_delta)

        transitions.append(
            {
                "timestamp": current["timestamp"],
                "previous_timestamp": previous["timestamp"],
                "previous_value": float(previous["value"]),
                "value": float(current["value"]),
                "delta": delta,
                "absolute_delta": absolute_delta,
                "relative_change": relative_change,
                "direction": direction,
            }
        )

    if not deltas:
        return {
            "q1_delta": None,
            "q3_delta": None,
            "iqr_delta": None,
            "upper_delta_bound": None,
            "transitions": transitions,
            "significant": [],
        }

    absolute_delta_series = pd.Series(deltas, dtype="float64")

    q1 = float(absolute_delta_series.quantile(0.25, interpolation="linear"))
    q3 = float(absolute_delta_series.quantile(0.75, interpolation="linear"))
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr

    significant = [
        transition
        for transition in transitions
        if transition["absolute_delta"] > upper_bound
    ]

    return {
        "q1_delta": q1,
        "q3_delta": q3,
        "iqr_delta": iqr,
        "upper_delta_bound": upper_bound,
        "transitions": transitions,
        "significant": significant,
    }


def test_stable_series_oracle():
    result = _oracle("stable.csv")

    assert result["q1_delta"] == pytest.approx(1.0)
    assert result["q3_delta"] == pytest.approx(1.5)
    assert result["iqr_delta"] == pytest.approx(0.5)
    assert result["upper_delta_bound"] == pytest.approx(2.25)

    assert result["significant"] == []


def test_sudden_change_oracle():
    result = _oracle("sudden_change.csv")

    assert result["q1_delta"] == pytest.approx(1.0)
    assert result["q3_delta"] == pytest.approx(1.0)
    assert result["iqr_delta"] == pytest.approx(0.0)
    assert result["upper_delta_bound"] == pytest.approx(1.0)

    assert len(result["significant"]) == 1

    change = result["significant"][0]

    assert change["previous_value"] == pytest.approx(105.0)
    assert change["value"] == pytest.approx(125.0)
    assert change["delta"] == pytest.approx(20.0)
    assert change["absolute_delta"] == pytest.approx(20.0)
    assert change["relative_change"] == pytest.approx(20 / 105)
    assert change["direction"] == "increase"


def test_multiple_changes_oracle():
    result = _oracle("multiple_changes.csv")

    assert result["q1_delta"] == pytest.approx(1.0)
    assert result["q3_delta"] == pytest.approx(3.25)
    assert result["iqr_delta"] == pytest.approx(2.25)
    assert result["upper_delta_bound"] == pytest.approx(6.625)

    significant = result["significant"]

    assert len(significant) == 3

    assert [item["delta"] for item in significant] == [
        pytest.approx(10.0),
        pytest.approx(-10.0),
        pytest.approx(15.0),
    ]

    assert [item["direction"] for item in significant] == [
        "increase",
        "decrease",
        "increase",
    ]


def test_unsorted_timestamps_are_ordered_before_transition_calculation():
    result = _oracle("unsorted.csv")

    transitions = result["transitions"]

    assert [
        (item["previous_value"], item["value"], item["delta"])
        for item in transitions
    ] == [
        (100.0, 101.0, 1.0),
        (101.0, 103.0, 2.0),
    ]


def test_zero_baseline_has_no_relative_change():
    result = _oracle("zero_baseline.csv")

    first = result["transitions"][0]
    second = result["transitions"][1]

    assert first["delta"] == pytest.approx(10.0)
    assert first["relative_change"] is None

    assert second["delta"] == pytest.approx(1.0)
    assert second["relative_change"] == pytest.approx(0.1)


def test_missing_value_does_not_create_cross_gap_transition():
    result = _oracle("missing_value.csv")

    assert result["transitions"] == []
    assert result["significant"] == []


def test_duplicate_timestamp_is_rejected():
    frame = _read_csv("duplicate_timestamp.csv")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")

    assert frame["timestamp"].duplicated().any()

    with pytest.raises(AssertionError, match="duplicate timestamp"):
        assert not frame["timestamp"].duplicated().any(), (
            "duplicate timestamp"
        )
