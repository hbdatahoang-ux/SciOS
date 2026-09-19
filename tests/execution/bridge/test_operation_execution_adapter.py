import pytest

from scios.execution.node.node import ExecutionNode
from scios.execution.operation.ref import OperationRef


def test_execution_node_operation_ref_resolves_to_callable():
    from scios.execution.bridge import OperationExecutionAdapter
    from scios.execution.operation.registry import OperationRegistry
    from scios.execution.operation.resolver import OperationResolver

    registry = OperationRegistry()

    def analyze():
        return "ok"

    ref = OperationRef("data.analyze", "1.0")
    registry.register(ref, analyze)

    resolver = OperationResolver(registry)
    adapter = OperationExecutionAdapter(resolver)

    node = ExecutionNode(
        name="Analyze data",
        operation_ref=ref,
    )

    resolved = adapter.resolve(node)

    assert resolved is analyze


def test_execution_node_resolution_does_not_execute_callable():
    from scios.execution.bridge import OperationExecutionAdapter
    from scios.execution.operation.registry import OperationRegistry
    from scios.execution.operation.resolver import OperationResolver

    registry = OperationRegistry()
    calls = []

    def analyze():
        calls.append("executed")
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

    resolved = adapter.resolve(node)

    assert resolved is analyze
    assert calls == []


def test_execution_node_without_operation_ref_is_rejected():
    from scios.execution.bridge import OperationExecutionAdapter
    from scios.execution.operation.registry import OperationRegistry
    from scios.execution.operation.resolver import OperationResolver

    adapter = OperationExecutionAdapter(
        OperationResolver(OperationRegistry())
    )

    node = ExecutionNode(name="Unbound task")

    with pytest.raises(ValueError, match="operation_ref"):
        adapter.resolve(node)
