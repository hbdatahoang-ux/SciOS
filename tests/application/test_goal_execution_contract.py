from __future__ import annotations

import ast
import inspect

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.compilation.operation_binder import OperationBinder
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor


class ContractBinder(OperationBinder):
    def __init__(
        self,
        mapping: dict[str, OperationRef],
    ) -> None:
        self.mapping = mapping
        self.calls: list[str] = []

    def bind(self, task: Task) -> OperationRef:
        self.calls.append(task.id)
        return self.mapping[task.id]


def test_goal_execution_service_contract_exists():
    from scios.application.goal_execution import (
        GoalExecutionResult,
        GoalExecutionService,
    )

    assert GoalExecutionService is not None
    assert GoalExecutionResult is not None

    parameters = inspect.signature(
        GoalExecutionService
    ).parameters

    assert "planner" in parameters
    assert "compiler" in parameters
    assert "resolver" in parameters
    assert "executor" in parameters


def test_goal_execution_service_exposes_execute_contract():
    from scios.application.goal_execution import GoalExecutionService

    parameters = inspect.signature(
        GoalExecutionService.execute
    ).parameters

    assert "goal" in parameters
    assert "tasks" in parameters


def test_goal_to_runtime_boundary_contract():
    from scios.application.goal_execution import GoalExecutionService

    calls: list[str] = []

    def operation_a():
        calls.append("A")
        return "A"

    def operation_b():
        calls.append("B")
        return "B"

    registry = OperationRegistry()

    ref_a = OperationRef("contract.a", "1.0")
    ref_b = OperationRef("contract.b", "1.0")

    registry.register(ref_a, operation_a)
    registry.register(ref_b, operation_b)

    resolver = OperationResolver(registry)

    binder = ContractBinder(
        {
            "a": ref_a,
            "b": ref_b,
        }
    )

    compiler = PlanCompiler(
        operation_binder=binder,
    )

    service = GoalExecutionService(
        planner=Planner(),
        compiler=compiler,
        resolver=resolver,
        executor=Executor(),
    )

    goal = Goal(
        description="Execute contract workflow",
    )

    tasks = [
        Task(
            description="A",
            task_id="a",
        ),
        Task(
            description="B",
            task_id="b",
            dependencies=["a"],
        ),
    ]

    result = service.execute(
        goal,
        tasks=tasks,
    )

    assert result.goal is goal
    assert result.plan.goal is goal
    assert len(result.plan.tasks) == 2

    assert isinstance(result.graph, ExecutionGraph)
    assert len(result.graph.nodes) == 2
    assert len(result.graph.edges) == 1

    assert binder.calls == ["a", "b"]

    refs = {
        node.operation_ref
        for node in result.graph.nodes.values()
    }

    assert refs == {ref_a, ref_b}

    assert calls == ["A", "B"]


def _module_source() -> str:
    import scios.application.goal_execution as module

    return inspect.getsource(module)


def test_goal_execution_service_has_no_runtime_engine_reference():
    source = _module_source()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id != "RuntimeEngine"

        elif isinstance(node, ast.Attribute):
            assert node.attr != "RuntimeEngine"


def test_goal_execution_service_has_no_runtime_engine_import():
    source = _module_source()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "runtime.engine" not in alias.name

        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""

            assert module_name != "scios.runtime.engine"
            assert not module_name.endswith(".runtime.engine")

            for alias in node.names:
                assert alias.name != "RuntimeEngine"


def test_goal_execution_service_dependency_boundary():
    source = _module_source()
    tree = ast.parse(source)

    forbidden_imports = {
        "scios.runtime.engine",
        "scios.runtime.scheduler",
        "scios.runtime.worker",
        "scios.runtime.context",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_imports

        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            assert module_name not in forbidden_imports

def test_goal_execution_service_failure_semantics():
    from scios.application.goal_execution import GoalExecutionService
    from scios.execution.node.status import NodeStatus

    calls: list[str] = []

    def operation_a():
        calls.append("A")
        return "A"

    def operation_b():
        calls.append("B")
        raise RuntimeError("B failed")

    def operation_c():
        calls.append("C")
        return "C"

    registry = OperationRegistry()

    ref_a = OperationRef("contract.failure.a", "1.0")
    ref_b = OperationRef("contract.failure.b", "1.0")
    ref_c = OperationRef("contract.failure.c", "1.0")

    registry.register(ref_a, operation_a)
    registry.register(ref_b, operation_b)
    registry.register(ref_c, operation_c)

    resolver = OperationResolver(registry)

    binder = ContractBinder(
        {
            "a": ref_a,
            "b": ref_b,
            "c": ref_c,
        }
    )

    compiler = PlanCompiler(
        operation_binder=binder,
    )

    service = GoalExecutionService(
        planner=Planner(),
        compiler=compiler,
        resolver=resolver,
        executor=Executor(),
    )

    goal = Goal(
        description="Verify application failure semantics",
    )

    tasks = [
        Task(
            description="A",
            task_id="a",
        ),
        Task(
            description="B",
            task_id="b",
            dependencies=["a"],
        ),
        Task(
            description="C",
            task_id="c",
            dependencies=["b"],
        ),
    ]

    result = service.execute(
        goal,
        tasks=tasks,
    )

    nodes = {
        node.metadata["source"]["task_id"]: node
        for node in result.graph.nodes.values()
    }

    assert nodes["a"].status is NodeStatus.SUCCESS
    assert nodes["b"].status is NodeStatus.FAILED
    assert nodes["c"].status is NodeStatus.WAITING

    assert calls == ["A", "B"]

    assert result.goal is goal
    assert result.plan.goal is goal
    assert result.graph is not None
