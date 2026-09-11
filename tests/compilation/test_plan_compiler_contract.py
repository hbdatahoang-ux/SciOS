from __future__ import annotations

import inspect

import pytest

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.node.kind import NodeKind
from scios.execution.node.status import NodeStatus

from scios.compilation.plan_compiler import PlanCompiler
from scios.compilation.errors import (
    CyclicPlanError,
    InvalidPlanError,
    MissingTaskDependencyError,
    PlanCompilationError,
)


def make_goal() -> Goal:
    return Goal(description="Test goal")


def make_plan(*tasks: Task) -> Plan:
    return Plan(
        goal=make_goal(),
        tasks=list(tasks),
    )


class TestPlanCompilerContract:
    """
    Contract tests for the Cognitive Plan -> ExecutionGraph boundary.

    PlanCompiler is a semantic compiler only.

    It MUST:
        Plan -> ExecutionGraph
        Task -> ExecutionNode
        dependency -> ExecutionEdge

    It MUST NOT:
        execute
        schedule
        resolve runtime callables
        mutate execution lifecycle
    """

    # ==========================================================
    # PC-01
    # Plan -> ExecutionGraph
    # ==========================================================

    def test_compile_returns_execution_graph(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        assert isinstance(graph, ExecutionGraph)

    # ==========================================================
    # PC-02
    # Exactly one Task -> exactly one ExecutionNode
    # ==========================================================

    def test_one_task_produces_exactly_one_execution_node(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        assert len(graph.nodes) == 1

        node = next(iter(graph.nodes.values()))

        assert isinstance(node, ExecutionNode)

    # ==========================================================
    # PC-03
    # Task.description -> ExecutionNode.name
    # ==========================================================

    def test_task_description_maps_to_execution_node_name(self):
        task = Task(
            description="Acquire experimental data",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.name == "Acquire experimental data"

    # ==========================================================
    # PC-04
    # Task.id -> execution provenance
    # ==========================================================

    def test_task_id_is_preserved_as_provenance(self):
        task = Task(
            description="Acquire experimental data",
            task_id="task-a-123",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert "source" in node.metadata
        assert node.metadata["source"]["type"] == "cognitive_task"
        assert node.metadata["source"]["task_id"] == "task-a-123"

    # ==========================================================
    # PC-05
    # Task -> NodeKind.PROCESS
    # ==========================================================

    def test_task_maps_to_process_node(self):
        task = Task(
            description="Acquire experimental data",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.kind is NodeKind.PROCESS

    # ==========================================================
    # PC-06
    # Compiled node starts in READY state
    # ==========================================================

    def test_compiled_node_starts_ready(self):
        task = Task(
            description="Acquire experimental data",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.status is NodeStatus.READY

    # ==========================================================
    # PC-07
    # Task dependency -> ExecutionEdge
    #
    # Cognitive:
    #
    #     B depends_on A
    #
    # TaskGraph representation:
    #
    #     edges["B"] = ["A"]
    #
    # ExecutionGraph representation:
    #
    #     A -> B
    #
    # prerequisite -> dependent
    # ==========================================================

    def test_task_dependency_maps_to_execution_edge(self):
        task_a = Task(
            description="Acquire data",
            task_id="task-a",
        )

        task_b = Task(
            description="Analyze data",
            task_id="task-b",
            dependencies=["task-a"],
        )

        plan = make_plan(
            task_a,
            task_b,
        )

        graph = PlanCompiler().compile(plan)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

        node_by_task_id = {
            node.metadata["source"]["task_id"]: node
            for node in graph.nodes.values()
        }

        node_a = node_by_task_id["task-a"]
        node_b = node_by_task_id["task-b"]

        edge = graph.edges[0]

        assert edge.source_id == node_a.node_id
        assert edge.target_id == node_b.node_id
        assert edge.relation == "dependency"

    # ==========================================================
    # PC-07b
    # TaskGraph.edges is the canonical dependency source
    #
    # TaskGraph owns topology.
    #
    # This regression test deliberately makes the Task-level
    # dependency mirror disagree with TaskGraph.edges.
    #
    # The compiler MUST lower dependencies from TaskGraph.edges,
    # not from Task.dependencies.
    # ==========================================================

    def test_compiler_uses_task_graph_edges_as_dependency_source(self):
        task_a = Task(
            description="Acquire data",
            task_id="task-a",
        )

        task_b = Task(
            description="Analyze data",
            task_id="task-b",
        )

        plan = make_plan(
            task_a,
            task_b,
        )

        # TaskGraph owns canonical topology.
        plan.task_graph.edges["task-b"] = ["task-a"]

        # Deliberately make the Task-level mirror disagree.
        task_b.dependencies = []

        graph = PlanCompiler().compile(plan)

        node_by_task_id = {
            node.metadata["source"]["task_id"]: node
            for node in graph.nodes.values()
        }

        node_a = node_by_task_id["task-a"]
        node_b = node_by_task_id["task-b"]

        assert len(graph.edges) == 1

        edge = graph.edges[0]

        assert edge.source_id == node_a.node_id
        assert edge.target_id == node_b.node_id
        assert edge.relation == "dependency"

    # ==========================================================
    # PC-08
    # Compiler MUST NOT execute
    #
    # This contract checks that compilation does not transition
    # the generated node into an execution lifecycle state.
    # ==========================================================

    def test_compiler_does_not_execute(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        compiler = PlanCompiler()
        graph = compiler.compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.status is NodeStatus.READY

        assert not hasattr(compiler, "execute")

    # ==========================================================
    # PC-09
    # Compiler MUST NOT schedule
    # ==========================================================

    def test_compiler_does_not_schedule(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        compiler = PlanCompiler()

        graph = compiler.compile(plan)

        assert isinstance(graph, ExecutionGraph)

        assert not hasattr(compiler, "schedule")
        assert not hasattr(compiler, "scheduler")

    # ==========================================================
    # PC-10
    # Compiler MUST NOT resolve or invoke runtime callable
    #
    # The compiler creates semantic execution IR only.
    # Runtime operation resolution belongs downstream.
    # ==========================================================

    def test_compiler_does_not_resolve_runtime_callable(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        compiler = PlanCompiler()
        graph = compiler.compile(plan)

        node = next(iter(graph.nodes.values()))

        assert isinstance(node, ExecutionNode)

        # No runtime callable should be attached/resolved
        # by the compiler.
        assert not callable(getattr(node, "handler", None))

    # ==========================================================
    # PC-11
    # Invalid input -> explicit PlanCompilationError
    # ==========================================================

    def test_invalid_plan_input_fails_explicitly(self):
        compiler = PlanCompiler()

        with pytest.raises(PlanCompilationError):
            compiler.compile(None)

    # ==========================================================
    # Additional structural contract
    # ==========================================================

    def test_compiler_exposes_compile_as_primary_boundary(self):
        compiler = PlanCompiler()

        assert hasattr(compiler, "compile")
        assert callable(compiler.compile)

    # ==========================================================
    # Additional provenance contract
    # ==========================================================

    def test_compilation_does_not_use_task_id_as_runtime_node_id(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )
        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.metadata["source"]["task_id"] == "task-a"

        # Runtime identity is an ExecutionNode UUID, not the
        # cognitive Task string identifier.
        assert node.node_id != "task-a"

    # ==========================================================
    # Additional topology contract
    # ==========================================================

    def test_compilation_does_not_duplicate_topology_in_parent_children(self):
        task_a = Task(
            description="Acquire data",
            task_id="task-a",
        )

        task_b = Task(
            description="Analyze data",
            task_id="task-b",
            dependencies=["task-a"],
        )

        plan = make_plan(
            task_a,
            task_b,
        )

        graph = PlanCompiler().compile(plan)

        node_by_task_id = {
            node.metadata["source"]["task_id"]: node
            for node in graph.nodes.values()
        }

        node_a = node_by_task_id["task-a"]
        node_b = node_by_task_id["task-b"]

        # ExecutionGraph.edges is the canonical topology.
        assert len(graph.edges) == 1

        # Compiler must not create a second topology representation
        # through ExecutionNode.parent/children.
        assert not hasattr(node_a, "parent")
        assert not hasattr(node_a, "children")

        assert not hasattr(node_b, "parent")
        assert not hasattr(node_b, "children")

    # ==========================================================
    # Additional API boundary contract
    # ==========================================================

    def test_compile_accepts_one_plan_argument(self):
        signature = inspect.signature(PlanCompiler.compile)

        parameters = list(signature.parameters.values())

        assert len(parameters) == 2
        assert parameters[0].name == "self"
        assert parameters[1].name == "plan"
    # ==========================================================
    # PC-12
    # Invalid Plan.tasks entry -> InvalidPlanError
    # ==========================================================

    def test_invalid_task_entry_fails_explicitly(self):
        compiler = PlanCompiler()

        plan = make_plan(
            Task(
                description="Valid task",
                task_id="task-a",
            )
        )

        plan.tasks.append("not-a-task")

        with pytest.raises(InvalidPlanError):
            compiler.compile(plan)

    # ==========================================================
    # PC-13
    # Missing TaskGraph dependency -> MissingTaskDependencyError
    # ==========================================================

    def test_missing_task_dependency_fails_explicitly(self):
        task = Task(
            description="Analyze data",
            task_id="task-b",
        )

        plan = make_plan(task)

        plan.task_graph.edges["task-b"] = ["missing-task"]

        with pytest.raises(MissingTaskDependencyError):
            PlanCompiler().compile(plan)

    # ==========================================================
    # PC-14
    # Self dependency -> CyclicPlanError
    # ==========================================================

    def test_self_dependency_fails_as_cyclic_plan(self):
        task = Task(
            description="Self dependent task",
            task_id="task-a",
        )

        plan = make_plan(task)

        plan.task_graph.edges["task-a"] = ["task-a"]

        with pytest.raises(CyclicPlanError):
            PlanCompiler().compile(plan)

    # ==========================================================
    # PC-15
    # Cyclic Plan -> CyclicPlanError
    # ==========================================================

    def test_cyclic_plan_fails_explicitly(self):
        task_a = Task(
            description="Task A",
            task_id="task-a",
        )

        task_b = Task(
            description="Task B",
            task_id="task-b",
        )

        plan = make_plan(
            task_a,
            task_b,
        )

        plan.task_graph.edges["task-a"] = ["task-b"]
        plan.task_graph.edges["task-b"] = ["task-a"]

        with pytest.raises(CyclicPlanError):
            PlanCompiler().compile(plan)

    # ==========================================================
    # PC-16
    # Successful compilation MUST produce a valid ExecutionGraph
    # ==========================================================

    def test_compiled_execution_graph_is_valid(self):
        task_a = Task(
            description="Acquire data",
            task_id="task-a",
        )

        task_b = Task(
            description="Analyze data",
            task_id="task-b",
            dependencies=["task-a"],
        )

        plan = make_plan(
            task_a,
            task_b,
        )

        graph = PlanCompiler().compile(plan)

        graph.validate()

    # ==========================================================
    # PC-17
    # Provenance source type -> cognitive_task
    # ==========================================================

    def test_compiled_node_has_cognitive_task_provenance(self):
        task = Task(
            description="Perform task A",
            task_id="task-a",
        )

        plan = make_plan(task)

        graph = PlanCompiler().compile(plan)

        node = next(iter(graph.nodes.values()))

        assert node.metadata["source"]["type"] == "cognitive_task"