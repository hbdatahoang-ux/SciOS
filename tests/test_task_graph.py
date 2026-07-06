# tests/test_task_graph.py

import pytest
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.task_graph import TaskGraph

def test_add_task():
    graph = TaskGraph()
    task = Task(description="Initialize system")
    graph.add_task("init", task)
    assert "init" in graph.graph
    assert graph.graph["init"]["task"].description == "Initialize system"

def test_add_dependency():
    graph = TaskGraph()
    t1 = Task(description="Setup environment")
    t2 = Task(description="Deploy application")
    graph.add_task("setup", t1)
    graph.add_task("deploy", t2)

    graph.add_dependency("deploy", "setup")
    assert "setup" in graph.graph["deploy"]["dependencies"]

def test_topological_sort_valid():
    graph = TaskGraph()
    t1 = Task(description="Gather requirements")
    t2 = Task(description="Design system")
    t3 = Task(description="Implement system")

    graph.add_task("req", t1)
    graph.add_task("design", t2)
    graph.add_task("impl", t3)

    graph.add_dependency("design", "req")
    graph.add_dependency("impl", "design")

    order = graph.topological_sort()
    assert order == ["req", "design", "impl"]

def test_topological_sort_cycle_detection():
    graph = TaskGraph()
    t1 = Task(description