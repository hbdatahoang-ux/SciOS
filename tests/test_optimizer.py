# tests/test_optimizer.py

import pytest
from scios.cognitive_core.planner.optimizer import PlanOptimizer
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task

def test_optimizer_initialization():
    optimizer = PlanOptimizer(name="BasicOptimizer")
    assert optimizer.name == "BasicOptimizer"

def test_optimizer_apply_on_plan():
    optimizer = PlanOptimizer(name="SimpleOptimizer")
    tasks = [Task(description=f"Task {i}") for i in range(3)]
    plan = Plan(goal=Goal("Optimization goal"), tasks=tasks)

    new_plan = optimizer.optimize(plan)
    assert isinstance(new_plan, Plan)
    assert len(new_plan.tasks) == 3

def test_optimizer_preserves_goal():
    optimizer = PlanOptimizer(name="PreserveGoalOptimizer")
    plan = Plan(goal=Goal("Original goal"), tasks=[Task(description="T1")])
    new_plan = optimizer.optimize(plan)
    assert new_plan.goal.description == "Original goal"

def test_optimizer_modifies_metadata():
    optimizer = PlanOptimizer(name="MetaOptimizer")
    plan = Plan(goal=Goal("Meta goal"), tasks=[Task(description="T1")])
    new_plan = optimizer.optimize(plan)
    assert "optimized_by" in new_plan.metadata
    assert new_plan.metadata["optimized_by"] == "MetaOptimizer"

def test_optimizer_repr():
    optimizer = PlanOptimizer(name="ReprOptimizer")
    assert "ReprOptimizer" in repr(optimizer)
