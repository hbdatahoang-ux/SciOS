"""
Tests for the canonical Cognitive Core Planner.

Contract:

    Goal -> Plan

The Planner must construct cognitive Plans only.
It must not execute or compile them.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.strategy import PlanningStrategy
from scios.cognitive_core.planner.task import Task


# ==========================================================
# Construction
# ==========================================================

def test_planner_creation() -> None:
    planner = Planner()

    assert isinstance(
        planner,
        Planner,
    )

    assert isinstance(
        planner.strategy,
        PlanningStrategy,
    )


def test_planner_accepts_custom_strategy() -> None:
    strategy = PlanningStrategy()
    planner = Planner(strategy=strategy)

    assert planner.strategy is strategy


def test_planner_rejects_invalid_strategy() -> None:
    with pytest.raises(
        TypeError,
        match="strategy must be an instance of PlanningStrategy",
    ):
        Planner(strategy=object())


# ==========================================================
# create_plan()
# ==========================================================

def test_create_plan_returns_canonical_plan() -> None:
    planner = Planner()

    goal = Goal(
        description="analyze battery"
    )

    plan = planner.create_plan(goal)

    assert isinstance(
        plan,
        Plan,
    )

    assert plan.goal is goal


def test_create_plan_rejects_invalid_goal() -> None:
    planner = Planner()

    with pytest.raises(
        TypeError,
        match="goal must be an instance of Goal",
    ):
        planner.create_plan(
            "analyze battery"  # type: ignore[arg-type]
        )


# ==========================================================
# Explicit string tasks
# ==========================================================

def test_create_plan_normalizes_string_tasks() -> None:
    planner = Planner()

    goal = Goal(
        description="build tool"
    )

    plan = planner.create_plan(
        goal,
        tasks=[
            "inspect requirements",
            "implement tool",
            "validate tool",
        ],
    )

    assert isinstance(
        plan,
        Plan,
    )

    assert [
        task.description
        for task in plan.tasks
    ] == [
        "inspect requirements",
        "implement tool",
        "validate tool",
    ]


def test_string_tasks_are_converted_to_task_objects() -> None:
    planner = Planner()

    goal = Goal(
        description="build tool"
    )

    plan = planner.create_plan(
        goal,
        tasks=["implement tool"],
    )

    assert len(plan.tasks) == 1
    assert isinstance(
        plan.tasks[0],
        Task,
    )


# ==========================================================
# Explicit Task objects
# ==========================================================

def test_create_plan_preserves_task_objects() -> None:
    planner = Planner()

    goal = Goal(
        description="analyze battery"
    )

    task = Task(
        description="collect measurements"
    )

    plan = planner.create_plan(
        goal,
        tasks=[task],
    )

    assert len(plan.tasks) == 1
    assert plan.tasks[0] is task


def test_create_plan_preserves_task_dependencies() -> None:
    planner = Planner()

    goal = Goal(
        description="analyze battery"
    )

    first = Task(
        description="collect measurements",
        task_id="measure",
    )

    second = Task(
        description="analyze measurements",
        task_id="analyze",
        dependencies=["measure"],
    )

    plan = planner.create_plan(
        goal,
        tasks=[
            first,
            second,
        ],
    )

    assert plan.get_task("analyze").dependencies == [
        "measure",
    ]

    assert [
        task.id
        for task in plan.topological_order()
    ] == [
        "measure",
        "analyze",
    ]


# ==========================================================
# Invalid tasks
# ==========================================================

def test_create_plan_rejects_invalid_task_type() -> None:
    planner = Planner()

    goal = Goal(
        description="build tool"
    )

    with pytest.raises(
        TypeError,
        match="tasks must contain only str or Task instances",
    ):
        planner.create_plan(
            goal,
            tasks=[123],  # type: ignore[list-item]
        )


# ==========================================================
# Strategy delegation
# ==========================================================

class RecordingStrategy(PlanningStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.called_with: Goal | None = None

    def decompose_goal(
        self,
        goal: Goal,
    ) -> list[Task]:
        self.called_with = goal

        return [
            Task(
                description="generated task"
            )
        ]


def test_create_plan_delegates_to_strategy_when_tasks_omitted() -> None:
    strategy = RecordingStrategy()
    planner = Planner(
        strategy=strategy
    )

    goal = Goal(
        description="scientific analysis"
    )

    plan = planner.create_plan(goal)

    assert strategy.called_with is goal

    assert [
        task.description
        for task in plan.tasks
    ] == [
        "generated task",
    ]


def test_explicit_tasks_bypass_strategy() -> None:
    strategy = RecordingStrategy()
    planner = Planner(
        strategy=strategy
    )

    goal = Goal(
        description="scientific analysis"
    )

    plan = planner.create_plan(
        goal,
        tasks=["explicit task"],
    )

    assert strategy.called_with is None

    assert [
        task.description
        for task in plan.tasks
    ] == [
        "explicit task",
    ]


# ==========================================================
# Reset
# ==========================================================

def test_reset_restores_default_strategy() -> None:
    custom = RecordingStrategy()
    planner = Planner(
        strategy=custom
    )

    assert planner.strategy is custom

    planner.reset()

    assert isinstance(
        planner.strategy,
        PlanningStrategy,
    )

    assert planner.strategy is not custom


# ==========================================================
# Representation
# ==========================================================

def test_repr() -> None:
    planner = Planner()

    result = repr(planner)

    assert result.startswith(
        "Planner(strategy="
    )


# ==========================================================
# Architectural boundary
# ==========================================================

def test_planner_does_not_execute_or_compile() -> None:
    planner = Planner()

    goal = Goal(
        description="execute experiment"
    )

    plan = planner.create_plan(
        goal,
        tasks=["run experiment"],
    )

    assert isinstance(
        plan,
        Plan,
    )

    assert not hasattr(
        planner,
        "execute",
    )

    assert not hasattr(
        planner,
        "execute_tool",
    )

    assert not hasattr(
        planner,
        "compile",
    )

    assert not hasattr(
        planner,
        "execution_graph",
    )


def test_plan_has_no_runtime_execution_state() -> None:
    planner = Planner()

    plan = planner.create_plan(
        Goal(
            description="run experiment"
        ),
        tasks=["execute experiment"],
    )

    forbidden = {
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
        "retry_count",
        "execution_context",
        "execution_graph",
        "scheduler",
        "executor",
    }

    assert forbidden.isdisjoint(
        vars(plan)
    )
