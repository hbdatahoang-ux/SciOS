"""
SciOS Plan Compilation Errors
=============================

Errors raised at the Cognitive Plan -> Execution IR boundary.
"""

from __future__ import annotations


__all__ = [
    "PlanCompilationError",
    "InvalidPlanError",
    "MissingTaskDependencyError",
    "UnsupportedTaskError",
    "CyclicPlanError",
]


class PlanCompilationError(Exception):
    """Base exception for Plan -> ExecutionGraph compilation."""


class InvalidPlanError(PlanCompilationError):
    """Raised when the input Plan is invalid or structurally unusable."""


class MissingTaskDependencyError(PlanCompilationError):
    """Raised when a Task references a dependency that cannot be compiled."""


class UnsupportedTaskError(PlanCompilationError):
    """Raised when a Task cannot be lowered to an execution node."""


class CyclicPlanError(PlanCompilationError):
    """Raised when the source planning graph contains a cycle."""