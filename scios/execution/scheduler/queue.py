from __future__ import annotations

from collections import deque

from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus


class TaskQueue:
    """
    Queue of execution-ready nodes.

    TaskQueue owns queue mechanics only. It does not know about
    ExecutionGraph or dependency resolution.
    """

    def __init__(self) -> None:
        self._queue: deque[ExecutionNode] = deque()

    def enqueue(self, node: ExecutionNode) -> None:
        if not isinstance(node, ExecutionNode):
            raise TypeError("node must be an ExecutionNode")

        if node.status is not NodeStatus.READY:
            raise ValueError("only READY nodes can be enqueued")

        self._queue.append(node)

    def dequeue(self) -> ExecutionNode | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def peek(self) -> ExecutionNode | None:
        if not self._queue:
            return None
        return self._queue[0]

    def has_tasks(self) -> bool:
        return bool(self._queue)

    def size(self) -> int:
        return len(self._queue)

    def reset(self) -> None:
        self._queue.clear()
