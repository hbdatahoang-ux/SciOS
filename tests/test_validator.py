# tests/test_validator.py

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


def test_validator_valid_plan_all_tasks_completed():
    validator = PlanValidator()
    tasks = [Task(description="Task 1"), Task(description="Task 2")]
    for t in tasks:
        t.mark_completed()
    plan = Plan(goal=Goal("Valid goal"), tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validator_incomplete_task_detected():
    validator = PlanValidator()
    task = Task(description="Incomplete Task")
    plan = Plan(goal=Goal("Incomplete goal"), tasks=[task])

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("Incomplete Task" in e for e in result["errors"])


def test_validator_empty_plan_detected():
    validator = PlanValidator()
    plan = Plan(goal=Goal("Empty goal"), tasks=[])

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("No tasks" in e for e in result["errors"])


def test_validator_missing_goal_detected():
    validator = PlanValidator()
    tasks = [Task(description="Task with no goal")]
    plan = Plan(goal=None, tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is False
    assert any("Missing goal" in e for e in result["errors"])


def test_validator_mixed_tasks_produce_errors_or_warnings():
    validator = PlanValidator()
    tasks = [Task(description="Completed Task"), Task(description="Pending Task")]
    tasks[0].mark_completed()
    plan = Plan(goal=Goal("Mixed goal"), tasks=tasks)

    result = validator.validate(plan)
    assert result["valid"] is False
    # Pending Task phải xuất hiện trong errors hoặc warnings
    assert any("Pending Task" in msg for msg in result["errors"] + result["warnings"])


def test_validator_multiple_plans_consistency():
    validator = PlanValidator()

    # Plan hợp lệ
    t1 = Task(description="Done")
    t1.mark_completed()
    plan1 = Plan(goal=Goal("Plan 1"), tasks=[t1])
    r1 = validator.validate(plan1)
    assert r1["valid"] is True

    # Plan không hợp lệ
    t2 = Task(description="Not done")
    plan2 = Plan(goal=Goal("Plan 2"), tasks=[t2])
    r2 = validator.validate(plan2)
    assert r2["valid"] is False
    assert any("Not done" in e or "No tasks" in e for e in r2["errors"])
