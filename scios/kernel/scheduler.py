"""
SciOS Kernel Scheduler
======================

Task scheduler for the Scientific Cognitive
Operating System (SciOS).

Responsibilities
----------------
- Queue task execution
- Support multiple scheduling policies
- Dispatch tasks to the Runtime
- Track scheduler statistics
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


__all__ = [
    "SchedulePolicy",
    "Task",
    "Scheduler",
]


# ==========================================================
# Scheduling Policy
# ==========================================================

class SchedulePolicy(str, Enum):
    """
    Supported scheduling policies.
    """

    FIFO = "fifo"

    LIFO = "lifo"


# ==========================================================
# Task
# ==========================================================

@dataclass(slots=True)
class Task:
    """
    Scheduled task.
    """

    id: int

    payload: Any

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ==========================================================
# Scheduler
# ==========================================================

class Scheduler:
    """
    Kernel task scheduler.

    The scheduler stores tasks and dispatches them
    to the Runtime in the selected scheduling order.
    """

    def __init__(
        self,
        policy: SchedulePolicy = SchedulePolicy.FIFO,
    ) -> None:

        self._policy = policy

        self._queue: deque[Task] = deque()

        self._counter = 0

        self._executed = 0

    # ======================================================
    # Task Management
    # ======================================================

    def submit(
        self,
        payload: Any,
    ) -> Task:
        """
        Submit a task.
        """

        self._counter += 1

        task = Task(
            id=self._counter,
            payload=payload,
        )

        self._queue.append(task)

        return task

    # ======================================================
    # Dispatch
    # ======================================================

    def next(self) -> Task | None:
        """
        Return the next task.
        """

        if not self._queue:
            return None

        if self._policy == SchedulePolicy.FIFO:
            task = self._queue.popleft()
        else:
            task = self._queue.pop()

        self._executed += 1

        return task

    # ======================================================
    # Queue Operations
    # ======================================================

    def clear(self) -> None:

        self._queue.clear()

    def empty(self) -> bool:

        return len(self._queue) == 0

    def pending(self) -> int:

        return len(self._queue)

    # ======================================================
    # Policy
    # ======================================================

    @property
    def policy(self) -> SchedulePolicy:

        return self._policy

    def set_policy(
        self,
        policy: SchedulePolicy,
    ) -> None:

        self._policy = policy

    # ======================================================
    # Statistics
    # ======================================================

    def status(self) -> dict[str, Any]:

        return {

            "policy": self._policy.value,

            "pending": self.pending(),

            "submitted": self._counter,

            "executed": self._executed,
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:

        return self.pending()

    def __bool__(self) -> bool:

        return not self.empty()

    def __repr__(self) -> str:

        return (
            "Scheduler("
            f"policy={self._policy.value}, "
            f"pending={self.pending()})"
        )