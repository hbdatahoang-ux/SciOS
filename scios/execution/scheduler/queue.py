from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4

from scios.execution.node.node import ExecutionNode


@dataclass
class TaskQueue:
    """
    TaskQueue = Manages execution-ready nodes.
    """

    queue_id: UUID = field(default_factory=uuid4)
    tasks: List[ExecutionNode] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def enqueue(self, node: ExecutionNode) -> None:
        """
        Add node to queue.
        """
        self.tasks.append(node)

    def dequeue(self) -> ExecutionNode | None:
        """
        Remove and return next node from queue.
        """
        if not self.tasks:
            return None
        return self.tasks.pop(0)

    def peek(self) -> ExecutionNode | None:
        """
        Peek at next node without removing.
        """
        return self.tasks[0] if self.tasks else None

    def has_tasks(self) -> bool:
        """
        Check if queue has tasks.
        """
        return len(self.tasks) > 0

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Clear queue.
        """
        self.tasks.clear()

    def size(self) -> int:
        """
        Return number of tasks in queue.
        """
        return len(self.tasks)
