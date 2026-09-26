from collections.abc import Callable
from typing import Any

from scios.execution.node.node import ExecutionNode
from scios.execution.operation.resolver import OperationResolver


class OperationExecutionAdapter:
    """Resolve an ExecutionNode operation reference to a callable."""

    def __init__(self, resolver: OperationResolver) -> None:
        self._resolver = resolver

    def resolve(self, node: ExecutionNode) -> Callable[..., Any]:
        if not isinstance(node, ExecutionNode):
            raise TypeError("node must be an ExecutionNode")

        if node.operation_ref is None:
            raise ValueError(
                "ExecutionNode has no operation_ref"
            )

        return self._resolver.resolve(node.operation_ref)
