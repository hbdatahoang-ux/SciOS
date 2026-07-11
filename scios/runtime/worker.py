"""
SciOS Runtime Worker
====================

Runtime worker responsible for executing execution contexts.

Responsibilities
----------------
- Execute one ExecutionContext at a time.
- Delegate execution to Executor.
- Maintain worker lifecycle.
- Track execution statistics.
- Remain scheduler-independent.

Design Goals
------------
- Python 3.11+
- Stateless task execution
- Thread-safe friendly
- Lightweight
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .context import ExecutionContext
from .exceptions import WorkerUnavailableError
from .executor import Executor
from .result import ExecutionResult
from .state import RuntimeState

__all__ = [
    "Worker",
]


class Worker:
    """
    Runtime execution worker.

    A Worker owns an Executor and is responsible for executing
    one ExecutionContext at a time.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        executor: Executor | None = None,
    ) -> None:

        self._id = str(uuid4())

        self._name = name or f"worker-{self._id[:8]}"

        self._executor = executor or Executor()

        self._state: RuntimeState = "idle"

        self._enabled = True

        self._tasks_completed = 0

        self._created_at = datetime.now(
            timezone.utc
        )

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> RuntimeState:
        return self._state

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def executor(self) -> Executor:
        return self._executor

    @property
    def tasks_completed(self) -> int:
        return self._tasks_completed

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """
        Initialize worker.
        """
        self._state = "idle"

    def shutdown(self) -> None:
        """
        Shutdown worker.
        """
        self._enabled = False
        self._state = "stopped"

    def enable(self) -> None:
        self._enabled = True

        if self._state == "stopped":
            self._state = "idle"

    def disable(self) -> None:
        self._enabled = False

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute one execution context.
        """

        if not self._enabled:
            raise WorkerUnavailableError(
                "Worker is disabled."
            )

        self._state = "running"

        try:

            result = self._executor.execute(context)

            self._tasks_completed += 1

            return result

        finally:

            if self._enabled:
                self._state = "idle"

    # ==========================================================
    # Statistics
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return worker status.
        """

        return {
            "id": self._id,
            "name": self._name,
            "state": self._state,
            "enabled": self._enabled,
            "tasks_completed": self._tasks_completed,
            "executor_executions": self._executor.executions,
            "created_at": self._created_at.isoformat(),
        }

    def reset(self) -> None:
        """
        Reset worker statistics.
        """

        self._tasks_completed = 0

        self._executor.reset()

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __call__(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        return self.execute(context)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"state={self._state!r}, "
            f"tasks_completed={self._tasks_completed})"
        )