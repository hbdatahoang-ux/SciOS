"""
SciOS Runtime
=============

Runtime execution layer of the Scientific Cognitive Operating System.

The Runtime transforms executable tasks into Runtime results through
ExecutionEngine, Pipeline, Stage, Scheduler, Worker, and Executor coordination.

Architecture
------------

    ExecutionEngine
            |
        Pipeline
            |
        +---+---+
        |       |
      Stage   Stage
        |
     Executor


Public API
----------

Core Components
    ExecutionEngine
    Pipeline
    Stage
    Scheduler
    Worker
    Executor

Models
    ExecutionContext
    ExecutionResult

State
    RuntimeState
    RuntimeStatus

Events
    RuntimeEvent
    EventType

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

from .pipeline import Pipeline

from .stage import Stage

from .scheduler import Scheduler

from .worker import Worker

from .executor import Executor



# ==========================================================
# Execution Models
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
# Runtime Events
# ==========================================================

try:

    from .events import (
        RuntimeEvent,
        EventType,
    )

except ImportError:

    RuntimeEvent = None

    EventType = None



# ==========================================================
# Runtime Exceptions
# ==========================================================

from .exceptions import (

    RuntimeError,

    RuntimeInitializationError,


    ExecutionError,

    ExecutionTimeoutError,

    ExecutionCancelledError,


    InvalidTaskError,


    ContextError,

    InvalidContextError,


    SchedulerError,

    QueueEmptyError,

    TaskRejectedError,


    WorkerError,

    WorkerUnavailableError,


    ExecutorError,

)



# ==========================================================
# Version
# ==========================================================

__version__ = "0.3.0-alpha"



# ==========================================================
# Public API
# ==========================================================

__all__ = [

    # ------------------------------------------------------
    # Engine
    # ------------------------------------------------------

    "ExecutionEngine",



    # ------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------

    "Pipeline",

    "Stage",



    # ------------------------------------------------------
    # Runtime Components
    # ------------------------------------------------------

    "Scheduler",

    "Worker",

    "Executor",



    # ------------------------------------------------------
    # Execution Models
    # ------------------------------------------------------

    "ExecutionContext",

    "ExecutionResult",



    # ------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------

    "RuntimeState",

    "RuntimeStatus",



    # ------------------------------------------------------
    # Events
    # ------------------------------------------------------

    "RuntimeEvent",

    "EventType",



    # ------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------

    "RuntimeError",

    "RuntimeInitializationError",


    "ExecutionError",

    "ExecutionTimeoutError",

    "ExecutionCancelledError",


    "InvalidTaskError",


    "ContextError",

    "InvalidContextError",


    "SchedulerError",

    "QueueEmptyError",

    "TaskRejectedError",


    "WorkerError",

    "WorkerUnavailableError",


    "ExecutorError",



    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    "__version__",

]