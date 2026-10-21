from __future__ import annotations

from collections.abc import Sequence

from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus


class SchedulingPolicy:
    """
    Selects one node from the currently ready nodes.

    SchedulingPolicy does not know about ExecutionGraph or dependencies.
    """

    def select(
        self,
        ready_nodes: Sequence[ExecutionNode],
    ) -> ExecutionNode:
        if not ready_nodes:
            raise ValueError("ready_nodes must not be empty")

        for node in ready_nodes:
            if not isinstance(node, ExecutionNode):
                raise TypeError("ready_nodes must contain ExecutionNode")

            if node.status is not NodeStatus.READY:
                raise ValueError("ready_nodes must contain only READY nodes")

        return ready_nodes[0]
