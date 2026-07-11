"""
SciOS Runtime
=============

Runtime execution layer of the Scientific Cognitive Operating System.

The Runtime is responsible for transforming executable tasks into
ExecutionResult objects through the coordinated operation of the
ExecutionEngine, Scheduler, Worker, and Executor.

Architecture
------------
    ExecutionEngine
            │
     ┌──────┴──────┐
     │             │
 Scheduler      Worker
     │             │
     ▼             ▼
ExecutionContext Executor
            │
            ▼
     ExecutionResult

Public API
----------
Core
    ExecutionEngine
    Scheduler
    Worker
    Executor

Data Models
    ExecutionContext
    ExecutionResult

State
    RuntimeState
    RuntimeStatus

Exceptions
    RuntimeError
    RuntimeInitializationError
    ExecutionError
    ExecutionTimeoutError
    ExecutionCancelledError
    InvalidTaskError
    ContextError
    InvalidContextError
    SchedulerError
    QueueEmptyError
    TaskRejectedError
    WorkerError
    WorkerUnavailableError
    ExecutorError
"""

from __future__ import annotations

# ==========================================================
# Core Runtime Components
# ==========================================================

from .engine import ExecutionEngine
from .scheduler import Scheduler
from .worker import Worker
from .executor import Executor

# ==========================================================
# Data Models
# ==========================================================

from .context import ExecutionContext
from .result import ExecutionResult

# ==========================================================
# Runtime State
# ==========================================================

from .state import (
    RuntimeState,
    RuntimeStatus,
)

# ==========================================================
# Exceptions
# ==========================================================

from .exceptions import (
    RuntimeError,
    RuntimeInitializationError,

    ExecutionError,
    ExecutionTimeoutError,
    ExecutionCancelledError,

    ContextError,
    InvalidContextError,

    SchedulerError,
    QueueEmptyError,
    TaskRejectedError,

    WorkerError,
    WorkerUnavailableError,

    ExecutorError,

    InvalidTaskError,
)

# ==========================================================
# Version
# ==========================================================

__version__ = "0.3.0-alpha"

# ==========================================================
# Public API
# ==========================================================

__all__ = [
    # Engine
    "ExecutionEngine",

    # Core
    "Scheduler",
    "Worker",
    "Executor",

    # Models
    "ExecutionContext",
    "ExecutionResult",

    # State
    "RuntimeState",
    "RuntimeStatus",

    # Exceptions
    "RuntimeError",
    "RuntimeInitializationError",

    "ExecutionError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",

    "ContextError",
    "InvalidContextError",

    "SchedulerError",
    "QueueEmptyError",
    "TaskRejectedError",

    "WorkerError",
    "WorkerUnavailableError",

    "ExecutorError",

    "InvalidTaskError",
]