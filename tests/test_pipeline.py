"""
SciOS Runtime Pipeline Integration Tests
========================================

Integration tests for the runtime execution pipeline.
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
# Test Stages
# ==========================================================

class PlannerStage(Stage):

    def execute(self, context: ExecutionContext) -> None:
        context.log("planner")
        context.set_artifact(
            "plan",
            [
                "collect",
                "analyze",
                "report",
            ],
        )


class ExecutorStage(Stage):

    def execute(self, context: ExecutionContext) -> None:
        plan = context.get_artifact("plan")

        assert plan is not None

        context.log("executor")

        context.set_artifact(
            "execution",
            True,
        )


class ReflectionStage(Stage):

    def execute(self, context: ExecutionContext) -> None:

        context.log("reflection")

        context.set_result(
            {
                "status": "success",
                "task": context.task,
            }
        )


# ==========================================================
# Fixture
# ==========================================================

@pytest.fixture
def engine() -> ExecutionEngine:

    pipeline = Pipeline()

    pipeline.add_stage(
        PlannerStage()
    )

    pipeline.add_stage(
        ExecutorStage()
    )

    pipeline.add_stage(
        ReflectionStage()
    )

    return ExecutionEngine(
        pipeline=pipeline,
    )


# ==========================================================
# Pipeline
# ==========================================================

def test_pipeline_execution(
    engine: ExecutionEngine,
) -> None:

    ctx = engine.run(
        "battery analysis"
    )

    assert ctx.status == "completed"

    assert ctx.result["status"] == "success"

    assert ctx.get_artifact(
        "plan"
    ) is not None

    assert ctx.get_artifact(
        "execution"
    ) is True


def test_pipeline_stage_order(
    engine: ExecutionEngine,
) -> None:

    ctx = engine.run(
        "pipeline ordering"
    )

    assert ctx.logs == [
        "Task received: pipeline ordering",
        "Pipeline started",
        "Executing stage: PlannerStage",
        "planner",
        "Executing stage: ExecutorStage",
        "executor",
        "Executing stage: ReflectionStage",
        "reflection",
        "Pipeline completed",
    ]


def test_pipeline_events(
    engine: ExecutionEngine,
) -> None:

    ctx = engine.run(
        "events"
    )

    assert "PlannerStage.started" in ctx.events
    assert "PlannerStage.completed" in ctx.events

    assert "ExecutorStage.started" in ctx.events
    assert "ExecutorStage.completed" in ctx.events

    assert "ReflectionStage.started" in ctx.events
    assert "ReflectionStage.completed" in ctx.events


@pytest.mark.parametrize(
    "task",
    [
        "simulation",
        "optimization",
        "battery",
        "protein",
        "climate",
    ],
)
def test_pipeline_multiple_tasks(
    engine: ExecutionEngine,
    task: str,
) -> None:

    ctx = engine.run(task)

    assert ctx.status == "completed"

    assert ctx.result["task"] == task


def test_pipeline_stress(
    engine: ExecutionEngine,
) -> None:

    for i in range(100):

        ctx = engine.run(
            f"task-{i}"
        )

        assert ctx.status == "completed"

        assert ctx.result["status"] == "success"