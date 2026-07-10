# scios/kernel/execution.py

"""
SciOS Execution Engine

Responsibilities
----------------
- Validate tasks.
- Execute tasks via Dispatcher.
- Provide batch execution.
"""

from __future__ import annotations
from typing import Any, Iterable
import logging

from .scheduler import Task
from .dispatcher import Dispatcher


logger = logging.getLogger("SciOS.ExecutionEngine")


class ExecutionEngine:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher

    def validate(self, task: Task) -> None:
        """Validate a task before execution."""
        if task is None:
            raise ValueError("Task cannot be None.")
        if task.payload is None:
            raise ValueError(f"Task '{task.name}' has no payload.")

    def execute(self, task: Task) -> Any:
        """Execute a single task via Dispatcher."""
        self.validate(task)
        try:
            result = self._dispatcher.dispatch(task)
            return result
        except Exception as e:
            logger.exception("Execution failed for task %s", task.id)
            raise

    def execute_batch(self, tasks: Iterable[Task]) -> list[Any]:
        """Execute multiple tasks sequentially."""
        results = []
        for task in tasks:
            results.append(self.execute(task))
        return results

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dispatcher={self._dispatcher})"
