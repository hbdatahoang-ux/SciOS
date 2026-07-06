# tests/test_task.py

import pytest
from scios.cognitive_core.planner.task import Task

def test_task_initialization():
    task = Task(description="Collect customer feedback")
    assert task.description == "Collect customer feedback"
    assert task.completed is False
    assert task.constraints == {}
    assert task.dependencies == []

def test_mark_completed():
    task = Task(description="Prepare report")
    assert task.is_completed() is False
    task.mark_completed()
    assert task.is_completed() is True

def test_add_constraint():
    task = Task(description="Design prototype")
    task.add_constraint("priority", 5)
    assert task.constraints["priority"] == 5

def test_add_dependency():
    task = Task(description="Deploy system")
    task.add_dependency("setup_environment")
    assert "setup_environment" in task.dependencies
    assert len(task.dependencies) == 1

def test_multiple_constraints_and_dependencies():
    task = Task(description="Run marketing campaign")
    task.add_constraint("budget", 10000)
    task.add_constraint("deadline", "2026-07-10")
    task.add_dependency("design_materials")
    task.add_dependency("approve_budget")

    assert task.constraints["budget"] == 10000
    assert task.constraints["deadline"] == "2026-07-10"
    assert "design_materials" in task.dependencies
    assert "approve_budget" in task.dependencies
