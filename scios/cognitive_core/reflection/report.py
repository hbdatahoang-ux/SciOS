"""
SciOS Reflection Report
=======================

ReflectionReport aggregates all outputs from the reflection pipeline
into a structured report.

Supports:
- generate()
- process()
- summary generation
- pipeline compatibility

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Dict

from .base import ReflectionComponent


__all__ = [
    "ReflectionReport",
]


class ReflectionReport(ReflectionComponent):
    """
    ReflectionReport compiles all reflection outputs
    into a unified report.
    """

    def __init__(self) -> None:

        super().__init__(
            "ReflectionReport"
        )

        self.count = 0


    # ======================================================
    # Core API
    # ======================================================

    def generate(
        self,
        evaluation: Dict[str, Any],
        critique: Dict[str, Any],
        analysis: Dict[str, Any],
        metrics: Dict[str, Any],
        score: Dict[str, Any],
        feedback: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate complete reflection report.
        """

        self.count += 1

        return {

            "evaluation": evaluation,

            "critique": critique,

            "analysis": analysis,

            "metrics": metrics,

            "score": score,

            "feedback": feedback,

            "summary": self._summarize(
                evaluation,
                critique,
                analysis,
                metrics,
                score,
                feedback,
            ),

        }


    # ======================================================
    # Summary
    # ======================================================

    def _summarize(
        self,
        evaluation: Dict[str, Any],
        critique: Dict[str, Any],
        analysis: Dict[str, Any],
        metrics: Dict[str, Any],
        score: Dict[str, Any],
        feedback: Dict[str, Any],
    ) -> str:
        """
        Create human-readable reflection summary.
        """

        success = bool(
            evaluation.get(
                "success",
                False,
            )
        )


        raw_score = score.get(
            "final_score",
            0.0,
        )

        try:
            final_score = float(raw_score)

        except (
            TypeError,
            ValueError,
        ):
            final_score = 0.0


        weaknesses = critique.get(
            "weaknesses",
            [],
        )

        risks = critique.get(
            "risks",
            [],
        )

        insights = analysis.get(
            "insights",
            [],
        )

        mismatches = analysis.get(
            "mismatches",
            [],
        )

        suggestions = feedback.get(
            "suggestions",
            [],
        )


        parts: list[str] = []


        # ==================================================
        # Evaluation
        # ==================================================

        parts.append(
            "Evaluation: "
            +
            (
                "successful"
                if success
                else "failed"
            )
        )


        # ==================================================
        # Critique
        # ==================================================

        critique_items: list[str] = []


        if weaknesses:

            critique_items.append(
                "Weaknesses="
                +
                ", ".join(
                    map(
                        str,
                        weaknesses,
                    )
                )
            )


        if risks:

            critique_items.append(
                "Risks="
                +
                ", ".join(
                    map(
                        str,
                        risks,
                    )
                )
            )


        parts.append(
            "Critique: "
            +
            (
                "; ".join(
                    critique_items
                )
                if critique_items
                else "none"
            )
        )


        # ==================================================
        # Analysis
        # ==================================================

        analysis_items: list[str] = []


        if insights:

            analysis_items.append(
                "Insights="
                +
                ", ".join(
                    map(
                        str,
                        insights,
                    )
                )
            )


        if mismatches:

            analysis_items.append(
                "Mismatches="
                +
                ", ".join(
                    map(
                        str,
                        mismatches,
                    )
                )
            )


        parts.append(
            "Analysis: "
            +
            (
                "; ".join(
                    analysis_items
                )
                if analysis_items
                else "none"
            )
        )


        # ==================================================
        # Metrics
        # ==================================================

        if metrics:

            metrics_text = ", ".join(
                f"{key}={value}"
                for key, value
                in metrics.items()
            )

            parts.append(
                "Metrics: "
                +
                metrics_text
            )

        else:

            parts.append(
                "Metrics: none"
            )


        # ==================================================
        # Score
        # ==================================================

        parts.append(
            f"Score: {final_score:.2f}"
        )


        # ==================================================
        # Feedback
        # ==================================================

        parts.append(
            "Feedback: "
            +
            (
                ", ".join(
                    map(
                        str,
                        suggestions,
                    )
                )
                if suggestions
                else "none"
            )
        )


        return (
            ". ".join(parts)
            +
            "."
        )


    # ======================================================
    # Pipeline API
    # ======================================================

    def process(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Standard pipeline interface.
        """

        return self.generate(

            evaluation=data.get(
                "evaluation",
                {},
            ),

            critique=data.get(
                "critique",
                {},
            ),

            analysis=data.get(
                "analysis",
                {},
            ),

            metrics=data.get(
                "metrics",
                {},
            ),

            score=data.get(
                "score",
                {},
            ),

            feedback=data.get(
                "feedback",
                {},
            ),

        )


    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "generated":
                self.count,

        }


    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:

        self.count = 0


    # ======================================================
    # Protocol
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(count={self.count})"
        )