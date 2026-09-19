"""
SciOS Runtime Executor
======================

Core task executor for the SciOS Runtime.

Responsibilities
----------------
- Execute a single task.
- Create an ExecutionResult.
- Measure execution time.
- Handle execution errors.
- Remain independent of scheduling and workers.

Design Goals
------------
- Python 3.11+
- Stateless execution
- Deterministic behavior
- Zero external dependencies
"""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from .context import ExecutionContext
from .exceptions import ExecutionError
from .result import ExecutionResult

__all__ = [
    "Executor",
]


class Executor:
    """
    Execute a single task.

    The Executor is intentionally lightweight. Scheduling,
    retries, parallelism, and orchestration belong to higher
    runtime components.
    """

    def __init__(self) -> None:
        self._executions = 0

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def executions(self) -> int:
        """
        Number of executed tasks.
        """
        return self._executions

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute the task stored in the context.
        """

        task = context.task

        if not callable(task):
            raise ExecutionError(
                "Task must be callable."
            )

        started = perf_counter()

        try:
            value = task()

            success = True
            error = None

        except Exception as exc:  # noqa: BLE001

            value = None
            success = False
            error = exc

        elapsed = perf_counter() - started

        self._executions += 1

        result = ExecutionResult(
            success=success,
            value=value,
            error=error,
            duration=elapsed,
            metadata=context.metadata.copy(),
        )

        context.result = result

        return result

    # ==========================================================
    # Utility
    # ==========================================================

    def reset(self) -> None:
        """
        Reset execution statistics.
        """
        self._executions = 0

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __call__(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        return self.execute(context)

    def __len__(self) -> int:
        return self._executions

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"executions={self._executions})"
        )