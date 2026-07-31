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



class StageTracker:
    """
    Tracks reflection pipeline stages.

    Compatible APIs:

    tracker.advance()

    tracker.advance("evaluation")

    tracker.get_stage()
    """



    def __init__(
        self,
    ) -> None:

        self.current_stage = (
            ReflectionStage.INITIALIZED
        )

        self.history = [
            self.current_stage
        ]



    # ==================================================
    # Advance
    # ==================================================

    def advance(
        self,
        stage: str | ReflectionStage | None = None,
    ) -> str:
        """
        Advance stage.

        Supports:

        advance()
            -> next stage

        advance("analysis")
            -> move to analysis
        """

        if stage is not None:

            self.move_to(
                stage
            )

            return self.current_stage.value



        stages = list(
            ReflectionStage
        )


        index = stages.index(
            self.current_stage
        )


        if index < len(stages) - 1:

            self.current_stage = (
                stages[index + 1]
            )

            self.history.append(
                self.current_stage
            )


        return self.current_stage.value



    # ==================================================
    # Move
    # ==================================================

    def move_to(
        self,
        stage: str | ReflectionStage,
    ) -> None:
        """
        Move directly to stage.
        """

        if isinstance(
            stage,
            str,
        ):

            try:

                stage = ReflectionStage(
                    stage
                )

            except ValueError:

                raise ValueError(
                    f"Unknown reflection stage: {stage}"
                )


        self.current_stage = stage


        self.history.append(
            stage
        )



    # ==================================================
    # Reset
    # ==================================================

    def reset(
        self,
    ) -> None:

        self.current_stage = (
            ReflectionStage.INITIALIZED
        )

        self.history = [
            self.current_stage
        ]



    # ==================================================
    # Query
    # ==================================================

    def get_stage(
        self,
    ) -> str:

        return self.current_stage.value



    def get_stage_enum(
        self,
    ) -> ReflectionStage:

        return self.current_stage



    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "stage":
                self.current_stage.value,

            "history":
                [
                    s.value
                    for s in self.history
                ],

        }



    # ==================================================
    # Protocol
    # ==================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "<StageTracker "
            f"current_stage={self.current_stage.value}>"
        )