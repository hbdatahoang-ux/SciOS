"""
SciOS Runtime Scheduler
=======================

Task scheduler for the SciOS Runtime.

Responsibilities
----------------
- Maintain the runtime task queue.
- Submit and dequeue execution contexts.
- Provide FIFO scheduling by default.
- Track scheduling statistics.
- Expose queue inspection APIs.

Design Goals
------------
- Python 3.11+
- Thread-safe ready
- Lightweight
- Deterministic
- Zero external dependencies
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from threading import Lock
from typing import Any

from .context import ExecutionContext
from .exceptions import QueueEmptyError

__all__ = [
    "Scheduler",
]


class Scheduler:
    """
    Runtime FIFO Scheduler.

    This scheduler is intentionally simple.

    Higher-level schedulers (priority, deadline,
    distributed, GPU-aware, etc.) may subclass this
    implementation.
    """

    def __init__(self) -> None:

        self._queue: deque[ExecutionContext] = deque()

        self._lock = Lock()

        self._submitted = 0

        self._completed = 0

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """
        Initialize scheduler.
        """

        self.clear()

    def shutdown(self) -> None:
        """
        Shutdown scheduler.
        """

        self.clear()

    # ==========================================================
    # Queue Operations
    # ==========================================================

    def submit(
        self,
        context: ExecutionContext,
    ) -> None:
        """
        Submit a new execution context.
        """

        with self._lock:

            self._queue.append(context)

            self._submitted += 1

    def next(self) -> ExecutionContext:
        """
        Retrieve the next scheduled context.
        """

        with self._lock:

            if not self._queue:
                raise QueueEmptyError(
                    "Scheduler queue is empty."
                )

            return self._queue.popleft()

    def complete(
        self,
        context: ExecutionContext,
    ) -> None:
        """
        Mark one execution as completed.
        """

        self._completed += 1

    def peek(self) -> ExecutionContext | None:
        """
        Return the next task without removing it.
        """

        with self._lock:

            if not self._queue:
                return None

            return self._queue[0]

    def clear(self) -> None:
        """
        Remove all queued contexts.
        """

        with self._lock:

            self._queue.clear()

    # ==========================================================
    # Query
    # ==========================================================

    def empty(self) -> bool:
        """
        Whether the queue is empty.
        """

        return len(self) == 0

    def size(self) -> int:
        """
        Queue size.
        """

        return len(self)

    @property
    def submitted(self) -> int:
        """
        Total submitted contexts.
        """

        return self._submitted

    @property
    def completed(self) -> int:
        """
        Total completed contexts.
        """

        return self._completed

    @property
    def pending(self) -> int:
        """
        Number of pending contexts.
        """

        return len(self)

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Scheduler status.
        """

        return {
            "submitted": self._submitted,
            "completed": self._completed,
            "pending": self.pending,
            "queue_size": len(self),
        }

    # ==========================================================
    # Iteration
    # ==========================================================

    def __iter__(self) -> Iterator[ExecutionContext]:

        with self._lock:

            yield from tuple(self._queue)

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __len__(self) -> int:

        return len(self._queue)

    def __bool__(self) -> bool:

        return not self.empty()

    def __contains__(
        self,
        context: ExecutionContext,
    ) -> bool:

        return context in self._queue

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"pending={self.pending}, "
            f"submitted={self.submitted}, "
            f"completed={self.completed})"
        )