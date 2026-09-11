"""
SciOS Plan Compilation Errors
=============================

Errors raised at the Cognitive Plan -> ExecutionGraph boundary.
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
    """Base exception for Cognitive Plan -> ExecutionGraph compilation."""


class InvalidPlanError(PlanCompilationError):
    """Raised when a Plan is invalid or structurally unusable."""


class MissingTaskDependencyError(InvalidPlanError):
    """Raised when a Task references an unknown or unusable dependency."""


class UnsupportedTaskError(InvalidPlanError):
    """Raised when a planning object cannot be lowered to an ExecutionNode."""


class CyclicPlanError(PlanCompilationError):
    """Raised when the source planning graph contains a cycle."""