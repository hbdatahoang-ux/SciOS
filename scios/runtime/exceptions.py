"""
SciOS Runtime Exceptions
========================

Canonical exception hierarchy for the SciOS Runtime.

Responsibilities
----------------
- Provide a common Runtime exception hierarchy.
- Enable fine-grained exception handling.
- Keep Runtime independent from higher-level modules.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    # Base
    "RuntimeError",
    "RuntimeInitializationError",

    # Execution
    "ExecutionError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",

    # Context
    "ContextError",
    "InvalidContextError",

    # Scheduler
    "SchedulerError",
    "QueueEmptyError",
    "TaskRejectedError",

    # Worker
    "WorkerError",
    "WorkerUnavailableError",

    # Executor
    "ExecutorError",

    # Validation
    "InvalidTaskError",
]


# ==========================================================
# Base Runtime Exceptions
# ==========================================================


class RuntimeError(Exception):
    """
    Base class for all SciOS Runtime exceptions.
    """

    def __init__(
        self,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message

        self.metadata = metadata or {}

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r})"
        )


class RuntimeInitializationError(RuntimeError):
    """
    Runtime failed to initialize.
    """


# ==========================================================
# Execution
# ==========================================================


class ExecutionError(RuntimeError):
    """
    Generic execution failure.
    """


class ExecutionTimeoutError(ExecutionError):
    """
    Execution exceeded its timeout.
    """


class ExecutionCancelledError(ExecutionError):
    """
    Execution cancelled before completion.
    """


# ==========================================================
# Context
# ==========================================================


class ContextError(RuntimeError):
    """
    Base execution context error.
    """


class InvalidContextError(ContextError):
    """
    Invalid execution context.
    """


# ==========================================================
# Scheduler
# ==========================================================


class SchedulerError(RuntimeError):
    """
    Scheduler failure.
    """


class QueueEmptyError(SchedulerError):
    """
    Task queue is empty.
    """


class TaskRejectedError(SchedulerError):
    """
    Scheduler rejected a task.
    """


# ==========================================================
# Worker
# ==========================================================


class WorkerError(RuntimeError):
    """
    Worker failure.
    """


class WorkerUnavailableError(WorkerError):
    """
    No worker available.
    """


# ==========================================================
# Executor
# ==========================================================


class ExecutorError(RuntimeError):
    """
    Executor failed.
    """


# ==========================================================
# Validation
# ==========================================================


class InvalidTaskError(ExecutionError):
    """
    Invalid task submitted to Runtime.
    """