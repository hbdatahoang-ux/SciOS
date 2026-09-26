from __future__ import annotations

from pathlib import Path

import pytest

from scios.application.dataset_quality import (
    DATASET_QUALITY_REF,
    DatasetQualityApplication,
)
from scios.cognitive_core.planner import Goal, Task


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "data" / "real_workflow" / "dataset_quality"


def _run_application(fixture_name: str) -> dict[str, object]:
    fixture = FIXTURE_DIR / fixture_name
    assert fixture.exists(), f"Missing acceptance fixture: {fixture}"

    app = DatasetQualityApplication(
        file_path=str(fixture),
    )

    goal = Goal(f"Audit dataset quality: {fixture_name}")

    result = app.analyze(goal=goal)

    assert isinstance(result, dict)
    assert app.last_result is not None
    assert app.last_result.success is True

    return result


def _get_profile(
    result: dict[str, object],
) -> dict[str, dict[str, object]]:
    assert "columns_profile" in result

    profile = result["columns_profile"]

    assert isinstance(profile, dict)
    assert all(isinstance(value, dict) for value in profile.values())

    return profile


def test_complete_dataset_workflow():
    result = _run_application("complete.csv")

    assert result["rows"] == 5
    assert result["columns"] == 4
    assert result["column_names"] == [
        "id",
        "age",
        "group",
        "active",
    ]

    profile = _get_profile(result)

    assert profile["id"]["kind"] == "numeric"
    assert profile["age"]["kind"] == "numeric"
    assert profile["group"]["kind"] == "categorical/text"
    assert profile["active"]["kind"] == "boolean"

    assert result["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_missing_values_workflow():
    result = _run_application("missing.csv")

    profile = _get_profile(result)

    assert profile["age"]["missing_count"] == 2
    assert profile["age"]["missing_fraction"] == pytest.approx(0.4)

    assert profile["group"]["missing_count"] == 1
    assert profile["group"]["missing_fraction"] == pytest.approx(0.2)


def test_duplicate_rows_workflow():
    result = _run_application("duplicates.csv")

    duplicate_rows = result["duplicate_rows"]

    assert duplicate_rows == {
        "count": 2,
        "fraction": pytest.approx(0.4),
    }


def test_constant_columns_workflow():
    result = _run_application("constant.csv")

    profile = _get_profile(result)

    assert profile["constant"]["unique_count"] == 1
    assert profile["constant"]["is_constant"] is True

    assert profile["id"]["is_constant"] is False


def test_mixed_types_workflow():
    result = _run_application("mixed_types.csv")

    profile = _get_profile(result)

    assert profile["number"]["kind"] == "numeric"
    assert profile["flag"]["kind"] == "boolean"
    assert profile["label"]["kind"] == "categorical/text"


def test_empty_dataset_workflow():
    result = _run_application("empty.csv")

    assert result["rows"] == 0
    assert result["columns"] == 3

    profile = _get_profile(result)

    for column in profile.values():
        assert column["missing_fraction"] == 0.0

    assert result["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_quality_findings_workflow():
    result = _run_application("quality_findings.csv")

    profile = _get_profile(result)

    assert profile["value"]["missing_count"] == 2
    assert profile["constant"]["is_constant"] is True

    assert result["duplicate_rows"]["count"] == 1


def test_application_preserves_tool_evidence_contract():
    result = _run_application("complete.csv")

    assert set(result) == {
        "rows",
        "columns",
        "column_names",
        "columns_profile",
        "duplicate_rows",
    }

    profile = _get_profile(result)

    required_fields = {
        "dtype",
        "kind",
        "missing_count",
        "missing_fraction",
        "unique_count",
        "is_constant",
    }

    for column in profile.values():
        assert set(column) == required_fields

    assert set(result["duplicate_rows"]) == {
        "count",
        "fraction",
    }


@pytest.mark.parametrize(
    "file_path",
    [
        "",
        "   ",
    ],
)
def test_empty_file_path_is_rejected(file_path: str):
    with pytest.raises(ValueError):
        DatasetQualityApplication(file_path=file_path)


def test_non_string_file_path_is_rejected():
    with pytest.raises(TypeError):
        DatasetQualityApplication(file_path=123)  # type: ignore[arg-type]


def test_binder_contract():
    app = DatasetQualityApplication(
        file_path=str(FIXTURE_DIR / "complete.csv"),
    )

    bound = app.binder.bind(
        Task(
            "Audit dataset structural and integrity quality.",
            task_id="dataset-quality",
        )
    )

    assert bound == DATASET_QUALITY_REF


def test_non_matching_task_is_not_bound():
    app = DatasetQualityApplication(
        file_path=str(FIXTURE_DIR / "complete.csv"),
    )

    result = app.binder.bind(
        Task(
            "Some other task.",
            task_id="other-task",
        )
    )

    assert result is None


def test_missing_file_failure_propagates():
    app = DatasetQualityApplication(
        file_path=str(FIXTURE_DIR / "does-not-exist.csv"),
    )

    with pytest.raises(Exception):
        app.analyze(
            goal=Goal("Audit missing dataset"),
        )



