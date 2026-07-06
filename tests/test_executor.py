# tests/test_executor.py

import pytest
from scios.cognitive_core.planner.executor import PlanExecutor
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal

def test_executor_create():
    executor = PlanExecutor()
    assert executor is not None

def test_executor_initial_state():
    executor = PlanExecutor()
    assert executor.get_log() == []

def test_executor_submit_and_execute_one():
    executor = PlanExecutor()
    task = Task(description="Do something")
    plan = Plan(goal=Goal("Test goal"), tasks=[task])
    executor.execute(plan)
    assert task.is_completed()
    assert "Executing task: Do something" in executor.get_log()[0]

def test_executor_execute_fifo():
    executor = PlanExecutor()
    t1 = Task(description="Task A")
    t2 = Task(description="Task B")
    plan = Plan(goal=Goal("FIFO goal"), tasks=[t1, t2])
    executor.execute(plan)
    logs = executor.get_log()
    assert logs[0].endswith("Task A")
    assert logs[1].endswith("Task B")

def test_executor_execute_all():
    executor = PlanExecutor()
    tasks = [Task(description=f"Task {i}") for i in range(5)]
    plan = Plan(goal=Goal("All tasks"), tasks=tasks)
    executor.execute(plan)
    assert all(t.is_completed() for t in tasks)
    assert plan.metadata["status"] == "executed"

def test_executor_clear_log():
    executor = PlanExecutor()
    t = Task(description="Clear test")
    plan = Plan(goal=Goal("Clear goal"), tasks=[t])
    executor.execute(plan)
    executor.execution_log.clear()
    assert executor.get_log() == []

def test_executor_status_metadata():
    executor = PlanExecutor()
    t = Task(description="Status test")
    plan = Plan(goal=Goal("Status goal"), tasks=[t])
    executor.execute(plan)
    assert plan.metadata["status"] == "executed"

def test_executor_empty_plan():
    executor = PlanExecutor()
    plan = Plan(goal=Goal("Empty goal"), tasks=[])
    with pytest.raises(ValueError):
        executor.execute(plan)

def test_executor_reuse_after_execution():
    executor = PlanExecutor()
    t1 = Task(description="First run")
    plan1 = Plan(goal=Goal("Reuse goal"), tasks=[t1])
    executor.execute(plan1)
    t2 = Task(description="Second run")
    plan2 = Plan(goal=Goal("Reuse goal 2"), tasks=[t2])
    executor.execute(plan2)
    assert t2.is_completed()
