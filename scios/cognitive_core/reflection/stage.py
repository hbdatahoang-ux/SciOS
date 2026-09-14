"""
SciOS Reflection Stage
======================

Reflection lifecycle stage definitions
and stage tracking.

Python 3.11+
"""

from __future__ import annotations

from enum import Enum
from typing import Any


__all__ = [
    "ReflectionStage",
    "StageTracker",
]



class ReflectionStage(Enum):
    """
    Reflection pipeline stages.
    """

    INITIALIZED = "initialized"

    EVALUATION = "evaluation"

    CRITIQUE = "critique"

    ANALYSIS = "analysis"

    METRICS = "metrics"

    # canonical
    SCORING = "scoring"

    # compatibility
    SCORE = "score"

    IMPROVEMENT = "improvement"

    FEEDBACK = "feedback"

    REPORT = "report"

    SELF_REVIEW = "self_review"

    VALIDATION = "validation"

    ADAPTIVE = "adaptive"

    COMPLETED = "completed"


    def __str__(self) -> str:

        return self.value
