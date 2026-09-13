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

        assert result.task_graph is not plan.task_graph

    def test_apply_preserves_task_graph_structure(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        plan.task_graph.add_dependency("task-a", "task-b")

        result = strategy.apply(plan)

        assert set(result.task_graph.tasks) == {
            "task-a",
            "task-b",
        }

        assert result.task_graph.get_task("task-a") is (
            plan.task_graph.get_task("task-a")
        )

        assert result.task_graph.get_task("task-b") is (
            plan.task_graph.get_task("task-b")
        )

        assert result.task_graph.topological_sort() == [
            "task-b",
            "task-a",
        ]

    def test_apply_preserves_constraints(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.constraints is not plan.constraints

    def test_apply_preserves_constraint_content(self):
        strategy = PlanningStrategy()
        plan = self._make_plan()

        result = strategy.apply(plan)

        assert result.constraints.constraints == (
            plan.constraints.constraints
        )

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
