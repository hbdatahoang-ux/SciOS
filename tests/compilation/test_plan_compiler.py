from __future__ import annotations

import pytest

from scios.cognitive_core.planner import Goal, Plan, Task, TaskGraph
from scios.compilation.plan_compiler import PlanCompiler
from scios.compilation.errors import (
    CyclicPlanError,
    InvalidPlanError,
)

from scios.execution.node.kind import NodeKind
from scios.execution.node.status import NodeStatus


def make_plan() -> Plan:
    goal = Goal(
        description="Analyze experimental data",
    )

    task_a = Task(
        description="Collect measurements",
        task_id="collect",
    )

    task_b = Task(
        description="Analyze measurements",
        task_id="analyze",
        dependencies=["collect"],
    )

    graph = TaskGraph()
    graph.add_task(task_a.id, task_a)
    graph.add_task(task_b.id, task_b)

    return Plan(
        goal=goal,
        tasks=[task_a, task_b],
        task_graph=graph,
    )


def test_compile_returns_execution_graph():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    assert graph is not None
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


def test_compile_creates_one_execution_node_per_task():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    assert len(graph.nodes) == len(plan.tasks)


def test_compile_preserves_task_provenance():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    source_task_ids = {
        node.metadata["source"]["task_id"]
        for node in graph.nodes.values()
    }

    assert source_task_ids == {"collect", "analyze"}


def test_compile_maps_task_description_to_node_name():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    names = {
        node.metadata["source"]["task_id"]: node.name
        for node in graph.nodes.values()
    }

    assert names == {
        "collect": "Collect measurements",
        "analyze": "Analyze measurements",
    }


def test_compile_maps_task_to_process_node():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    for node in graph.nodes.values():
        assert node.kind == NodeKind.PROCESS
        assert node.status == NodeStatus.READY


def test_compile_preserves_dependency_edge():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    collect_node = next(
        node
        for node in graph.nodes.values()
        if node.metadata["source"]["task_id"] == "collect"
    )

    analyze_node = next(
        node
        for node in graph.nodes.values()
        if node.metadata["source"]["task_id"] == "analyze"
    )

    edge = graph.edges[0]

    assert edge.source_id == collect_node.node_id
    assert edge.target_id == analyze_node.node_id
    assert edge.label == "dependency"


def test_execution_identity_is_distinct_from_task_identity():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    for node in graph.nodes.values():
        task_id = node.metadata["source"]["task_id"]

        assert node.node_id != task_id


def test_compile_preserves_task_metadata():
    goal = Goal(description="Test metadata")

    task = Task(
        description="Execute analysis",
        task_id="analysis",
    )

    task.metadata["experiment"] = "exp-01"

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    graph = PlanCompiler().compile(plan)

    node = next(iter(graph.nodes.values()))

    assert node.metadata["task_metadata"] == {
        "experiment": "exp-01",
    }


def test_compile_preserves_priority_constraint():
    goal = Goal(description="Priority test")

    task = Task(
        description="High priority task",
        task_id="priority-task",
        constraints={"priority": 10},
    )

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    graph = PlanCompiler().compile(plan)

    node = next(iter(graph.nodes.values()))

    assert node.metadata["priority"] == 10


def test_compile_does_not_mutate_plan():
    plan = make_plan()

    before = plan.to_dict()

    PlanCompiler().compile(plan)

    after = plan.to_dict()

    assert after == before


def test_compile_rejects_non_plan():
    with pytest.raises(InvalidPlanError):
        PlanCompiler().compile(None)


def test_compile_rejects_non_task_in_plan():
    plan = make_plan()
    plan.tasks.append("not-a-task")

    with pytest.raises(InvalidPlanError):
        PlanCompiler().compile(plan)


def test_compile_rejects_missing_dependency():
    goal = Goal(description="Missing dependency")

    task = Task(
        description="Analyze",
        task_id="analyze",
        dependencies=["missing"],
    )

    graph = TaskGraph()

    # Intentionally construct an invalid TaskGraph state.
    # TaskGraph.add_task() normally rejects this dependency.
    graph.tasks[task.id] = task
    graph.edges[task.id] = list(task.dependencies)

    plan = Plan(
        goal=goal,
        tasks=[task],
        task_graph=graph,
    )

    with pytest.raises(
        InvalidPlanError,
        match="Unknown dependency",
    ):
        PlanCompiler().compile(plan)


def test_compile_rejects_self_dependency():
    goal = Goal(description="Self dependency")

    task = Task(
        description="Recursive task",
        task_id="recursive",
    )

    task.dependencies = ["recursive"]

    graph = TaskGraph()

    # Intentionally construct an invalid TaskGraph state.
    graph.tasks[task.id] = task
    graph.edges[task.id] = ["recursive"]

    plan = Plan(
        goal=goal,
        tasks=[task],
        task_graph=graph,
    )

    with pytest.raises(CyclicPlanError):
        PlanCompiler().compile(plan)


def test_compiler_has_no_execution_responsibility():
    compiler = PlanCompiler()

    assert not hasattr(compiler, "execute")
    assert not hasattr(compiler, "schedule")
    assert not hasattr(compiler, "dispatch")
    assert not hasattr(compiler, "executor")
    assert not hasattr(compiler, "scheduler")


def test_compiler_only_performs_semantic_lowering():
    plan = make_plan()

    graph = PlanCompiler().compile(plan)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    # Compilation produces Execution IR only.
    # No runtime callable, tool result, or execution result
    # is attached by the compiler.
    for node in graph.nodes.values():
        assert "callable" not in node.metadata
        assert "tool" not in node.metadata
        assert "result" not in node.metadata