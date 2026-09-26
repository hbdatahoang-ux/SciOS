from pathlib import Path

import pytest

from scios.runtime.tools.time_series import TimeSeriesChangeTool


ROOT = Path("data/real_workflow/time_series")


def test_metadata():
    tool = TimeSeriesChangeTool()

    assert tool.NAME == "time_series_change"
    assert tool.VERSION == "0.1.0"
    assert "deterministic delta-based IQR evidence" in tool.DESCRIPTION


def test_schema():
    tool = TimeSeriesChangeTool()

    schema = tool.schema()

    assert schema["required"] == ["file_path"]
    assert schema["properties"]["file_path"]["type"] == "string"


@pytest.mark.parametrize(
    "file_path",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_invalid_file_path_is_rejected(file_path):
    tool = TimeSeriesChangeTool()

    result = tool.run(file_path=file_path)

    assert result.success is False
    assert isinstance(result.error, ValueError)
    assert result.error.args[0] == "Invalid tool input"
    assert tool.executions == 0
    assert tool.failures == 0


def test_unsorted_series_is_ordered_before_transitions():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "unsorted.csv")
    )

    assert result.success is True

    transitions = result.value["transitions"]

    assert len(transitions) == 2

    assert transitions[0]["previous_value"] == 100.0
    assert transitions[0]["value"] == 101.0
    assert transitions[0]["delta"] == 1.0
    assert transitions[0]["direction"] == "increase"

    assert transitions[1]["previous_value"] == 101.0
    assert transitions[1]["value"] == 103.0
    assert transitions[1]["delta"] == 2.0
    assert transitions[1]["direction"] == "increase"

    assert result.value["changes"] == []
    assert tool.executions == 1
    assert tool.failures == 0


def test_zero_baseline_has_no_relative_change():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "zero_baseline.csv")
    )

    assert result.success is True

    transitions = result.value["transitions"]

    assert len(transitions) == 2

    assert transitions[0]["previous_value"] == 0.0
    assert transitions[0]["value"] == 10.0
    assert transitions[0]["delta"] == 10.0
    assert transitions[0]["absolute_delta"] == 10.0
    assert transitions[0]["relative_change"] is None

    assert transitions[1]["previous_value"] == 10.0
    assert transitions[1]["value"] == 11.0
    assert transitions[1]["delta"] == 1.0
    assert transitions[1]["absolute_delta"] == 1.0
    assert transitions[1]["relative_change"] == pytest.approx(0.1)


def test_missing_value_does_not_create_cross_gap_transition():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "missing_value.csv")
    )

    assert result.success is True
    assert result.value["transitions"] == []
    assert result.value["changes"] == []


def test_significant_change_contains_complete_deterministic_evidence():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "sudden_change.csv")
    )

    assert result.success is True

    transitions = result.value["transitions"]
    changes = result.value["changes"]

    assert len(transitions) == 6
    assert len(changes) == 1

    significant = changes[0]

    assert significant in transitions
    assert significant["previous_value"] == 105.0
    assert significant["value"] == 125.0
    assert significant["delta"] == 20.0
    assert significant["absolute_delta"] == 20.0
    assert significant["relative_change"] == pytest.approx(20.0 / 105.0)
    assert significant["direction"] == "increase"
    assert significant["significant_change"] is True
    assert significant["q1_delta"] == 1.0
    assert significant["q3_delta"] == 1.0
    assert significant["iqr_delta"] == 0.0
    assert significant["upper_delta_bound"] == 1.0
    assert significant["rule"] == "IQR_DELTA"


def test_changes_are_subset_of_transitions():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "multiple_changes.csv")
    )

    assert result.success is True

    transitions = result.value["transitions"]
    changes = result.value["changes"]

    assert len(transitions) == 12
    assert len(changes) == 3

    assert all(change in transitions for change in changes)
    assert all(change["significant_change"] is True for change in changes)


def test_duplicate_timestamp_is_a_tool_failure():
    tool = TimeSeriesChangeTool()

    result = tool.run(
        file_path=str(ROOT / "duplicate_timestamp.csv")
    )

    assert result.success is False
    assert isinstance(result.error, ValueError)
    assert (
        str(result.error)
        == "Time-series CSV contains duplicate timestamps."
    )
    assert tool.executions == 0
    assert tool.failures == 1


def test_missing_required_columns_is_a_tool_failure(tmp_path):
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(
        "timestamp,other\n"
        "2026-01-01,100\n"
        "2026-01-02,101\n",
        encoding="utf-8",
    )

    tool = TimeSeriesChangeTool()

    result = tool.run(file_path=str(csv_file))

    assert result.success is False
    assert isinstance(result.error, ValueError)
    assert (
        str(result.error)
        == "Time-series CSV must contain 'timestamp' and 'value' columns."
    )
    assert tool.executions == 0
    assert tool.failures == 1


def test_invalid_timestamp_is_a_tool_failure(tmp_path):
    csv_file = tmp_path / "invalid_timestamp.csv"
    csv_file.write_text(
        "timestamp,value\n"
        "not-a-date,100\n"
        "2026-01-02,101\n",
        encoding="utf-8",
    )

    tool = TimeSeriesChangeTool()

    result = tool.run(file_path=str(csv_file))

    assert result.success is False
    assert result.error is not None
    assert tool.executions == 0
    assert tool.failures == 1


def test_empty_series_returns_success_with_no_transitions(tmp_path):
    csv_file = tmp_path / "empty_series.csv"
    csv_file.write_text(
        "timestamp,value\n",
        encoding="utf-8",
    )

    tool = TimeSeriesChangeTool()

    result = tool.run(file_path=str(csv_file))

    assert result.success is True
    assert result.value["transitions"] == []
    assert result.value["changes"] == []
    assert result.value["q1_delta"] is None
    assert result.value["q3_delta"] is None
    assert result.value["iqr_delta"] is None
    assert result.value["upper_delta_bound"] is None
    assert tool.executions == 1
    assert tool.failures == 0
