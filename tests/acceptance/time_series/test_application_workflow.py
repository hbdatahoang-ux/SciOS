from __future__ import annotations

from pathlib import Path

import pytest

from scios.application.time_series_analysis import TimeSeriesChangeApplication
from scios.cognitive_core.planner import Goal


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "data" / "real_workflow" / "time_series"


def _run_application(fixture_name: str) -> dict[str, object]:
    fixture = FIXTURE_DIR / fixture_name
    assert fixture.exists(), f"Missing acceptance fixture: {fixture}"

    app = TimeSeriesChangeApplication(
        file_path=str(fixture),
    )

    goal = Goal(f"Analyze time series: {fixture_name}")

    result = app.analyze(
        goal=goal,
        query=(
            f"Analyze the time series in {fixture_name} "
            "and explain significant changes."
        ),
    )

    assert isinstance(result, dict)
    return result


def _get_transitions(result: dict[str, object]) -> list[dict[str, object]]:
    assert "transitions" in result

    transitions = result["transitions"]

    assert isinstance(transitions, list)
    assert all(isinstance(item, dict) for item in transitions)

    return transitions


def _get_changes(result: dict[str, object]) -> list[dict[str, object]]:
    assert "changes" in result

    changes = result["changes"]

    assert isinstance(changes, list)
    assert all(isinstance(item, dict) for item in changes)

    return changes


def _get_explanation(result: dict[str, object]) -> str:
    assert "explanation" in result

    explanation = result["explanation"]

    assert isinstance(explanation, str)
    return explanation


def test_stable_series_workflow():
    result = _run_application("stable.csv")

    changes = _get_changes(result)

    assert changes == []

    explanation = _get_explanation(result)
    assert "No significant changes" in explanation


def test_sudden_change_workflow():
    result = _run_application("sudden_change.csv")

    changes = _get_changes(result)

    assert len(changes) == 1

    change = changes[0]

    assert change["previous_value"] == 105
    assert change["value"] == 125
    assert change["delta"] == 20
    assert change["direction"] == "increase"
    assert change["significant_change"] is True
    assert change["rule"] == "IQR_DELTA"

    explanation = _get_explanation(result)

    assert "105" in explanation
    assert "125" in explanation
    assert "20" in explanation


def test_multiple_changes_workflow():
    result = _run_application("multiple_changes.csv")

    changes = _get_changes(result)

    assert len(changes) == 3

    deltas = [change["delta"] for change in changes]
    directions = [change["direction"] for change in changes]

    assert deltas == [10, -10, 15]
    assert directions == [
        "increase",
        "decrease",
        "increase",
    ]

    assert all(
        change["significant_change"] is True
        for change in changes
    )

    assert all(
        change["rule"] == "IQR_DELTA"
        for change in changes
    )


def test_unsorted_timestamps_are_processed_chronologically():
    result = _run_application("unsorted.csv")

    transitions = _get_transitions(result)

    assert len(transitions) == 2

    assert transitions[0]["previous_value"] == 100
    assert transitions[0]["value"] == 101
    assert transitions[0]["delta"] == 1

    assert transitions[1]["previous_value"] == 101
    assert transitions[1]["value"] == 103
    assert transitions[1]["delta"] == 2

    timestamps = [
        transition["timestamp"]
        for transition in transitions
    ]

    assert timestamps == sorted(timestamps)


def test_zero_baseline_has_no_relative_change():
    result = _run_application("zero_baseline.csv")

    transitions = _get_transitions(result)

    assert len(transitions) == 2

    first = transitions[0]
    second = transitions[1]

    assert first["previous_value"] == 0
    assert first["value"] == 10
    assert first["delta"] == 10
    assert first["relative_change"] is None

    assert second["previous_value"] == 10
    assert second["value"] == 11
    assert second["delta"] == 1
    assert second["relative_change"] == pytest.approx(0.1)


def test_missing_value_does_not_create_cross_gap_transition():
    result = _run_application("missing_value.csv")

    transitions = _get_transitions(result)
    changes = _get_changes(result)

    assert transitions == []
    assert changes == []

    explanation = _get_explanation(result)
    assert "No significant changes" in explanation


def test_duplicate_timestamp_is_rejected():
    fixture = FIXTURE_DIR / "duplicate_timestamp.csv"
    assert fixture.exists()

    app = TimeSeriesChangeApplication(
        file_path=str(fixture),
    )

    goal = Goal("Analyze duplicate timestamp series")

    with pytest.raises(RuntimeError):
        app.analyze(
            goal=goal,
            query="Analyze the time series and explain significant changes.",
        )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "stable.csv",
        "sudden_change.csv",
        "multiple_changes.csv",
        "unsorted.csv",
        "zero_baseline.csv",
        "missing_value.csv",
    ],
)
def test_changes_are_subset_of_transitions(fixture_name: str):
    result = _run_application(fixture_name)

    transitions = _get_transitions(result)
    changes = _get_changes(result)

    transition_keys = {
        (
            transition["previous_timestamp"],
            transition["timestamp"],
            transition["previous_value"],
            transition["value"],
        )
        for transition in transitions
    }

    for change in changes:
        key = (
            change["previous_timestamp"],
            change["timestamp"],
            change["previous_value"],
            change["value"],
        )

        assert key in transition_keys
