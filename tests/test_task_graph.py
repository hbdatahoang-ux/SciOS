"""
Tests for TaskGraph.
"""

import pytest

from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.task_graph import TaskGraph


def test_add_task():

    graph = TaskGraph()

    task = Task(
        description="Initialize system"
    )

    graph.add_task(
        "init",
        task,
    )

    assert "init" in graph.graph
    assert (
        graph.graph["init"]["task"].description
        == "Initialize system"
    )


def test_add_dependency():

    graph = TaskGraph()

    setup = Task(
        description="Setup environment"
    )

    deploy = Task(
        description="Deploy application"
    )

    graph.add_task(
        "setup",
        setup,
    )

    graph.add_task(
        "deploy",
        deploy,
    )

    graph.add_dependency(
        "deploy",
        "setup",
    )

    assert (
        "setup"
        in graph.graph["deploy"]["dependencies"]
    )


def test_topological_sort_valid():

    graph = TaskGraph()

    req = Task(
        description="Gather requirements"
    )

    design = Task(
        description="Design system"
    )

    impl = Task(
        description="Implement system"
    )

    graph.add_task("req", req)
    graph.add_task("design", design)
    graph.add_task("impl", impl)

    graph.add_dependency(
        "design",
        "req",
    )

    graph.add_dependency(
        "impl",
        "design",
    )

    order = graph.topological_sort()

    assert order == [
        "req",
        "design",
        "impl",
    ]


def test_topological_sort_cycle_detection():

    graph = TaskGraph()

    a = Task(description="A")
    b = Task(description="B")

    graph.add_task("a", a)
    graph.add_task("b", b)

    graph.add_dependency("a", "b")
    graph.add_dependency("b", "a")

    with pytest.raises(ValueError):
        graph.topological_sort()


def test_get_task():

    graph = TaskGraph()

    task = Task(
        description="Example"
    )

    graph.add_task(
        "example",
        task,
    )

    assert graph.get_task("example") is task


def test_unknown_task_returns_none():

    graph = TaskGraph()

    assert graph.get_task("missing") is None
    