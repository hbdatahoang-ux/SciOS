from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.scheduler.policy import SchedulingPolicy


@dataclass
class Scheduler:
    """
    Scheduler = Orchestrates execution order of nodes in ExecutionGraph.
    """

    scheduler_id: UUID = field(default_factory=uuid4)
    policy: SchedulingPolicy = field(default_factory=SchedulingPolicy)
    queue: List[ExecutionNode] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def build_queue(self, graph: ExecutionGraph) -> None:
        """
        Build execution queue based on scheduling policy.
        """
        self.queue = self.policy.apply(graph)

    def next_task(self) -> ExecutionNode | None:
        """
        Get next node to execute.
        """
        if not self.queue:
            return None
        return self.queue.pop(0)

    def has_tasks(self) -> bool:
        """
        Check if there are tasks left in queue.
        """
        return len(self.queue) > 0

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Clear queue and reset scheduler.
        """
        self.queue.clear()
