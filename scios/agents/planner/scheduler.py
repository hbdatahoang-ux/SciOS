"""
SciOS Planner Scheduler
=======================

Task scheduler for the SciOS Planning subsystem.

Responsibilities
----------------
- Queue executable tasks
- Dispatch tasks in execution order
- Support future scheduling strategies
"""

from __future__ import annotations

from collections import deque
from typing import Any

__all__ = [
    "Scheduler",
]


class Scheduler:
    """
    Planner task scheduler.

    The Scheduler manages execution order of planning tasks.
    Future versions may support priority scheduling,
    dependency-aware scheduling, and distributed execution.
    """

    def __init__(self) -> None:

        self._queue: deque[dict[str, Any]] = deque()

        self._completed = 0

    # =====================================================
    # Queue Management
    # =====================================================

    def submit(
        self,
        task: dict[str, Any],
    ) -> None:
        """
        Submit a task to the scheduler.
        """

        self._queue.append(task)

    def dispatch(
        self,
    ) -> dict[str, Any] | None:
        """
        Dispatch the next task.
        """

        if not self._queue:
            return None

        task = self._queue.popleft()

        self._completed += 1

        return task

    def peek(
        self,
    ) -> dict[str, Any] | None:
        """
        Peek at the next task.
        """

        if not self._queue:
            return None

        return self._queue[0]

    # =====================================================
    # Queue Control
    # =====================================================

    def clear(self) -> None:
        """
        Remove all pending tasks.
        """

        self._queue.clear()

    @property
    def empty(self) -> bool:
        """
        Whether the scheduler queue is empty.
        """

        return len(self._queue) == 0

    # =====================================================
    # Status
    # =====================================================

    def status(self) -> dict[str, Any]:

        return {

            "strategy": "FIFO",

            "queued": len(self._queue),

            "completed": self._completed,
        }

    # =====================================================
    # Python Protocols
    # =====================================================

    def __len__(self) -> int:

        return len(self._queue)

    def __bool__(self) -> bool:

        return not self.empty

    def __repr__(self) -> str:

        return (
            "Scheduler("
            f"queued={len(self)}, "
            f"completed={self._completed})"
        )