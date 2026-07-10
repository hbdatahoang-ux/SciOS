"""
SciOS Cognitive Core - Errors
=============================

Defines common exception hierarchy for the Cognitive Core.
"""

class CognitiveError(Exception):
    """
    Base class for all cognitive errors.
    """
    pass


class PlannerError(CognitiveError):
    """
    Raised when planning fails.
    """
    pass


class ReasoningError(CognitiveError):
    """
    Raised when reasoning/inference fails.
    """
    pass


class MemoryError(CognitiveError):
    """
    Raised when memory operations fail.
    """
    pass


class ToolError(CognitiveError):
    """
    Raised when tool invocation fails.
    """
    pass


class PipelineError(CognitiveError):
    """
    Raised when pipeline execution fails.
    """
    pass
