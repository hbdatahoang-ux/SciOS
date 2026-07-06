# tests/test_validator.py

import pytest
from scios.cognitive_core.planner.validator import PlanValidator
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task


def test_validator_initialization():
    validator = PlanValidator()
    assert validator is not None


def test_validator_validate_successful_plan():
    validator = PlanValidator()
    tasks = [Task(description="Task 1"), Task(description="Task 2")]
    for t in tasks:
        t.mark_completed()
    plan = Plan(goal=Goal("Validation goal"), tasks=tasks)

    result = validator.validate(plan)
    assert isinstance(result, dict)
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validator_validate_incomplete_plan():
    validator = PlanValidator()
    tasks = [Task(description="Incomplete Task")]
    plan = Plan(goal=Goal("Incomplete goal"), tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("Incomplete Task" in e for e in result["errors"])


def test_validator_validate_empty_plan():
    validator = PlanValidator()
    plan = Plan(goal=Goal("Empty goal"), tasks=[])

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("No tasks" in e for e in result["errors"])


def test_validator_validate_missing_goal():
    validator = PlanValidator()
    tasks = [Task(description="Task with no goal")]
    plan = Plan(goal=None, tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("Missing goal" in e for e in result["errors"])


def test_validator_plan_with_mixed_tasks():
    validator = PlanValidator()
    tasks = [Task(description="Completed Task"), Task(description="Pending Task")]
    tasks[0].mark_completed()
    plan = Plan(goal=Goal("Mixed goal"), tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is False
    # Có thể vừa có errors vừa có warnings
    assert any("Pending Task" in e or "Pending Task" in w for e in result["errors"] + result["warnings"])


def test_validator_status_schema():
    validator = PlanValidator()
    tasks = [Task(description="Task X")]
    plan = Plan(goal=Goal("Schema goal"), tasks=tasks)
    result = validator.validate(plan)

    required_keys = {"valid", "errors", "warnings"}
    assert required_keys.issubset(result.keys())
