"""
SciOS Kernel Scheduler
======================

Task scheduler for the SciOS Kernel.

Responsibilities
----------------
- Maintain a thread-safe task queue.
- Provide FIFO scheduling.
- Support enqueue/dequeue operations.
- Maintain scheduling statistics.

Design Goals
------------
- Thread-safe
- Lightweight
- Deterministic FIFO
- Runtime independent
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from threading import RLock
from typing import Any


class Scheduler:
    """
    FIFO task scheduler.
    """

    def __init__(self) -> None:
        self._queue: deque[Any] = deque()
        self._lock = RLock()

        self._running = False

        self._tasks_enqueued = 0
        self._tasks_dequeued = 0

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """Initialize scheduler."""
        self._running = False

    def start(self) -> None:
        """Start scheduler."""
        self._running = True

    def shutdown(self) -> None:
        """Shutdown scheduler."""
        self._running = False
        self.clear()

    # ==========================================================
    # Queue Operations
    # ==========================================================

    def enqueue(
        self,
        task: Any,
    ) -> None:
        """
        Add a task to the queue.
        """

        with self._lock:
            self._queue.append(task)
            self._tasks_enqueued += 1

    def extend(
        self,
        tasks: Iterable[Any],
    ) -> None:
        """
        Add multiple tasks.
        """

        for task in tasks:
            self.enqueue(task)

    def dequeue(self) -> Any:
        """
        Remove and return the next task.

        Raises
        ------
        IndexError
            If queue is empty.
        """

        with self._lock:

            if not self._queue:
                raise IndexError(
                    "Scheduler queue is empty."
                )

            self._tasks_dequeued += 1

            return self._queue.popleft()

    def peek(self) -> Any | None:
        """
        Return the next task without removing it.
        """

        with self._lock:

            if not self._queue:
                return None

            return self._queue[0]

    def clear(self) -> None:
        """
        Remove all queued tasks.
        """

        with self._lock:
            self._queue.clear()

    # ==========================================================
    # Query
    # ==========================================================

    def empty(self) -> bool:
        """
        True if queue is empty.
        """

        with self._lock:
            return len(self._queue) == 0

    @property
    def running(self) -> bool:
        """
        Scheduler running state.
        """

        return self._running

    @property
    def queue_size(self) -> int:
        """
        Number of queued tasks.
        """

        return len(self)

    # ==========================================================
    # Statistics
    # ==========================================================

    @property
    def tasks_enqueued(self) -> int:
        return self._tasks_enqueued

    @property
    def tasks_dequeued(self) -> int:
        return self._tasks_dequeued

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Scheduler status.
        """

        return {
            "running": self._running,
            "queue_size": len(self),
            "tasks_enqueued": self._tasks_enqueued,
            "tasks_dequeued": self._tasks_dequeued,
        }

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> None:
        """
        Reset scheduler.
        """

        self.clear()

        self._tasks_enqueued = 0
        self._tasks_dequeued = 0

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)

    def __bool__(self) -> bool:
        return not self.empty()

    def __iter__(self):
        with self._lock:
            return iter(tuple(self._queue))

    def __contains__(
        self,
        task: object,
    ) -> bool:
        with self._lock:
            return task in self._queue

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"running={self._running}, "
            f"queue_size={len(self)}, "
            f"enqueued={self._tasks_enqueued}, "
            f"dequeued={self._tasks_dequeued})"
        )