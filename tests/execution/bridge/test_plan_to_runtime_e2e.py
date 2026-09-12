from scios.cognitive_core.planner import Goal, Plan, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.bridge import OperationExecutionAdapter
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime import ExecutionContext
from scios.runtime.executor import Executor


class _TestOperationBinder:
    def __init__(self, ref):
        self.ref = ref

    def bind(self, task):
        return self.ref


def test_plan_to_runtime_execution_end_to_end():
    calls = []

    def analyze():
        calls.append("executed")
        return "analysis-ok"

    ref = OperationRef("data.analyze", "1.0")

    registry = OperationRegistry()
    registry.register(ref, analyze)

    binder = _TestOperationBinder(ref)
    compiler = PlanCompiler(operation_binder=binder)

    plan = Plan(
        goal=Goal("Analyze data"),
        tasks=[
            Task("Analyze data", task_id="analyze"),
        ],
    )

    graph = compiler.compile(plan)

    assert len(graph.nodes) == 1

    node = next(iter(graph.nodes.values()))

    assert node.operation_ref == ref

    adapter = OperationExecutionAdapter(
        OperationResolver(registry)
    )

    operation = adapter.resolve(node)

    assert operation is analyze
    assert calls == []

    context = ExecutionContext(task=operation)
    result = Executor().execute(context)

    assert result.value == "analysis-ok"
    assert context.result.value == "analysis-ok"
    assert calls == ["executed"]

