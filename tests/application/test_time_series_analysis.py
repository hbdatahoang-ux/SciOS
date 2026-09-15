from __future__ import annotations

from pathlib import Path

import pytest

from scios.application.time_series_analysis import (
    TIME_SERIES_CHANGE_REF,
    TimeSeriesChangeApplication,
    TimeSeriesChangeBinder,
)
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.graph import ExecutionGraph
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.result import ToolResult


FIXTURE_DIR = Path("data/real_workflow/time_series")


def make_app(name: str) -> TimeSeriesChangeApplication:
    return TimeSeriesChangeApplication(
        file_path=str(FIXTURE_DIR / name),
    )


def make_goal() -> Goal:
    return Goal(
        description="Analyze time-series changes",
        success_criteria=["time_series_change_completed"],
    )


def test_time_series_application_contract_exists() -> None:
    app = make_app("stable.csv")

    assert isinstance(app, TimeSeriesChangeApplication)
    assert isinstance(app.binder, TimeSeriesChangeBinder)
    assert isinstance(app.tool, object)
    assert isinstance(app.registry, OperationRegistry)

    assert TIME_SERIES_CHANGE_REF.name == "time_series_change"
    assert TIME_SERIES_CHANGE_REF.version == "0.1.0"


def test_binder_contract() -> None:
    binder = TimeSeriesChangeBinder()

    task = Task(
        "Analyze time series for significant changes.",
        task_id="time-series-change",
    )

    assert binder.bind(task) == TIME_SERIES_CHANGE_REF

    unrelated = Task(
        "Unrelated task",
        task_id="other-task",
    )

    assert binder.bind(unrelated) is None

    with pytest.raises(TypeError, match="task must be a Task"):
        binder.bind("not-a-task")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "file_path, expected_exception, message",
    [
        (
            "",
            ValueError,
            "file_path must not be empty",
        ),
        (
            "   ",
            ValueError,
            "file_path must not be empty",
        ),
    ],
)
def test_application_file_path_validation(
    file_path: str,
    expected_exception: type[Exception],
    message: str,
) -> None:
    with pytest.raises(expected_exception, match=message):
        TimeSeriesChangeApplication(file_path=file_path)


def test_application_rejects_non_string_file_path() -> None:
    with pytest.raises(
        TypeError,
        match="file_path must be a string",
    ):
        TimeSeriesChangeApplication(
            file_path=123,  # type: ignore[arg-type]
        )


def test_reasoning_problem_contract() -> None:
    app = make_app("sudden_change.csv")

    evidence = {
        "timestamp": "2026-02-07",
        "previous_timestamp": "2026-02-06",
        "previous_value": 105.0,
        "value": 125.0,
        "delta": 20.0,
        "absolute_delta": 20.0,
        "relative_change": 20.0 / 105.0,
        "direction": "increase",
        "significant_change": True,
        "q1_delta": 1.0,
        "q3_delta": 1.0,
        "iqr_delta": 0.0,
        "upper_delta_bound": 1.0,
        "rule": "IQR_DELTA",
    }

    problem = app.reasoning_problem(
        query="Why did the time series change significantly?",
        evidence=evidence,
    )

    assert problem.context["evidence"] == evidence


def test_reasoning_problem_validates_query() -> None:
    app = make_app("stable.csv")

    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        app.reasoning_problem(
            query="",
            evidence={},
        )


def test_reasoning_problem_validates_evidence() -> None:
    app = make_app("stable.csv")

    with pytest.raises(
        TypeError,
        match="evidence must be a dict",
    ):
        app.reasoning_problem(
            query="Why?",
            evidence=[],  # type: ignore[arg-type]
        )


def test_execution_service_uses_application_binding() -> None:
    app = make_app("sudden_change.csv")

    compiler = PlanCompiler(
        operation_binder=app.binder,
    )
    resolver = OperationResolver(app.registry)

    service = app.execution_service(
        compiler=compiler,
        resolver=resolver,
        executor=Executor(),
    )

    goal = make_goal()
    task = Task(
        "Analyze time series for significant changes.",
        task_id="time-series-change",
    )

    result = service.execute(
        goal,
        tasks=[task],
    )

    assert result.goal is goal
    assert isinstance(result.graph, ExecutionGraph)
    assert len(result.graph.nodes) == 1

    node = next(iter(result.graph.nodes.values()))

    assert node.operation_ref == TIME_SERIES_CHANGE_REF
    assert node.status.name == "SUCCESS"

    assert isinstance(app.last_result, ToolResult)
    assert app.last_result.success

    assert isinstance(app.last_result.value, dict)
    assert app.last_result.value["changes"]


def test_end_to_end_sudden_change() -> None:
    app = make_app("sudden_change.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Why is the final increase significant?",
    )

    assert answer["goal"] == "Analyze time-series changes"
    assert answer["rows"] == 7
    assert answer["columns"] == 2
    assert answer["column_names"] == ["timestamp", "value"]

    assert answer["timestamp_column"] == "timestamp"
    assert answer["value_column"] == "value"

    assert len(answer["transitions"]) == 6
    assert len(answer["changes"]) == 1

    change = answer["changes"][0]

    assert change["previous_value"] == 105.0
    assert change["value"] == 125.0
    assert change["delta"] == 20.0
    assert change["direction"] == "increase"
    assert change["significant_change"] is True
    assert change["rule"] == "IQR_DELTA"

    assert len(answer["reasoning"]) == 1
    assert answer["reasoning"][0]["significant_change"] is True

    assert isinstance(answer["explanation"], str)
    assert answer["explanation"].strip()


def test_multiple_changes_preserve_deterministic_evidence() -> None:
    app = make_app("multiple_changes.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Which changes are significant?",
    )

    assert len(answer["transitions"]) == 12
    assert len(answer["changes"]) == 3

    directions = [
        change["direction"]
        for change in answer["changes"]
    ]

    assert directions == [
        "increase",
        "decrease",
        "increase",
    ]

    deltas = [
        change["delta"]
        for change in answer["changes"]
    ]

    assert deltas == [10.0, -10.0, 15.0]

    for change in answer["changes"]:
        assert change in answer["transitions"]
        assert change["significant_change"] is True
        assert change["rule"] == "IQR_DELTA"


def test_unsorted_input_is_returned_in_chronological_order() -> None:
    app = make_app("unsorted.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="What changed?",
    )

    transitions = answer["transitions"]

    assert len(transitions) == 2

    assert transitions[0]["previous_value"] == 100.0
    assert transitions[0]["value"] == 101.0
    assert transitions[0]["delta"] == 1.0

    assert transitions[1]["previous_value"] == 101.0
    assert transitions[1]["value"] == 103.0
    assert transitions[1]["delta"] == 2.0


def test_zero_baseline_preserves_none_relative_change() -> None:
    app = make_app("zero_baseline.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="What changed?",
    )

    transitions = answer["transitions"]

    assert len(transitions) == 2

    assert transitions[0]["delta"] == 10.0
    assert transitions[0]["relative_change"] is None

    assert transitions[1]["delta"] == 1.0
    assert transitions[1]["relative_change"] == pytest.approx(
        0.1,
    )


def test_missing_value_does_not_create_cross_gap_transition() -> None:
    app = make_app("missing_value.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Are there significant changes?",
    )

    assert answer["transitions"] == []
    assert answer["changes"] == []
    assert answer["reasoning"] == []


def test_stable_series_has_no_significant_changes() -> None:
    app = make_app("stable.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Are there significant changes?",
    )

    assert len(answer["transitions"]) == 7
    assert answer["changes"] == []
    assert answer["reasoning"] == []

    assert "No significant changes" in answer["explanation"]


def test_answer_does_not_leak_execution_internals() -> None:
    app = make_app("sudden_change.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Explain the significant change.",
    )

    answer_text = repr(answer)

    assert "ExecutionGraph" not in answer_text
    assert "ToolResult" not in answer_text
    assert "GoalExecutionService" not in answer_text


def test_time_series_explanation_uses_change_semantics() -> None:
    app = make_app("sudden_change.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Explain the final increase.",
    )

    assert "significant change" in answer["explanation"]
    assert "105.0" in answer["explanation"]
    assert "125.0" in answer["explanation"]
    assert "IQR_DELTA" in answer["explanation"]


def test_time_series_explanation_preserves_original_query_contract() -> None:
    app = make_app("sudden_change.csv")

    answer = app.analyze(
        goal=make_goal(),
        query="Why is the final increase significant?",
    )

    assert answer["explanation"]
    assert answer["changes"]
    assert answer["reasoning"]
    assert answer["changes"][0]["significant_change"] is True


def test_explanation_failure_uses_deterministic_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = make_app("sudden_change.csv")

    def failing_explain(**_: object) -> str:
        raise RuntimeError("reasoner unavailable")

    monkeypatch.setattr(
        app,
        "_explain_changes",
        failing_explain,
    )

    answer = app.analyze(
        goal=make_goal(),
        query="Explain the significant change.",
    )

    assert answer["explanation"] == (
        "1 significant change(s) were identified "
        "by the deterministic reasoning layer."
    )


def test_duplicate_timestamp_fails_at_application_boundary() -> None:
    app = make_app("duplicate_timestamp.csv")

    with pytest.raises(
        RuntimeError,
        match="Time-series change execution failed",
    ):
        app.analyze(
            goal=make_goal(),
            query="Why did the series change?",
        )
