"""
SciOS Runtime Pipeline Contract Tests
======================================

Canonical contract tests for:

    scios.runtime.pipeline.Pipeline

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime import (
    ExecutionContext,
    Pipeline,
    Stage,
)


# ==========================================================
# Test Stages
# ==========================================================


class FirstStage(Stage):

    def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        context.log("first")
        context.set_artifact(
            "first",
            True,
        )


class SecondStage(Stage):

    def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        context.log("second")

        context.set_artifact(
            "second",
            True,
        )


class FailingStage(Stage):

    def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        raise ValueError("boom")


class OutputStage(Stage):

    def __init__(
        self,
        output,
    ) -> None:

        self.output = output

    def execute(
        self,
        context: ExecutionContext,
    ):

        return self.output


# ==========================================================
# Construction
# ==========================================================


def test_default_pipeline():

    pipeline = Pipeline()

    assert len(pipeline) == 0
    assert pipeline.stage_count == 0
    assert pipeline.stages == ()


def test_pipeline_from_stages():

    first = FirstStage()
    second = SecondStage()

    pipeline = Pipeline(
        [
            first,
            second,
        ]
    )

    assert pipeline.stage_count == 2
    assert pipeline.stages == (
        first,
        second,
    )


# ==========================================================
# Stage Management
# ==========================================================


def test_add_stage():

    pipeline = Pipeline()
    stage = FirstStage()

    returned = pipeline.add_stage(stage)

    assert returned is None
    assert stage in pipeline
    assert pipeline.stage_count == 1


def test_duplicate_stage_is_ignored():

    pipeline = Pipeline()
    stage = FirstStage()

    pipeline.add_stage(stage)
    pipeline.add_stage(stage)

    assert pipeline.stage_count == 1


def test_remove_stage():

    stage = FirstStage()

    pipeline = Pipeline(
        [stage]
    )

    pipeline.remove_stage(stage)

    assert stage not in pipeline
    assert pipeline.stage_count == 0


def test_remove_missing_stage_is_safe():

    pipeline = Pipeline()

    pipeline.remove_stage(
        FirstStage()
    )

    assert pipeline.stage_count == 0


def test_clear():

    pipeline = Pipeline(
        [
            FirstStage(),
            SecondStage(),
        ]
    )

    pipeline.clear()

    assert pipeline.stage_count == 0
    assert pipeline.stages == ()


def test_stages_are_read_only_view():

    pipeline = Pipeline(
        [
            FirstStage(),
        ]
    )

    stages = pipeline.stages

    assert isinstance(stages, tuple)

    with pytest.raises(AttributeError):
        stages.append(
            SecondStage()
        )


# ==========================================================
# Execution
# ==========================================================


def test_execute_returns_same_context():

    pipeline = Pipeline(
        [
            FirstStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    returned = pipeline.execute(
        context
    )

    assert returned is context


def test_run_is_execute_alias():

    pipeline = Pipeline(
        [
            FirstStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    returned = pipeline.run(
        context
    )

    assert returned is context


def test_stages_execute_in_order():

    pipeline = Pipeline(
        [
            FirstStage(),
            SecondStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    pipeline.execute(
        context
    )

    assert context.logs == [
        "Executing stage: FirstStage",
        "first",
        "Executing stage: SecondStage",
        "second",
    ]


def test_stage_artifacts_survive_pipeline():

    pipeline = Pipeline(
        [
            FirstStage(),
            SecondStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    pipeline.execute(
        context
    )

    assert context.get_artifact(
        "first"
    ) is True

    assert context.get_artifact(
        "second"
    ) is True


# ==========================================================
# Events
# ==========================================================


def test_stage_lifecycle_events():

    pipeline = Pipeline(
        [
            FirstStage(),
            SecondStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    pipeline.execute(
        context
    )

    assert context.events == [
        "FirstStage.started",
        "FirstStage.completed",
        "SecondStage.started",
        "SecondStage.completed",
    ]


def test_failed_stage_emits_failed_event():

    pipeline = Pipeline(
        [
            FailingStage(),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    context.start()

    # Context.start() emits the execution-level lifecycle event.
    # This test focuses exclusively on Pipeline stage events.
    context.events.clear()

    with pytest.raises(
        ValueError,
        match="boom",
    ):
        pipeline.execute(
            context
        )

    assert context.events == [
        "FailingStage.started",
        "FailingStage.failed",
    ]

    # Pipeline propagates the exception to ExecutionEngine.
    # ExecutionContext lifecycle failure is owned by the Engine,
    # therefore Pipeline must not transition the context to failed.
    assert context.failed is False
    assert context.error is None


# ==========================================================
# Output Capture
# ==========================================================


@pytest.mark.parametrize(
    "output",
    [
        None,
        "hello",
        {"answer": 42},
        123,
        ["a", "b"],
    ],
)
def test_stage_output_is_accepted(
    output,
):

    pipeline = Pipeline(
        [
            OutputStage(output),
        ]
    )

    context = ExecutionContext(
        "demo"
    )

    pipeline.execute(
        context
    )

    if isinstance(output, dict):

        assert context.metadata[
            "answer"
        ] == 42

    elif isinstance(output, str):

        assert output in context.logs

    elif output is not None:

        assert str(output) in context.logs


# ==========================================================
# Validation
# ==========================================================


def test_execute_requires_context():

    pipeline = Pipeline()

    with pytest.raises(
        ValueError,
        match="ExecutionContext is required",
    ):

        pipeline.execute(
            None
        )


# ==========================================================
# Diagnostics
# ==========================================================


def test_summary():

    first = FirstStage()
    second = SecondStage()

    pipeline = Pipeline(
        [
            first,
            second,
        ]
    )

    summary = pipeline.summary()

    assert summary == {
        "stage_count": 2,
        "stages": [
            "FirstStage",
            "SecondStage",
        ],
    }


def test_iteration():

    first = FirstStage()
    second = SecondStage()

    pipeline = Pipeline(
        [
            first,
            second,
        ]
    )

    assert list(pipeline) == [
        first,
        second,
    ]


def test_contains():

    stage = FirstStage()

    pipeline = Pipeline(
        [stage]
    )

    assert stage in pipeline
    assert SecondStage() not in pipeline


def test_repr():

    pipeline = Pipeline(
        [
            FirstStage(),
            SecondStage(),
        ]
    )

    text = repr(pipeline)

    assert "Pipeline" in text
    assert "stages=2" in text