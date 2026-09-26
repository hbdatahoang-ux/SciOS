from __future__ import annotations

from scios.cognitive_core.planner import Goal, Plan, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.node.status import NodeStatus
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.execution.scheduler.scheduler import Scheduler
from scios.runtime.executor import Executor
from scios.execution.runner import ExecutionRunner


def _make_plan() -> Plan:
    a = Task("A", task_id="a")
    b = Task("B", task_id="b", dependencies=["a"])
    c = Task("C", task_id="c", dependencies=["b"])

    return Plan(
        goal=Goal("A ? B ? C"),
        tasks=[a, b, c],
    )


def _make_system(executed: list[str]):
    def operation_a():
        executed.append("A")
        return "result-A"

    def operation_b():
        executed.append("B")
        return "result-B"

    def operation_c():
        executed.append("C")
        return "result-C"

    operations = {
        "a": (OperationRef("test.a", "1.0"), operation_a),
        "b": (OperationRef("test.b", "1.0"), operation_b),
        "c": (OperationRef("test.c", "1.0"), operation_c),
    }

    registry = OperationRegistry()

    for ref, operation in operations.values():
        registry.register(ref, operation)

    resolver = OperationResolver(registry)

    class Binder:
        def bind(self, task: Task) -> OperationRef:
            return operations[task.id][0]

    plan = _make_plan()
    graph = PlanCompiler(operation_binder=Binder()).compile(plan)

    scheduler = Scheduler(graph)
    executor = Executor()

    runner = ExecutionRunner(
        scheduler=scheduler,
        resolver=resolver,
        executor=executor,
    )

    return runner, graph, operations


def _node_by_operation_ref(graph, ref: OperationRef):
    return next(
        node
        for node in graph.nodes.values()
        if node.operation_ref == ref
    )


def test_execution_runner_contract_three_node_e2e():
    """
    End-to-end ExecutionRunner contract.

        Plan
          ?
        PlanCompiler
          ?
        ExecutionGraph
          ?
        Scheduler
          ?
        ExecutionRunner
          +- resolve(OperationRef)
          +- ExecutionContext(callable)
          +- Runtime Executor.execute()
          +- node lifecycle update
          +- scheduler.notify_completed()

    Dependency contract:

        A ? B ? C

        A executes
        ? A SUCCESS
        ? B READY

        B executes
        ? B SUCCESS
        ? C READY

        C executes
        ? C SUCCESS
    """
    executed: list[str] = []

    runner, graph, operations = _make_system(executed)

    ref_a = operations["a"][0]
    ref_b = operations["b"][0]
    ref_c = operations["c"][0]

    node_a = _node_by_operation_ref(graph, ref_a)
    node_b = _node_by_operation_ref(graph, ref_b)
    node_c = _node_by_operation_ref(graph, ref_c)

    # Nothing executes before Runner starts.
    assert executed == []

    assert node_a.status is NodeStatus.READY
    assert node_b.status is NodeStatus.WAITING
    assert node_c.status is NodeStatus.WAITING

    # ------------------------------------------------------------
    # A
    # ------------------------------------------------------------
    result = runner.run_next()

    assert result is node_a
    assert executed == ["A"]

    assert node_a.status is NodeStatus.SUCCESS
    assert node_b.status is NodeStatus.READY
    assert node_c.status is NodeStatus.WAITING

    # ------------------------------------------------------------
    # B
    # ------------------------------------------------------------
    result = runner.run_next()

    assert result is node_b
    assert executed == ["A", "B"]

    assert node_a.status is NodeStatus.SUCCESS
    assert node_b.status is NodeStatus.SUCCESS
    assert node_c.status is NodeStatus.READY

    # ------------------------------------------------------------
    # C
    # ------------------------------------------------------------
    result = runner.run_next()

    assert result is node_c
    assert executed == ["A", "B", "C"]

    assert node_a.status is NodeStatus.SUCCESS
    assert node_b.status is NodeStatus.SUCCESS
    assert node_c.status is NodeStatus.SUCCESS

    # No executable node remains.
    assert runner.run_next() is None

    # Exactly one execution per node.
    assert executed == ["A", "B", "C"]


def test_execution_runner_contract_never_executes_blocked_node():
    """
    A blocked node must never reach its callable.

    B cannot execute before A succeeds.
    C cannot execute before B succeeds.
    """
    executed: list[str] = []

    runner, graph, operations = _make_system(executed)

    ref_a = operations["a"][0]
    ref_b = operations["b"][0]
    ref_c = operations["c"][0]

    node_a = _node_by_operation_ref(graph, ref_a)
    node_b = _node_by_operation_ref(graph, ref_b)
    node_c = _node_by_operation_ref(graph, ref_c)

    # Before any execution, B/C must remain blocked.
    assert node_b.status is NodeStatus.WAITING
    assert node_c.status is NodeStatus.WAITING
    assert executed == []

    # One runner step may execute A only.
    runner.run_next()

    assert executed == ["A"]
    assert node_a.status is NodeStatus.SUCCESS
    assert node_b.status is NodeStatus.READY
    assert node_c.status is NodeStatus.WAITING

    # B is now released, C is still blocked.
    runner.run_next()

    assert executed == ["A", "B"]
    assert node_b.status is NodeStatus.SUCCESS
    assert node_c.status is NodeStatus.READY

    # Only now may C execute.
    runner.run_next()

    assert executed == ["A", "B", "C"]
    assert node_c.status is NodeStatus.SUCCESS


def test_execution_runner_contract_resolves_operation_ref_at_execution_time():
    """
    ExecutionRunner must resolve the node's OperationRef.

    It must not derive a callable from node.name or Task.description.
    """
    executed: list[str] = []

    runner, graph, operations = _make_system(executed)

    ref_a = operations["a"][0]
    node_a = _node_by_operation_ref(graph, ref_a)

    assert node_a.name == "A"
    assert node_a.operation_ref == ref_a

    result = runner.run_next()

    assert result is node_a
    assert executed == ["A"]

def test_execution_runner_contract_failed_node_does_not_release_successor():
    """
    If A fails:

        A FAILED
        B remains WAITING
        B must never execute.
    """
    executed: list[str] = []

    def failing_a():
        executed.append("A")
        raise RuntimeError("A failed")

    def operation_b():
        executed.append("B")
        return "result-B"

    def operation_c():
        executed.append("C")
        return "result-C"

    ref_a = OperationRef("failure.a", "1.0")
    ref_b = OperationRef("failure.b", "1.0")
    ref_c = OperationRef("failure.c", "1.0")

    registry = OperationRegistry()
    registry.register(ref_a, failing_a)
    registry.register(ref_b, operation_b)
    registry.register(ref_c, operation_c)

    resolver = OperationResolver(registry)

    class Binder:
        def bind(self, task: Task) -> OperationRef:
            return {
                "a": ref_a,
                "b": ref_b,
                "c": ref_c,
            }[task.id]

    graph = PlanCompiler(
        operation_binder=Binder()
    ).compile(_make_plan())

    scheduler = Scheduler(graph)
    runner = ExecutionRunner(
        scheduler=scheduler,
        resolver=resolver,
        executor=Executor(),
    )

    node_a = _node_by_operation_ref(graph, ref_a)
    node_b = _node_by_operation_ref(graph, ref_b)
    node_c = _node_by_operation_ref(graph, ref_c)

    assert node_a.status is NodeStatus.READY
    assert node_b.status is NodeStatus.WAITING
    assert node_c.status is NodeStatus.WAITING

    result = runner.run_next()

    assert result is node_a
    assert executed == ["A"]

    assert node_a.status is NodeStatus.FAILED
    assert node_b.status is NodeStatus.WAITING
    assert node_c.status is NodeStatus.WAITING

    # A failure must not release B.
    assert runner.run_next() is None
    assert executed == ["A"]


def test_execution_runner_contract_failed_middle_node_does_not_release_successor():
    """
    If A succeeds but B fails:

        A SUCCESS
        B FAILED
        C remains WAITING
        C must never execute.
    """
    executed: list[str] = []

    def operation_a():
        executed.append("A")
        return "result-A"

    def failing_b():
        executed.append("B")
        raise RuntimeError("B failed")

    def operation_c():
        executed.append("C")
        return "result-C"

    ref_a = OperationRef("failure-chain.a", "1.0")
    ref_b = OperationRef("failure-chain.b", "1.0")
    ref_c = OperationRef("failure-chain.c", "1.0")

    registry = OperationRegistry()
    registry.register(ref_a, operation_a)
    registry.register(ref_b, failing_b)
    registry.register(ref_c, operation_c)

    resolver = OperationResolver(registry)

    class Binder:
        def bind(self, task: Task) -> OperationRef:
            return {
                "a": ref_a,
                "b": ref_b,
                "c": ref_c,
            }[task.id]

    graph = PlanCompiler(
        operation_binder=Binder()
    ).compile(_make_plan())

    scheduler = Scheduler(graph)
    runner = ExecutionRunner(
        scheduler=scheduler,
        resolver=resolver,
        executor=Executor(),
    )

    node_a = _node_by_operation_ref(graph, ref_a)
    node_b = _node_by_operation_ref(graph, ref_b)
    node_c = _node_by_operation_ref(graph, ref_c)

    # A succeeds and releases B.
    assert runner.run_next() is node_a

    assert executed == ["A"]
    assert node_a.status is NodeStatus.SUCCESS
    assert node_b.status is NodeStatus.READY
    assert node_c.status is NodeStatus.WAITING

    # B executes and fails.
    assert runner.run_next() is node_b

    assert executed == ["A", "B"]
    assert node_b.status is NodeStatus.FAILED

    # B failure must not release C.
    assert node_c.status is NodeStatus.WAITING
    assert runner.run_next() is None
    assert executed == ["A", "B"]


def test_execution_runner_contract_failed_leaf_has_no_successor():
    """
    A failed leaf becomes FAILED and the graph has no successor to release.
    """
    executed: list[str] = []

    def operation_a():
        executed.append("A")
        return "result-A"

    def operation_b():
        executed.append("B")
        return "result-B"

    def failing_c():
        executed.append("C")
        raise RuntimeError("C failed")

    ref_a = OperationRef("failure-leaf.a", "1.0")
    ref_b = OperationRef("failure-leaf.b", "1.0")
    ref_c = OperationRef("failure-leaf.c", "1.0")

    registry = OperationRegistry()
    registry.register(ref_a, operation_a)
    registry.register(ref_b, operation_b)
    registry.register(ref_c, failing_c)

    resolver = OperationResolver(registry)

    class Binder:
        def bind(self, task: Task) -> OperationRef:
            return {
                "a": ref_a,
                "b": ref_b,
                "c": ref_c,
            }[task.id]

    graph = PlanCompiler(
        operation_binder=Binder()
    ).compile(_make_plan())

    scheduler = Scheduler(graph)
    runner = ExecutionRunner(
        scheduler=scheduler,
        resolver=resolver,
        executor=Executor(),
    )

    node_a = _node_by_operation_ref(graph, ref_a)
    node_b = _node_by_operation_ref(graph, ref_b)
    node_c = _node_by_operation_ref(graph, ref_c)

    assert runner.run_next() is node_a
    assert runner.run_next() is node_b

    assert executed == ["A", "B"]
    assert node_c.status is NodeStatus.READY

    assert runner.run_next() is node_c

    assert executed == ["A", "B", "C"]
    assert node_c.status is NodeStatus.FAILED

    assert runner.run_next() is None
