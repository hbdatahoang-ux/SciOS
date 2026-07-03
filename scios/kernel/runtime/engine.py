"""
SciOS Runtime Engine
====================

Kernel runtime execution engine.

Responsibilities
----------------
- Receive tasks
- Schedule execution
- Dispatch tasks to AgentExecutor
- Maintain runtime statistics
"""

from __future__ import annotations

from typing import Any

from scios.agents.executor import AgentExecutor
from scios.kernel.scheduler import Scheduler

__all__ = [
    "Runtime",
]


class Runtime:
    """
    SciOS runtime engine.

    The Runtime coordinates execution between the
    Scheduler and the cognitive AgentExecutor.
    """

    def __init__(
        self,
        scheduler: Scheduler | None = None,
        executor: AgentExecutor | None = None,
    ) -> None:

        self.scheduler = scheduler or Scheduler()

        self.executor = executor or AgentExecutor()

        self._running = False

        self._executed = 0

    # ======================================================
    # Lifecycle
    # ======================================================

    def boot(self) -> None:
        """
        Start the runtime.
        """

        self._running = True

    def shutdown(self) -> None:
        """
        Stop the runtime.
        """

        self._running = False

        self.scheduler.clear()

    # ======================================================
    # Execution
    # ======================================================

    def submit(
        self,
        task: Any,
    ):
        """
        Submit a task.
        """

        return self.scheduler.submit(task)

    def execute(self):
        """
        Execute the next scheduled task.
        """

        if not self._running:
            raise RuntimeError(
                "Runtime is not running."
            )

        task = self.scheduler.next()

        if task is None:
            return None

        result = self.executor.execute(
            task.payload
        )

        self._executed += 1

        return result

    def run(
        self,
        task: Any,
    ):
        """
        Submit and execute immediately.
        """

        self.submit(task)

        return self.execute()

    # ======================================================
    # Status
    # ======================================================

    @property
    def running(self) -> bool:
        return self._running

    def status(self) -> dict[str, Any]:
        """
        Runtime status.
        """

        return {
            "running": self._running,
            "executed": self._executed,
            "scheduler": self.scheduler.status(),
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __repr__(self) -> str:

        return (
            "Runtime("
            f"running={self._running}, "
            f"executed={self._executed})"
        )
    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def infer(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Backward-compatible alias for reason().
        """

        return self.reason(
            query=query,
            context=context,
        )        