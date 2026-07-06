# tests/test_planner_execution.py

import pytest
from scios.cognitive_core.planner.planner_execution import PlannerExecution
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.task import Task

def test_execution_initialization():
    execution = PlannerExecution()
    assert execution is not None
    assert execution.state.get_state() == "initialized"

def test_execution_run_success():
    execution = PlannerExecution()
    goal = Goal("End-to-end success")
    tasks = [Task(description="Task A"), Task(description="Task B")]
    result = execution.run(goal, tasks)

    assert isinstance(result, dict)
    assert result["valid"] is True
    assert result["errors"] == []
    assert execution.state.is_terminal()

def test_execution_run_failure_empty_tasks():
    execution = PlannerExecution()
    goal = Goal("Failure goal")
    result = execution.run(goal, [])

    assert result["valid"] is False
    assert "No tasks" in result["errors"][0]
    assert execution.state.get_state() == "failed"

def test_execution_status_schema():
    execution = PlannerExecution()
    goal = Goal("Status goal")
    tasks = [Task(description="Task X")]
    execution.run(goal, tasks)
    status = execution.status()

    required_keys = {"state", "goal", "tasks", "result"}
    assert required_keys.issubset(status.keys())

def test_execution_reuse_after_run():
    execution = PlannerExecution()
    goal1 = Goal("First run")
    tasks1 = [Task(description="T1")]
    result1 = execution.run(goal1, tasks1)
    assert result1["valid"]

    goal2 = Goal("Second run")
    tasks2 = [Task(description="T2")]
    result2 = execution.run(goal2, tasks2)
    assert result2["valid"]
    assert tasks2[0].is_completed()
