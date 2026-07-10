# scios/kernel/scheduler.py
"""
SciOS Task Scheduler

Responsibilities
----------------
- Submit tasks into a queue.
- Retrieve next/peek tasks.
- Cancel tasks by id.
- Track task status and priority.
- Clear and inspect queue.

The Scheduler does NOT execute tasks.
Execution belongs to the Execution Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional
import threading
import collections
import uuid


class TaskPriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(slots=True)
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    payload: Any = None
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id}, name={self.name}, "
            f"priority={self.priority.name}, status={self.status.name})"
        )


class Scheduler:
    """
    Thread-safe task scheduler for SciOS Kernel.
    """

    def __init__(self) -> None:
        self._queue: collections.deque[Task] = collections.deque()
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def submit(self, task: Task) -> None:
        """Submit a new task into the queue."""
        with self._lock:
            self._queue.append(task)

    def next(self) -> Optional[Task]:
        """Pop and return the next task."""
        with self._lock:
            if not self._queue:
                return None
            task = self._queue.popleft()
            task.status = TaskStatus.RUNNING
            return task

    def peek(self) -> Optional[Task]:
        """Return the next task without removing it."""
        with self._lock:
            return self._queue[0] if self._queue else None

    def cancel(self, task_id: str) -> bool:
        """Cancel a task by id."""
        with self._lock:
            for task in list(self._queue):
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    self._queue.remove(task)
                    return True
            return False

    def clear(self) -> None:
        """Clear all tasks."""
        with self._lock:
            self._queue.clear()

    def count(self) -> int:
        """Number of tasks in queue."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return True if queue is empty."""
        return self.count() == 0

    # ------------------------------------------------------------------
    # Pythonic helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        with self._lock:
            return iter(tuple(self._queue))

    def __contains__(self, task: object) -> bool:
        if not isinstance(task, Task):
            return False
        with self._lock:
            return any(t.id == task.id for t in self._queue)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tasks={len(self)})"
