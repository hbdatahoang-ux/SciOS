from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any
from uuid import UUID, uuid4

from scios.execution.node.node import ExecutionNode
from scios.execution.scheduler.executor.worker import Worker
from scios.execution.scheduler.executor.pool import WorkerPool


@dataclass
class Executor:
    """
    Executor = Coordinates workers to execute nodes.
    """

    executor_id: UUID = field(default_factory=uuid4)
    pool: WorkerPool = field(default_factory=WorkerPool)
    completed: List[ExecutionNode] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def run_task(self, node: ExecutionNode) -> Any:
        """
        Execute a single node using available worker.
        """
        worker = self.pool.acquire_worker()
        result = worker.execute(node)
        self.completed.append(node)
        self.pool.release_worker(worker)
        return result

    def run_all(self, nodes: List[ExecutionNode]) -> List[Any]:
        """
        Execute all nodes sequentially.
        """
        results = []
        for node in nodes:
            results.append(self.run_task(node))
        return results

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Reset executor state.
        """
        self.completed.clear()
        self.pool.reset()
