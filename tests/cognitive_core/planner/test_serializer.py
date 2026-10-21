import json

import pytest

from scios.cognitive_core.planner.constraint import Constraint, ConstraintSet
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.serializer import PlanSerializer
from scios.cognitive_core.planner.task import Task


def make_plan() -> Plan:
    goal = Goal(
        description="Run experiment",
        success_criteria=["completed"],
    )

    plan = Plan(goal)

    task_a = Task(
        description="Prepare experiment",
        task_id="task-1",
    )
    task_a.set_metadata("source", "planner")

    task_b = Task(
        description="Run experiment",
        dependencies=["task-1"],
        task_id="task-2",
    )

    plan.add_task(task_a)
    plan.add_task(task_b)

    plan.constraints.add_constraint(
        Constraint(
            name="mode",
            value="safe",
            constraint_type="execution",
        )
    )

    plan.set_metadata("strategy", "priority")

    return plan


def test_to_dict_matches_plan_contract():
    plan = make_plan()

    data = PlanSerializer.to_dict(plan)

    assert data == plan.to_dict()
    assert "goal" in data
    assert "tasks" in data
    assert "constraints" in data
    assert "metadata" in data
    assert "task_graph" not in data


def test_from_dict_reconstructs_plan():
    original = make_plan()

    restored = PlanSerializer.from_dict(
        original.to_dict()
    )

    assert isinstance(restored, Plan)
    assert restored.goal.description == "Run experiment"
    assert restored.task_count == 2

    assert restored.get_task("task-1").description == (
        "Prepare experiment"
    )
    assert restored.get_task("task-2").dependencies == [
        "task-1"
    ]

    assert restored.metadata == {
        "strategy": "priority"
    }

    constraint = restored.constraints.get_constraint("mode")

    assert constraint is not None
    assert constraint.value == "safe"
    assert constraint.constraint_type == "execution"


def test_round_trip_json():
    original = make_plan()

    text = PlanSerializer.to_json(original)
    restored = PlanSerializer.from_json(text)

    assert isinstance(text, str)
    assert restored.to_dict() == original.to_dict()


def test_to_dict_rejects_invalid_plan():
    with pytest.raises(TypeError):
        PlanSerializer.to_dict("invalid")


def test_from_dict_rejects_invalid_input():
    with pytest.raises(TypeError):
        PlanSerializer.from_dict("invalid")


def test_from_dict_rejects_invalid_goal():
    with pytest.raises(ValueError):
        PlanSerializer.from_dict({"goal": None})


def test_from_dict_rejects_invalid_tasks():
    with pytest.raises(ValueError):
        PlanSerializer.from_dict(
            {
                "goal": {
                    "description": "test",
                    "success_criteria": [],
                    "constraints": {},
                },
                "tasks": {},
            }
        )


def test_from_dict_rejects_dependency_cycle():
    data = {
        "goal": {
            "description": "test",
            "success_criteria": [],
            "constraints": {},
        },
        "tasks": [
            {
                "id": "a",
                "description": "A",
                "constraints": {},
                "dependencies": ["b"],
                "metadata": {},
            },
            {
                "id": "b",
                "description": "B",
                "constraints": {},
                "dependencies": ["a"],
                "metadata": {},
            },
        ],
        "constraints": {},
        "metadata": {},
    }

    with pytest.raises(ValueError):
        PlanSerializer.from_dict(data)


def test_json_is_valid():
    plan = make_plan()

    text = PlanSerializer.to_json(plan)
    data = json.loads(text)

    assert data == plan.to_dict()