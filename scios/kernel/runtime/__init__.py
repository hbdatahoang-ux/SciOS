"""
SciOS Runtime
=============

Kernel Runtime subsystem.

This package provides the execution engine responsible for
dispatching tasks from the Kernel Scheduler to the cognitive
Agent pipeline.

Public API
----------
Runtime
    Kernel runtime execution engine.
"""

from .engine import Runtime

__all__ = [
    "Runtime",
]