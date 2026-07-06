# tests/test_strategy.py

import pytest
from scios.cognitive_core.planner.strategy import PlanningStrategy
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task

def test_strategy_initialization():
    strategy = PlanningStrategy(name="Greedy", description="Pick tasks with highest priority")
    assert strategy.name == "Greedy"
    assert "priority" in strategy.description

def test_strategy_apply_on_plan():
    strategy = PlanningStrategy(name="Simple", description="Execute tasks in order")
    tasks = [Task(description=f"Task {i}") for i in range(3)]
    plan = Plan(goal=Goal("Test goal"), tasks=tasks)

    new_plan = strategy.apply(plan)
    assert isinstance(new_plan, Plan)
    assert len(new_plan.tasks) == 3

def test_strategy_apply_preserves_goal():
    strategy = PlanningStrategy(name="PreserveGoal", description="Keep goal intact")
    plan = Plan(goal=Goal("Original goal"), tasks=[Task(description="T1")])
    new_plan = strategy.apply(plan)
    assert new_plan.goal.description == "Original goal"

def test_strategy_apply_modifies_metadata():
    strategy = PlanningStrategy(name="MetaUpdate", description="Update plan metadata")
    plan = Plan(goal=Goal("Meta goal"), tasks=[Task(description="T1")])
    new_plan = strategy.apply(plan)
    assert "strategy" in new_plan.metadata
    assert new_plan.metadata["strategy"] == "MetaUpdate"

def test_strategy_repr():
    strategy = PlanningStrategy(name="TestStrategy", description="For testing repr")
    assert "TestStrategy" in repr(strategy)
