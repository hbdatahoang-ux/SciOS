# scios/kernel/dispatcher.py
"""
SciOS Dispatcher

Responsibilities
----------------
- Fetch tasks from Scheduler.
- Dispatch tasks to Execution Engine.
- Update task status.
- Publish events via EventBus.
"""

from __future__ import annotations
from typing import Optional
import threading

from .scheduler import Task, TaskStatus, Scheduler
from .events import EventBus


class Dispatcher:
    """
    Thread-safe dispatcher for SciOS Kernel.
    """

    def __init__(self, scheduler: Scheduler, event_bus: Optional[EventBus] = None) -> None:
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._lock = threading.RLock()

    def dispatch(self) -> Optional[Task]:
        """
        Fetch next task from scheduler and mark as dispatched.
        """
        with self._lock:
            task = self._scheduler.next()
            if not task:
                return None

            # Publish event
            if self._event_bus:
                self._event_bus.publish("dispatcher.task_dispatched", task=task)

            return task

    def complete(self, task: Task, success: bool = True) -> None:
        """
        Mark a task as completed or failed.
        """
        with self._lock:
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

            if self._event_bus:
                event = "dispatcher.task_completed" if success else "dispatcher.task_failed"
                self._event_bus.publish(event, task=task)

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task via scheduler.
        """
        with self._lock:
            result = self._scheduler.cancel(task_id)
            if result and self._event_bus:
                self._event_bus.publish("dispatcher.task_cancelled", task_id=task_id)
            return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(scheduler={len(self._scheduler)})"
