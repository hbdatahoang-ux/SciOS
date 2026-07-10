"""
SciOS Runtime Loop
==================

Main runtime execution loop.

Responsibilities
----------------
- Drive Worker execution.
- Pull tasks from Scheduler.
- Execute one runtime cycle at a time.
- Remain deterministic and testable.
- Maintain runtime loop statistics.

The RuntimeLoop intentionally does NOT:
- own a Kernel
- execute cognitive logic
- manage threads
"""

from __future__ import annotations
from typing import Any

from ..scheduler import Scheduler
from .worker import Worker

__all__ = ["RuntimeLoop"]


class RuntimeLoop:
    """
    Runtime execution loop.

        Runtime
            ↓
        RuntimeLoop
            ↓
          Worker
            ↓
      RuntimeExecutor
    """

    def __init__(self, scheduler: Scheduler, worker: Worker) -> None:
        self._scheduler = scheduler
        self._worker = worker
        self._ticks = 0
        self._executed = 0

    # ==========================================================
    # Loop
    # ==========================================================

    def tick(self) -> Any:
        """
        Execute exactly one runtime iteration.

        Returns
        -------
        Any | None
            Result returned by the Worker.
        """
        self._ticks += 1

        task = self._scheduler.next_task()
        if task is None:
            return None

        result = self._worker.execute(task)
        if result is not None:
            self._executed += 1

        return result

    def run(self, cycles: int = 1) -> list[Any]:
        """
        Execute multiple runtime iterations.

        Parameters
        ----------
        cycles:
            Number of loop iterations.

        Returns
        -------
        list[Any]
            Results produced during execution.
        """
        if cycles < 1:
            return []

        results: list[Any] = []
        for _ in range(cycles):
            results.append(self.tick())
        return results

    # ==========================================================
    # Utilities
    # ==========================================================

    def reset(self) -> None:
        """Reset runtime loop statistics."""
        self._ticks = 0
        self._executed = 0

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def worker(self) -> Worker:
        return self._worker

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def executed(self) -> int:
        return self._executed

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """Runtime loop status."""
        return {
            "ticks": self._ticks,
            "executed": self._executed,
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __repr__(self) -> str:
        return f"RuntimeLoop(ticks={self._ticks}, executed={self._executed})"
