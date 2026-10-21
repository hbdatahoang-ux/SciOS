"""
SciOS Runtime Tests
===================

Unit tests for the SciOS Runtime subsystem.
"""

from __future__ import annotations

import pytest

from scios.runtime import (
    ExecutionContext,
    ExecutionEngine,
    Pipeline,
    Stage,
)


# ==========================================================
# Test Stage
# ==========================================================

class DummyStage(Stage):
    """
    Simple stage used for runtime testing.
    """

    def execute(self, context: ExecutionContext) -> None:
        context.log("DummyStage executed")
        context.set_artifact("dummy", True)
        context.set_result("ok")


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def pipeline() -> Pipeline:
    pipe = Pipeline()
    pipe.add_stage(DummyStage())
    return pipe


@pytest.fixture
def engine(pipeline: Pipeline) -> ExecutionEngine:
    return ExecutionEngine(pipeline=pipeline)


# ==========================================================
# ExecutionContext
# ==========================================================

def test_context_creation() -> None:

    ctx = ExecutionContext("hello")

    assert ctx.task == "hello"
    assert ctx.status == "created"
    assert ctx.result is None


def test_context_logging() -> None:

    ctx = ExecutionContext("task")

    ctx.log("running")

    assert len(ctx.logs) == 1
    assert ctx.logs[0] == "running"


def test_context_artifacts() -> None:

    ctx = ExecutionContext("task")

    ctx.set_artifact("answer", 42)

    assert ctx.get_artifact("answer") == 42


# ==========================================================
# Pipeline
# ==========================================================

def test_pipeline_execution(
    pipeline: Pipeline,
) -> None:

    ctx = ExecutionContext("pipeline")

    pipeline.execute(ctx)

    assert ctx.get_artifact("dummy") is True
    assert ctx.result.value == "ok"


# ==========================================================
# Engine
# ==========================================================

def test_engine_run(
    engine: ExecutionEngine,
) -> None:

    ctx = engine.run("runtime task")

    assert ctx.status == "completed"
    assert ctx.result.value == "ok"


def test_engine_execute(
    engine: ExecutionEngine,
) -> None:

    result = engine.execute("runtime task")

    assert result.value == "ok"


# ==========================================================
# Events
# ==========================================================

def test_pipeline_events(
    pipeline: Pipeline,
) -> None:

    ctx = ExecutionContext("events")

    pipeline.execute(ctx)

    assert len(ctx.events) >= 2


# ==========================================================
# Stress
# ==========================================================

@pytest.mark.parametrize(
    "count",
    [
        1,
        10,
        50,
    ],
)
def test_runtime_multiple_tasks(
    engine: ExecutionEngine,
    count: int,
) -> None:

    for i in range(count):

        ctx = engine.run(f"task-{i}")

        assert ctx.status == "completed"
        assert ctx.result.value == "ok"