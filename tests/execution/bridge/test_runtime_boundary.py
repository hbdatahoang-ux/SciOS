from scios.execution.bridge import OperationExecutionAdapter
from scios.execution.node.node import ExecutionNode
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime import ExecutionContext
from scios.runtime.executor import Executor


def test_resolved_operation_can_be_passed_to_runtime_executor():
    registry = OperationRegistry()

    def analyze():
        return "ok"

    ref = OperationRef("data.analyze", "1.0")
    registry.register(ref, analyze)

    adapter = OperationExecutionAdapter(
        OperationResolver(registry)
    )

    node = ExecutionNode(
        name="Analyze data",
        operation_ref=ref,
    )

    operation = adapter.resolve(node)

    context = ExecutionContext(task=operation)
    result = Executor().execute(context)

    assert result.value == "ok"
    assert context.result.value == "ok"

