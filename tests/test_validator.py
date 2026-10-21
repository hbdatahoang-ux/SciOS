from __future__ import annotations

import pytest

from scios.cognitive_core.planner.validator import PlanValidator
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task


def test_validator_initialization_and_schema():
    validator = PlanValidator()
    assert validator is not None

    tasks = [Task(description="Task X")]
    plan = Plan(goal=Goal("Schema goal"), tasks=tasks)
    result = validator.validate(plan)

    required_keys = {"valid", "errors", "warnings"}
    assert required_keys.issubset(result.keys())


def test_validator_valid_structural_plan():
    validator = PlanValidator()
    tasks = [Task(description="Task 1"), Task(description="Task 2")]
    plan = Plan(goal=Goal("Valid goal"), tasks=tasks)

    result = validator.validate(plan)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validator_empty_plan_detected():
    validator = PlanValidator()
    plan = Plan(goal=Goal("Empty goal"), tasks=[])

    result = validator.validate(plan)

    assert result["valid"] is False
    assert any("No tasks" in e for e in result["errors"])


def test_validator_missing_goal_rejected_by_plan_contract():
    with pytest.raises(TypeError, match="goal must be an instance of Goal"):
        Plan(goal=None, tasks=[Task(description="Task with no goal")])


def test_validator_mixed_task_structure_is_valid():
    validator = PlanValidator()
    tasks = [
        Task(description="Completed Task"),
        Task(description="Pending Task"),
    ]
    plan = Plan(goal=Goal("Mixed goal"), tasks=tasks)

    result = validator.validate(plan)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validator_multiple_plans_consistency():
    validator = PlanValidator()

    plan1 = Plan(
        goal=Goal("Plan 1"),
        tasks=[Task(description="Done")],
    )
    r1 = validator.validate(plan1)

    plan2 = Plan(
        goal=Goal("Plan 2"),
        tasks=[Task(description="Not done")],
    )
    r2 = validator.validate(plan2)

    assert r1["valid"] is True
    assert r2["valid"] is True
    assert r1["errors"] == []
    assert r2["errors"] == []
