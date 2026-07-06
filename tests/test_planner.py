# tests/test_planner.py

import pytest
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.plan import Plan

def test_planner_initialization():
    planner = Planner()
    assert planner is not None
    assert planner.state.get_state() == "initialized"

def test_planner_create_plan():
    planner = Planner()
    goal = Goal("Test goal")
    plan = planner.create_plan(goal, ["Task A", "Task B"])
    assert isinstance(plan, Plan)
    assert plan.goal.description == "Test goal"
    assert len(plan.tasks) == 2

def test_planner_execute_plan_success():
    planner = Planner()
    goal = Goal("Execution goal")
    plan = planner.create_plan(goal, ["Task 1", "Task 2"])
    result = planner.run(plan)
    assert result["valid"] is True
    assert plan.is_completed()
    assert planner.state.is_terminal()

def test_planner_execute_plan_failure():
    planner = Planner()
    goal = Goal("Failure goal")
    # tạo plan rỗng để gây lỗi
    plan = Plan(goal=goal, tasks=[])
    result = planner.run(plan)
    assert result["valid"] is False
    assert planner.state.get_state() == "failed"

def test_planner_status_schema():
    planner = Planner()
    goal = Goal("Status goal")
    plan = planner.create_plan(goal, ["Task X"])
    planner.run(plan)
    status = planner.status()
    required_keys = {"state", "goal", "tasks"}
    assert required_keys.issubset(status.keys())
