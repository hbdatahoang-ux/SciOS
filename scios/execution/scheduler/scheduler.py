from __future__ import annotations

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus
from scios.execution.scheduler.policy import SchedulingPolicy
from scios.execution.scheduler.queue import TaskQueue


class Scheduler:
    """
    Dependency-aware scheduler for ExecutionGraph.

    Scheduler selects READY nodes only. It never executes nodes.
    """

    def __init__(
        self,
        graph: ExecutionGraph,
        policy: SchedulingPolicy | None = None,
    ) -> None:
        if not isinstance(graph, ExecutionGraph):
            raise TypeError("graph must be an ExecutionGraph")

        self.graph = graph
        self.policy = policy if policy is not None else SchedulingPolicy()
        self.queue = TaskQueue()
        self._scheduled: set = set()

        self._initialize_readiness()

    def _initialize_readiness(self) -> None:
        self.queue.reset()
        self._scheduled.clear()

        for node in self.graph.nodes.values():
            predecessors = self.graph.predecessors(node.node_id)

            if not predecessors:
                node.status = NodeStatus.READY
            else:
                node.status = NodeStatus.WAITING

        for node in self.graph.nodes.values():
            if node.status is NodeStatus.READY:
                self.queue.enqueue(node)

    def next(self) -> ExecutionNode | None:
        candidates = []

        while self.queue.has_tasks():
            node = self.queue.dequeue()

            if node is None:
                continue

            if node.node_id in self._scheduled:
                continue

            if node.status is not NodeStatus.READY:
                continue

            candidates.append(node)

        if not candidates:
            return None

        selected = self.policy.select(candidates)

        for node in candidates:
            if node is not selected:
                self.queue.enqueue(node)

        self._scheduled.add(selected.node_id)

        return selected

    def notify_completed(self, node: ExecutionNode) -> None:
        if not isinstance(node, ExecutionNode):
            raise TypeError("node must be an ExecutionNode")

        if node.node_id not in self.graph.nodes:
            raise ValueError("node does not belong to the graph")

        if not node.is_terminal():
            raise ValueError("completed node must have a terminal status")

        for successor in self.graph.successors(node.node_id):
            if successor.status is not NodeStatus.WAITING:
                continue

            predecessors = self.graph.predecessors(successor.node_id)

            if all(
                predecessor.status is NodeStatus.SUCCESS
                for predecessor in predecessors
            ):
                successor.status = NodeStatus.READY
                self.queue.enqueue(successor)

    def reset(self) -> None:
        self._initialize_readiness()
