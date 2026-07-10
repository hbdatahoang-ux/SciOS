"""
SciOS Runtime Executor
======================

Runtime task execution engine.

Responsibilities
----------------
- Receive tasks from the Runtime.
- Submit tasks to the Scheduler.
- Execute scheduled tasks via ExecutionEngine.
- Maintain execution statistics.

The RuntimeExecutor intentionally does NOT:
- manage worker threads
- know about the Kernel
- know about the Cognitive Pipeline
"""

from __future__ import annotations

from typing import Any

from scios.kernel.execution import ExecutionEngine
from scios.kernel.scheduler import Scheduler, Task

__all__ = [
    "RuntimeExecutor",
]


class RuntimeExecutor:
    """
    Runtime execution engine.

    Coordinates:

        Scheduler
            ↓
        ExecutionEngine
    """

    def __init__(
        self,
        scheduler: Scheduler,
        execution_engine: ExecutionEngine,
    ) -> None:

        self._scheduler = scheduler
        self._engine = execution_engine

        self._executed = 0

    # ==========================================================
    # Task Management
    # ==========================================================

    def submit(self, task: Task):
        """
        Submit a task to the scheduler.
        """

        return self._scheduler.submit(task)

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(self) -> Any:
        """
        Execute the next scheduled task.

        Returns
        -------
        Any | None
            Result produced by the ExecutionEngine.
        """

        task = self._scheduler.next()

        if task is None:
            return None

        result = self._engine.execute(task)

        self._executed += 1

        return result

    def run(self, task: Task) -> Any:
        """
        Submit and execute immediately.
        """

        self.submit(task)

        return self.execute()

    # ==========================================================
    # Utilities
    # ==========================================================

    def clear(self) -> None:
        """
        Remove all pending tasks.
        """

        self._scheduler.clear()

    def reset(self) -> None:
        """
        Reset runtime statistics.
        """

        self.clear()

        self._executed = 0

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def execution_engine(self) -> ExecutionEngine:
        return self._engine

    @property
    def executed(self) -> int:
        """
        Number of successfully executed tasks.
        """

        return self._executed

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        RuntimeExecutor status.
        """

        return {
            "executed": self._executed,
            "pending_tasks": len(self._scheduler),
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._scheduler)

    def __repr__(self) -> str:

        return (
            "RuntimeExecutor("
            f"executed={self._executed}, "
            f"pending={len(self._scheduler)})"
        )