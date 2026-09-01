"""
SciOS Cognitive Core - Errors
=============================

Common exception hierarchy for the Cognitive Core.

All domain-specific cognitive exceptions inherit from ``CognitiveError``.
This provides a single stable base type for callers that need to catch
Cognitive Core failures generically.
"""

from __future__ import annotations


class CognitiveError(Exception):
    """Base exception for all Cognitive Core errors."""


class PlannerError(CognitiveError):
    """Raised when planning or plan generation fails."""


class ReasoningError(CognitiveError):
    """Raised when reasoning or inference fails."""


class MemoryError(CognitiveError):
    """Raised when a memory operation fails."""


class ToolError(CognitiveError):
    """Raised when tool invocation or execution fails."""


class PipelineError(CognitiveError):
    """Raised when cognitive pipeline execution fails."""


__all__ = [
    "CognitiveError",
    "PlannerError",
    "ReasoningError",
    "MemoryError",
    "ToolError",
    "PipelineError",
]