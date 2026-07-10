# scios/cognitive_core/reflection/stage.py

"""
SciOS Reflection Stage
======================

ReflectionStage defines the stages of the reflection pipeline.
It provides a structured enumeration of all steps in the process.
"""

from __future__ import annotations
from enum import Enum


class ReflectionStage(Enum):
    """
    ReflectionStage enumerates the steps in the reflection pipeline.
    """

    EVALUATION = "evaluation"
    CRITIQUE = "critique"
    ANALYSIS = "analysis"
    METRICS = "metrics"
    SCORING = "scoring"
    IMPROVEMENT = "improvement"
    FEEDBACK = "feedback"
    REPORT = "report"
    SELF_REVIEW = "self_review"
    VALIDATION = "validation"
    ADAPTIVE = "adaptive"

    def __str__(self) -> str:
        return self.value


class StageTracker:
    """
    StageTracker keeps track of the current stage in reflection.
    """

    def __init__(self) -> None:
        self.current_stage: ReflectionStage = ReflectionStage.EVALUATION

    def advance(self) -> None:
        """
        Advance to the next stage in the pipeline.
        """
        stages = list(ReflectionStage)
        idx = stages.index(self.current_stage)
        if idx < len(stages) - 1:
            self.current_stage = stages[idx + 1]

    def reset(self) -> None:
        """
        Reset to the first stage (Evaluation).
        """
        self.current_stage = ReflectionStage.EVALUATION

    def get_stage(self) -> ReflectionStage:
        """
        Return the current stage.
        """
        return self.current_stage

    def __repr__(self) -> str:
        return f"<StageTracker current_stage={self.current_stage}>"
