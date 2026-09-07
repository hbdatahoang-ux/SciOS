from __future__ import annotations

import pytest

from scios.cognitive_core.planner.objective import Objective
from scios.cognitive_core.planner.task import Task


class TestObjective:
    def test_create_with_description(self):
        objective = Objective("Build simulation model")

        assert objective.description == "Build simulation model"
        assert objective.parent_goal is None
        assert objective.constraints == {}
        assert objective.tasks == []

    def test_create_with_parent_goal(self):
        objective = Objective(
            "Prepare data",
            parent_goal="Complete experiment",
        )

        assert objective.parent_goal == "Complete experiment"

    def test_create_with_constraints(self):
        constraints = {
            "priority": 10,
            "timeout": 30,
        }

        objective = Objective(
            "Prepare data",
            constraints=constraints,
        )

        assert objective.constraints == constraints
        assert objective.constraints is not constraints

    def test_constraints_are_copied(self):
        constraints = {"priority": 5}
        objective = Objective(
            "Prepare data",
            constraints=constraints,
        )

        constraints["priority"] = 100

        assert objective.constraints["priority"] == 5

    def test_add_task(self):
        objective = Objective("Prepare data")
        task = Task("Load dataset")

        objective.add_task(task)

        assert objective.tasks == [task]

    def test_add_multiple_tasks(self):
        objective = Objective("Prepare data")

        task_a = Task("Load dataset")
        task_b = Task("Validate dataset")

        objective.add_task(task_a)
        objective.add_task(task_b)

        assert objective.tasks == [task_a, task_b]

    def test_add_task_requires_task_instance(self):
        objective = Objective("Prepare data")

        with pytest.raises(TypeError, match="Task"):
            objective.add_task("Load dataset")

    def test_description_must_be_string(self):
        with pytest.raises(TypeError, match="description"):
            Objective(123)

    def test_parent_goal_must_be_string_or_none(self):
        with pytest.raises(TypeError, match="parent_goal"):
            Objective(
                "Prepare data",
                parent_goal=123,
            )

    def test_constraints_must_be_dict_or_none(self):
        with pytest.raises(TypeError, match="constraints"):
            Objective(
                "Prepare data",
                constraints=[],
            )

    def test_empty_string_description_is_allowed(self):
        objective = Objective("")

        assert objective.description == ""

    def test_repr(self):
        objective = Objective("Prepare data")
        objective.add_task(Task("Load dataset"))

        representation = repr(objective)

        assert "Objective" in representation
        assert "Prepare data" in representation
        assert "tasks=1" in representation

    def test_objective_has_no_execution_state(self):
        objective = Objective("Prepare data")

        assert not hasattr(objective, "status")
        assert not hasattr(objective, "result")
        assert not hasattr(objective, "started_at")
        assert not hasattr(objective, "completed_at")