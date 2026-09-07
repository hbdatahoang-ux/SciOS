"""
Contract tests for SciOS Cognitive Core PlanningStrategy.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.strategy import PlanningStrategy
from scios.cognitive_core.planner.task import Task


class TestPlanningStrategyConstruction:
    def test_default_values(self):
        strategy = PlanningStrategy()

        assert strategy.name == "DefaultStrategy"
        assert strategy.description == ""

    def test_custom_values(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
            description="Research-oriented planning",
        )

        assert strategy.name == "ResearchStrategy"
        assert strategy.description == "Research-oriented planning"

    def test_name_must_be_string(self):
        with pytest.raises(TypeError):
            PlanningStrategy(name=123)

    def test_description_must_be_string(self):
        with pytest.raises(TypeError):
            PlanningStrategy(description=123)

    def test_name_must_not_be_empty(self):
        with pytest.raises(ValueError):
            PlanningStrategy(name="")

    def test_repr(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
            description="Research planning",
        )

        result = repr(strategy)

        assert "PlanningStrategy" in result
        assert "ResearchStrategy" in result
        assert "Research planning" in result


class TestPlanningStrategyApply:
    def _make_plan(self) -> Plan:
        goal = Goal(
            description="Improve system",
            success_criteria=[
                "Increase reliability",
                "Reduce latency",
            ],
        )

        tasks = [
            Task(
                description="Analyze reliability",
                task_id="task-a",
            ),
            Task(
                description="Analyze latency",
                task_id="task-b",
            ),
        ]

        plan = Plan(
            goal=goal,
            tasks=tasks,
        )

        plan.set_metadata("owner", "planner")
        plan.set_metadata("priority", "high")

        return plan

    def test_apply_requires_plan(self):
        strategy = PlanningStrategy()

        with pytest.raises(TypeError):
            strategy.apply("not-a-plan")

    def test_apply_returns_new_plan(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert isinstance(result, Plan)
        assert result is not plan

    def test_apply_preserves_goal(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.goal is plan.goal

    def test_apply_preserves_tasks(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.tasks == plan.tasks
        assert len(result.tasks) == 2

    def test_apply_preserves_task_graph(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.task_graph is plan.task_graph

    def test_apply_preserves_constraints(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.constraints is plan.constraints

    def test_apply_preserves_existing_metadata(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
        )
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.metadata["owner"] == "planner"
        assert result.metadata["priority"] == "high"

    def test_apply_records_strategy(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
        )
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.metadata["strategy"] == "ResearchStrategy"

    def test_apply_does_not_mutate_input_metadata(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
        )
        plan = self._make_plan()

        original_metadata = dict(plan.metadata)

        strategy.apply(plan)

        assert plan.metadata == original_metadata
        assert "strategy" not in plan.metadata

    def test_apply_metadata_isolated(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
        )
        plan = self._make_plan()

        result = strategy.apply(plan)

        result.metadata["owner"] = "changed"

        assert plan.metadata["owner"] == "planner"


class TestPlanningStrategyDecomposeGoal:
    def test_decompose_requires_goal(self):
        strategy = PlanningStrategy()

        with pytest.raises(TypeError):
            strategy.decompose_goal("not-a-goal")

    def test_one_task_per_success_criterion(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=[
                "Increase reliability",
                "Reduce latency",
                "Reduce cost",
            ],
        )

        tasks = strategy.decompose_goal(goal)

        assert len(tasks) == 3
        assert all(isinstance(task, Task) for task in tasks)

    def test_task_descriptions_follow_criteria(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=[
                "Increase reliability",
                "Reduce latency",
            ],
        )

        tasks = strategy.decompose_goal(goal)

        assert tasks[0].description == (
            "Achieve criterion: Increase reliability"
        )
        assert tasks[1].description == (
            "Achieve criterion: Reduce latency"
        )

    def test_empty_success_criteria_creates_fallback_task(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=[],
        )

        tasks = strategy.decompose_goal(goal)

        assert len(tasks) == 1
        assert tasks[0].description == (
            "Plan execution for Improve system"
        )

    def test_decompose_returns_new_tasks(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=["Increase reliability"],
        )

        tasks_a = strategy.decompose_goal(goal)
        tasks_b = strategy.decompose_goal(goal)

        assert tasks_a is not tasks_b
        assert tasks_a[0] is not tasks_b[0]

    def test_decompose_does_not_mutate_goal(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=["Increase reliability"],
        )

        original = goal.to_dict()

        strategy.decompose_goal(goal)

        assert goal.to_dict() == original

    def test_generated_tasks_have_no_execution_state(self):
        strategy = PlanningStrategy()

        goal = Goal(
            description="Improve system",
            success_criteria=["Increase reliability"],
        )

        tasks = strategy.decompose_goal(goal)

        for task in tasks:
            assert not hasattr(task, "status")
            assert not hasattr(task, "result")
            assert not hasattr(task, "started_at")
            assert not hasattr(task, "completed_at")
            assert not hasattr(task, "error")
            assert not hasattr(task, "retry_count")


class TestPlanningStrategyInfo:
    def test_info(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
            description="Research planning",
        )

        info = strategy.info()

        assert info == {
            "name": "ResearchStrategy",
            "description": "Research planning",
            "type": "PlanningStrategy",
        }

    def test_info_returns_new_dictionary(self):
        strategy = PlanningStrategy(
            name="ResearchStrategy",
            description="Research planning",
        )

        info = strategy.info()
        info["name"] = "Changed"

        assert strategy.name == "ResearchStrategy"

    def test_info_contains_only_strategy_metadata(self):
        strategy = PlanningStrategy()

        info = strategy.info()

        assert set(info) == {
            "name",
            "description",
            "type",
        }