# tests/test_context.py

import pytest
from scios.cognitive_core.planner.context import Context
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task


def test_context_initialization():
    ctx = Context()
    assert ctx.current_goal is None
    assert ctx.current_plan is None
    assert ctx.metadata == {}
    assert ctx.log == []


def test_context_set_goal_and_plan():
    ctx = Context()
    goal = Goal("Test goal")
    tasks = [Task(description="Task 1"), Task(description="Task 2")]
    plan = Plan(goal=goal, tasks=tasks)

    ctx.set_goal(goal)
    ctx.set_plan(plan)

    assert ctx.current_goal == goal
    assert ctx.current_plan == plan
    assert ctx.current_plan.goal.description == "Test goal"


def test_context_add_task_and_log():
    ctx = Context()
    task = Task(description="New Task")

    ctx.add_task(task)
    assert task in ctx.tasks
    ctx.add_log("Added new task")
    assert "Added new task" in ctx.log


def test_context_reset():
    ctx = Context()
    goal = Goal("Reset goal")
    plan = Plan(goal=goal, tasks=[Task(description="Task X")])
    ctx.set_goal(goal)
    ctx.set_plan(plan)
    ctx.add_log("Something happened")

    ctx.reset()
    assert ctx.current_goal is None
    assert ctx.current_plan is None
    assert ctx.log == []
    assert ctx.metadata == {}


def test_context_to_dict_schema():
    ctx = Context()
    goal = Goal("Schema goal")
    plan = Plan(goal=goal, tasks=[Task(description="Schema task")])
    ctx.set_goal(goal)
    ctx.set_plan(plan)
    ctx.add_log("Schema log")

    data = ctx.to_dict()
    required_keys = {"goal", "plan", "metadata", "log"}
    assert required_keys.issubset(data.keys())
    assert data["goal"]["description"] == "Schema goal"
    assert isinstance(data["plan"]["tasks"], list)
    assert "Schema log" in data["log"]
