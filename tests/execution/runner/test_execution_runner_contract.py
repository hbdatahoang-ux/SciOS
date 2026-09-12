from __future__ import annotations

from scios.cognitive_core.planner import Goal, Plan, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.node.status import NodeStatus
from scios.execution.operation.ref import OperationRef
from scios.execution.scheduler.scheduler import Scheduler


class _TestOperationBinder:
    def __init__(self, operations: dict[str, OperationRef]) -> None:
        self.operations = operations

    def bind(self, task: Task) -> OperationRef:
        return self.operations[task.id]


def _make_three_node_plan() -> Plan:
    a = Task("A", task_id="a")
    b = Task("B", task_id="b", dependencies=["a"])
    c = Task("C", task_id="c", dependencies=["b"])

    return Plan(
        goal=Goal("A ? B ? C"),
        tasks=[a, b, c],
    )


def _compile_three_node_graph():
    binder = _TestOperationBinder(
        {
            "a": OperationRef("test.a", "1.0"),
            "b": OperationRef("test.b", "1.0"),
            "c": OperationRef("test.c", "1.0"),
        }
    )

    return PlanCompiler(
        operation_binder=binder,
    ).compile(
        _make_three_node_plan()
    )


def test_execution_runner_contract_three_node_dependency_order():
    """
    Contract:

        A ? B ? C

    Only the graph scheduler may expose a dependency-ready node.

    Expected lifecycle:

        A READY
        A SUCCESS
        B READY
        B SUCCESS
        C READY
        C SUCCESS

    This test intentionally does not require an ExecutionRunner
    implementation yet. It defines the behavior that the runner
    must satisfy.
    """
    graph = _compile_three_node_graph()
    scheduler = Scheduler(graph)

    a = graph.get_node(
        next(
            node_id
            for node_id, node in graph.nodes.items()
            if node.operation_ref == OperationRef("test.a", "1.0")
        )
    )
    b = graph.get_node(
        next(
            node_id
            for node_id, node in graph.nodes.items()
            if node.operation_ref == OperationRef("test.b", "1.0")
        )
    )
    c = graph.get_node(
        next(
            node_id
            for node_id, node in graph.nodes.items()
            if node.operation_ref == OperationRef("test.c", "1.0")
        )
    )

    assert a is not None
    assert b is not None
    assert c is not None

    # Initial readiness: only A may execute.
    assert a.status is NodeStatus.READY
    assert b.status is NodeStatus.WAITING
    assert c.status is NodeStatus.WAITING

    selected = scheduler.next()

    assert selected is a

    # B and C must remain blocked while A has not completed.
    assert scheduler.next() is None
    assert b.status is NodeStatus.WAITING
    assert c.status is NodeStatus.WAITING

    # A completes successfully.
    a.mark_success()
    scheduler.notify_completed(a)

    assert a.status is NodeStatus.SUCCESS
    assert b.status is NodeStatus.READY
    assert c.status is NodeStatus.WAITING

    # Now and only now B becomes executable.
    selected = scheduler.next()

    assert selected is b

    assert c.status is NodeStatus.WAITING
    assert scheduler.next() is None

    # B completes successfully.
    b.mark_success()
    scheduler.notify_completed(b)

    assert b.status is NodeStatus.SUCCESS
    assert c.status is NodeStatus.READY

    # Now and only now C becomes executable.
    selected = scheduler.next()

    assert selected is c

    # No further node is available.
    assert scheduler.next() is None

    # C completes successfully.
    c.mark_success()
    scheduler.notify_completed(c)

    assert c.status is NodeStatus.SUCCESS


def test_execution_runner_contract_must_not_execute_blocked_nodes():
    """
    A runner must never execute a node that the graph scheduler
    has not released as READY.
    """
    graph = _compile_three_node_graph()
    scheduler = Scheduler(graph)

    selected = scheduler.next()

    assert selected is not None
    assert selected.operation_ref == OperationRef("test.a", "1.0")

    # B and C are structurally blocked.
    assert graph.successors(selected.node_id)

    successors = graph.successors(selected.node_id)

    assert len(successors) == 1
    assert successors[0].status is NodeStatus.WAITING

    # Without completion notification, B cannot become READY.
    assert scheduler.next() is None

    selected.mark_success()
    scheduler.notify_completed(selected)

    next_node = scheduler.next()

    assert next_node is not None
    assert next_node.operation_ref == OperationRef("test.b", "1.0")
