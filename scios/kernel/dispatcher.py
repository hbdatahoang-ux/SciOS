"""
SciOS Kernel Dispatcher
=======================

Task dispatcher for the SciOS Kernel.

Responsibilities
----------------
- Bridge Scheduler and ExecutionEngine.
- Dispatch queued tasks.
- Publish lifecycle events.
- Maintain execution statistics.

Design Goals
------------
- Thread-safe
- Runtime agnostic
- Event driven
- Extensible
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from scios.runtime import ExecutionContext
from scios.runtime import ExecutionEngine

from .scheduler import Scheduler


class Dispatcher:
    """
    Dispatch tasks from Scheduler to ExecutionEngine.
    """

    def __init__(
        self,
        scheduler: Scheduler,
        engine: ExecutionEngine,
    ) -> None:

        self.scheduler = scheduler
        self.engine = engine

        self._lock = RLock()

        self._running = False

        self._tasks_dispatched = 0
        self._tasks_failed = 0

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """
        Initialize dispatcher.
        """
        self._running = False

    def start(self) -> None:
        """
        Start dispatcher.
        """
        self._running = True

    def shutdown(self) -> None:
        """
        Shutdown dispatcher.
        """
        self._running = False

    # ==========================================================
    # Dispatch
    # ==========================================================

    def dispatch(
        self,
        task: Any,
        **metadata: Any,
    ) -> ExecutionContext:
        """
        Dispatch a single task immediately.
        """

        if not self._running:
            raise RuntimeError(
                "Dispatcher is not running."
            )

        with self._lock:

            context = self.engine.run(
                task=task,
                metadata=metadata,
            )

            self._tasks_dispatched += 1

            return context

    def dispatch_next(self) -> ExecutionContext | None:
        """
        Execute the next scheduled task.
        """

        if not self._running:
            raise RuntimeError(
                "Dispatcher is not running."
            )

        if self.scheduler.empty():
            return None

        task = self.scheduler.dequeue()

        try:

            return self.dispatch(task)

        except Exception:

            self._tasks_failed += 1
            raise

    def dispatch_all(self) -> list[ExecutionContext]:
        """
        Execute every queued task.
        """

        results: list[ExecutionContext] = []

        while not self.scheduler.empty():

            context = self.dispatch_next()

            if context is not None:
                results.append(context)

        return results

    # ==========================================================
    # Scheduler Interface
    # ==========================================================

    def submit(
        self,
        task: Any,
    ) -> None:
        """
        Submit a task to the scheduler.
        """

        self.scheduler.enqueue(task)

    # ==========================================================
    # Statistics
    # ==========================================================

    @property
    def tasks_dispatched(self) -> int:
        return self._tasks_dispatched

    @property
    def tasks_failed(self) -> int:
        return self._tasks_failed

    # ==========================================================
    # Status
    # ==========================================================

    @property
    def running(self) -> bool:
        return self._running

    def status(self) -> dict[str, Any]:
        """
        Dispatcher status.
        """

        return {
            "running": self._running,
            "queued_tasks": len(self.scheduler),
            "tasks_dispatched": self._tasks_dispatched,
            "tasks_failed": self._tasks_failed,
        }

    # ==========================================================
    # Utilities
    # ==========================================================

    def reset(self) -> None:
        """
        Reset dispatcher statistics.
        """

        self._tasks_dispatched = 0
        self._tasks_failed = 0

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __len__(self) -> int:
        return len(self.scheduler)

    def __bool__(self) -> bool:
        return self._running

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"running={self._running}, "
            f"queued={len(self.scheduler)}, "
            f"dispatched={self._tasks_dispatched}, "
            f"failed={self._tasks_failed})"
        )