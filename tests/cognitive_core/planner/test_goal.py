from __future__ import annotations

import pytest

from scios.cognitive_core.planner.goal import Goal


class TestGoal:
    def test_create_default(self):
        goal = Goal("Complete experiment")

        assert goal.description == "Complete experiment"
        assert goal.success_criteria == []
        assert goal.constraints == {}

    def test_create_with_criteria(self):
        criteria = [
            "data_collected",
            "model_validated",
        ]

        goal = Goal(
            "Complete experiment",
            success_criteria=criteria,
        )

        assert goal.success_criteria == criteria
        assert goal.success_criteria is not criteria

    def test_create_with_constraints(self):
        constraints = {
            "priority": 10,
            "timeout": 60,
        }

        goal = Goal(
            "Complete experiment",
            constraints=constraints,
        )

        assert goal.constraints == constraints
        assert goal.constraints is not constraints

    def test_description_must_be_string(self):
        with pytest.raises(TypeError, match="description"):
            Goal(123)

    def test_success_criteria_must_be_list(self):
        with pytest.raises(TypeError, match="success_criteria"):
            Goal(
                "Complete experiment",
                success_criteria="data_collected",
            )

    def test_success_criteria_must_contain_strings(self):
        with pytest.raises(TypeError, match="success_criteria"):
            Goal(
                "Complete experiment",
                success_criteria=["data_collected", 123],
            )

    def test_constraints_must_be_dict(self):
        with pytest.raises(TypeError, match="constraints"):
            Goal(
                "Complete experiment",
                constraints=[],
            )

    def test_add_success_criterion(self):
        goal = Goal("Complete experiment")

        goal.add_success_criterion("data_collected")

        assert goal.success_criteria == ["data_collected"]

    def test_duplicate_criterion_is_ignored(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["data_collected"],
        )

        goal.add_success_criterion("data_collected")

        assert goal.success_criteria == ["data_collected"]

    def test_add_constraint(self):
        goal = Goal("Complete experiment")

        goal.add_constraint("priority", 10)

        assert goal.constraints["priority"] == 10

    def test_constraint_can_be_replaced(self):
        goal = Goal(
            "Complete experiment",
            constraints={"priority": 10},
        )

        goal.add_constraint("priority", 20)

        assert goal.constraints["priority"] == 20

    def test_is_successful_without_criteria(self):
        goal = Goal("Complete experiment")

        assert goal.is_successful({}) is True

    def test_is_successful_all_criteria_true(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=[
                "data_collected",
                "model_validated",
            ],
        )

        context = {
            "data_collected": True,
            "model_validated": True,
        }

        assert goal.is_successful(context) is True

    def test_is_successful_missing_criterion(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=[
                "data_collected",
                "model_validated",
            ],
        )

        assert goal.is_successful(
            {"data_collected": True}
        ) is False

    def test_is_successful_false_criterion(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["data_collected"],
        )

        assert goal.is_successful(
            {"data_collected": False}
        ) is False

    def test_is_successful_requires_dict(self):
        goal = Goal("Complete experiment")

        with pytest.raises(TypeError, match="context"):
            goal.is_successful([])

    def test_is_satisfied_direct_context(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["data_collected"],
        )

        assert goal.is_satisfied(
            {"data_collected": True}
        ) is True

    def test_is_satisfied_legacy_achievements(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=[
                "data_collected",
                "model_validated",
            ],
        )

        results = {
            "achievements": [
                "data_collected",
                "model_validated",
            ]
        }

        assert goal.is_satisfied(results) is True

    def test_is_satisfied_legacy_missing_achievement(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=[
                "data_collected",
                "model_validated",
            ],
        )

        assert goal.is_satisfied(
            {"achievements": ["data_collected"]}
        ) is False

    def test_to_dict(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["validated"],
            constraints={"priority": 5},
        )

        result = goal.to_dict()

        assert result == {
            "description": "Complete experiment",
            "success_criteria": ["validated"],
            "constraints": {"priority": 5},
        }

    def test_to_dict_returns_copies(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["validated"],
            constraints={"priority": 5},
        )

        result = goal.to_dict()

        result["success_criteria"].append("extra")
        result["constraints"]["priority"] = 100

        assert goal.success_criteria == ["validated"]
        assert goal.constraints["priority"] == 5

    def test_repr(self):
        goal = Goal(
            "Complete experiment",
            success_criteria=["validated"],
            constraints={"priority": 5},
        )

        representation = repr(goal)

        assert "Goal" in representation
        assert "Complete experiment" in representation
        assert "criteria=1" in representation
        assert "constraints=1" in representation

    def test_goal_has_no_execution_state(self):
        goal = Goal("Complete experiment")

        assert not hasattr(goal, "status")
        assert not hasattr(goal, "result")
        assert not hasattr(goal, "started_at")
        assert not hasattr(goal, "completed_at")