"""
SciOS Runtime Package
=====================

Runtime subsystem of the SciOS Kernel.

The Runtime is responsible for coordinating task execution through:

    Runtime
        ↓
    RuntimeExecutor
        ↓
    Worker
        ↓
    RuntimeLoop

This package intentionally contains no cognitive logic.
"""

from .runtime import Runtime, RuntimeState
from .executor import RuntimeExecutor
from .worker import Worker
from .loop import RuntimeLoop

__all__ = [
    # runtime
    "Runtime",
    "RuntimeState",

    # execution
    "RuntimeExecutor",

    # workers
    "Worker",

    # runtime loop
    "RuntimeLoop",
]

__version__ = "0.2.0"