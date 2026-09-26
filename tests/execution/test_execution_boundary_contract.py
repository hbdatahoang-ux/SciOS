from __future__ import annotations

from scios.cognitive_core.planner import Goal, Plan, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.execution.runner import ExecutionRunner
from scios.execution.scheduler import Scheduler
from scios.runtime.executor import Executor


class _TestOperationBinder:
    def __init__(self, mapping: dict[str, OperationRef]) -> None:
        self.mapping = mapping
        self.calls: list[str] = []

    def bind(self, task: Task) -> OperationRef:
        self.calls.append(task.id)
        return self.mapping[task.id]


def test_plan_to_runtime_execution_boundary_contract() -> None:
    """
    Golden integration contract for the Plan -> Runtime execution boundary.

    Contract:
        Plan
          -> PlanCompiler
          -> ExecutionGraph
          -> Graph Scheduler
          -> ExecutionRunner
          -> OperationResolver
          -> Runtime Executor

    Success path:
        A -> B -> C executes strictly in dependency order.

    Failure path:
        A succeeds, B fails, C remains WAITING and is never executed.
    """

    # ------------------------------------------------------------------
    # Operations: runtime callables are registered independently from
    # cognitive planning objects.
    # ------------------------------------------------------------------
    success_calls: list[str] = []

    def operation_a() -> str:
        success_calls.append("A")
        return "result-A"

    def operation_b() -> str:
        success_calls.append("B")
        return "result-B"

    def operation_c() -> str:
        success_calls.append("C")
        return "result-C"

    refs = {
        "a": OperationRef("test.operation.a", "1.0"),
        "b": OperationRef("test.operation.b", "1.0"),
        "c": OperationRef("test.operation.c", "1.0"),
    }

    registry = OperationRegistry()
    registry.register(refs["a"], operation_a)
    registry.register(refs["b"], operation_b)
    registry.register(refs["c"], operation_c)

    resolver = OperationResolver(registry)

    # ------------------------------------------------------------------
    # Cognitive Plan: A -> B -> C.
    # ------------------------------------------------------------------
    plan = Plan(
        goal=Goal("Execute A, B, C in dependency order"),
        tasks=[
            Task("A", task_id="a"),
            Task("B", task_id="b", dependencies=["a"]),
            Task("C", task_id="c", dependencies=["b"]),
        ],
    )

    binder = _TestOperationBinder(refs)
    graph = PlanCompiler(operation_binder=binder).compile(plan)

    # ------------------------------------------------------------------
    # Compiler contract.
    # ------------------------------------------------------------------
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    nodes_by_task = {
        node.metadata["source"]["task_id"]: node
        for node in graph.nodes.values()
    }

    assert nodes_by_task["a"].operation_ref == refs["a"]
    assert nodes_by_task["b"].operation_ref == refs["b"]
    assert nodes_by_task["c"].operation_ref == refs["c"]

    # ------------------------------------------------------------------
    # Execution boundary.
    # Scheduler owns dependency readiness.
    # Runner owns the scheduler -> resolver -> runtime boundary.
    # Runtime Executor owns callable invocation.
    # ------------------------------------------------------------------
    scheduler = Scheduler(graph)
    runner = ExecutionRunner(
        scheduler=scheduler,
        resolver=resolver,
        executor=Executor(),
    )

    executed: list[str] = []

    # A must be the first released node.
    node = runner.run_next()
    assert node is not None
    assert node.metadata["source"]["task_id"] == "a"
    assert node.is_terminal()
    assert node.status.name == "SUCCESS"

    executed.append(node.metadata["source"]["task_id"])

    # B becomes READY only after A succeeds.
    node = runner.run_next()
    assert node is not None
    assert node.metadata["source"]["task_id"] == "b"
    assert node.status.name == "SUCCESS"

    executed.append(node.metadata["source"]["task_id"])

    # C becomes READY only after B succeeds.
    node = runner.run_next()
    assert node is not None
    assert node.metadata["source"]["task_id"] == "c"
    assert node.status.name == "SUCCESS"

    executed.append(node.metadata["source"]["task_id"])

    assert executed == ["a", "b", "c"]
    assert success_calls == ["A", "B", "C"]

    # No fourth node exists.
    assert runner.run_next() is None

    # ------------------------------------------------------------------
    # Failure propagation contract.
    #
    # Rebuild the graph so the test proves the behavior independently
    # from the successful execution above.
    # ------------------------------------------------------------------
    failure_calls: list[str] = []

    def failing_a() -> str:
        failure_calls.append("A")
        return "result-A"

    def failing_b() -> str:
        failure_calls.append("B")
        raise RuntimeError("B failed")

    def blocked_c() -> str:
        failure_calls.append("C")
        return "result-C"

    failure_refs = {
        "a": OperationRef("test.failure.a", "1.0"),
        "b": OperationRef("test.failure.b", "1.0"),
        "c": OperationRef("test.failure.c", "1.0"),
    }

    failure_registry = OperationRegistry()
    failure_registry.register(failure_refs["a"], failing_a)
    failure_registry.register(failure_refs["b"], failing_b)
    failure_registry.register(failure_refs["c"], blocked_c)

    failure_plan = Plan(
        goal=Goal("Verify failure propagation"),
        tasks=[
            Task("A", task_id="a"),
            Task("B", task_id="b", dependencies=["a"]),
            Task("C", task_id="c", dependencies=["b"]),
        ],
    )

    failure_binder = _TestOperationBinder(failure_refs)
    failure_graph = PlanCompiler(
        operation_binder=failure_binder
    ).compile(failure_plan)

    failure_nodes = {
        node.metadata["source"]["task_id"]: node
        for node in failure_graph.nodes.values()
    }

    failure_scheduler = Scheduler(failure_graph)
    failure_runner = ExecutionRunner(
        scheduler=failure_scheduler,
        resolver=OperationResolver(failure_registry),
        executor=Executor(),
    )

    # A succeeds.
    node = failure_runner.run_next()
    assert node is failure_nodes["a"]
    assert node.status.name == "SUCCESS"

    # B executes and fails. Runtime failure is reflected on the node.
    node = failure_runner.run_next()
    assert node is failure_nodes["b"]
    assert node.status.name == "FAILED"

    # Failed B must NOT release C.
    assert failure_nodes["c"].status.name == "WAITING"
    assert failure_runner.run_next() is None

    # C must never have reached the runtime executor.
    assert failure_calls == ["A", "B"]
