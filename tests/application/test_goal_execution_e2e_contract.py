from __future__ import annotations

from scios.application.goal_execution import GoalExecutionService
from scios.cognitive_core.planner import Goal, Planner, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor


class _TestOperationBinder:
    def __init__(self, refs: dict[str, OperationRef]) -> None:
        self.refs = refs

    def bind(self, task: Task) -> OperationRef:
        return self.refs[task.id]


def test_goal_execution_freezes_full_plan_to_runtime_lifecycle():
    calls: list[str] = []
    results: dict[str, str] = {}

    def operation_a() -> str:
        calls.append("A")
        results["A"] = "result-A"
        return "result-A"

    def operation_b() -> str:
        calls.append("B")
        results["B"] = "result-B"
        return "result-B"

    def operation_c() -> str:
        calls.append("C")
        results["C"] = "result-C"
        return "result-C"

    ref_a = OperationRef("A")
    ref_b = OperationRef("B")
    ref_c = OperationRef("C")

    registry = OperationRegistry()
    registry.register(ref_a, operation_a)
    registry.register(ref_b, operation_b)
    registry.register(ref_c, operation_c)

    refs = {
        "A": ref_a,
        "B": ref_b,
        "C": ref_c,
    }

    binder = _TestOperationBinder(refs)

    service = GoalExecutionService(
        planner=Planner(),
        compiler=PlanCompiler(operation_binder=binder),
        resolver=OperationResolver(registry),
        executor=Executor(),
    )

    goal = Goal("Execute dependent operations")

    tasks = [
        Task("A", task_id="A"),
        Task("B", task_id="B", dependencies=["A"]),
        Task("C", task_id="C", dependencies=["B"]),
    ]

    execution = service.execute(goal, tasks=tasks)

    assert execution.goal is goal
    assert execution.plan is not None
    assert execution.graph is not None

    assert calls == ["A", "B", "C"]

    assert results == {
        "A": "result-A",
        "B": "result-B",
        "C": "result-C",
    }


def test_goal_execution_preserves_dependency_order_with_independent_nodes():
    calls: list[str] = []

    def operation_a() -> str:
        calls.append("A")
        return "A-result"

    def operation_b() -> str:
        calls.append("B")
        return "B-result"

    def operation_c() -> str:
        calls.append("C")
        return "C-result"

    ref_a = OperationRef("A")
    ref_b = OperationRef("B")
    ref_c = OperationRef("C")

    registry = OperationRegistry()
    registry.register(ref_a, operation_a)
    registry.register(ref_b, operation_b)
    registry.register(ref_c, operation_c)

    refs = {
        "A": ref_a,
        "B": ref_b,
        "C": ref_c,
    }

    binder = _TestOperationBinder(refs)

    service = GoalExecutionService(
        planner=Planner(),
        compiler=PlanCompiler(operation_binder=binder),
        resolver=OperationResolver(registry),
        executor=Executor(),
    )

    goal = Goal("Execute dependency graph")

    tasks = [
        Task("A", task_id="A"),
        Task("B", task_id="B"),
        Task("C", task_id="C", dependencies=["A", "B"]),
    ]

    service.execute(goal, tasks=tasks)

    assert set(calls[:2]) == {"A", "B"}
    assert calls[-1] == "C"

    assert calls.index("A") < calls.index("C")
    assert calls.index("B") < calls.index("C")

