# ==============================================================================
# SciOS Runtime Science
# Scientific Execution Errors
# ==============================================================================

from __future__ import annotations


# ==============================================================================
# Base Error
# ==============================================================================


class ExecutionError(RuntimeError):
    """
    Base exception for scientific execution failures.

    All execution-layer exceptions should derive from this class.
    """


# ==============================================================================
# Validation Errors
# ==============================================================================


class InvalidExecutionError(
    ExecutionError,
    ValueError,
):
    """
    Raised when an execution request is invalid.
    """


class InvalidExecutionContextError(
    InvalidExecutionError,
):
    """
    Raised when an execution context is invalid.
    """


class InvalidExecutionResultError(
    InvalidExecutionError,
):
    """
    Raised when an execution result is invalid.
    """


# ==============================================================================
# Lifecycle Errors
# ==============================================================================


class ExecutionStateError(
    ExecutionError,
):
    """
    Raised when an execution lifecycle transition is invalid.
    """


class ExecutionAlreadyStartedError(
    ExecutionStateError,
):
    """
    Raised when an already-started execution is started again.
    """


class ExecutionNotStartedError(
    ExecutionStateError,
):
    """
    Raised when an operation requires execution to have started.
    """


class ExecutionAlreadyCompletedError(
    ExecutionStateError,
):
    """
    Raised when an operation is attempted after successful completion.
    """


class ExecutionAlreadyFailedError(
    ExecutionStateError,
):
    """
    Raised when an operation is attempted after execution failure.
    """


# ==============================================================================
# Runtime Errors
# ==============================================================================


class ExecutionFailedError(
    ExecutionError,
):
    """
    Raised when scientific execution fails during runtime.
    """


class ExecutionTimeoutError(
    ExecutionFailedError,
):
    """
    Raised when scientific execution exceeds its allowed duration.
    """


class ExecutionCancelledError(
    ExecutionFailedError,
):
    """
    Raised when scientific execution is explicitly cancelled.
    """


# ==============================================================================
# Dependency Errors
# ==============================================================================


class ExecutionDependencyError(
    ExecutionError,
):
    """
    Raised when an execution dependency is unavailable or invalid.
    """


class WorldExecutionError(
    ExecutionDependencyError,
):
    """
    Raised when execution cannot interact with the synthetic world.
    """


# ==============================================================================
# Public API
# ==============================================================================


__all__ = [
    "ExecutionError",
    "InvalidExecutionError",
    "InvalidExecutionContextError",
    "InvalidExecutionResultError",
    "ExecutionStateError",
    "ExecutionAlreadyStartedError",
    "ExecutionNotStartedError",
    "ExecutionAlreadyCompletedError",
    "ExecutionAlreadyFailedError",
    "ExecutionFailedError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",
    "ExecutionDependencyError",
    "WorldExecutionError",
]