"""
SciOS Reflection Pipeline
=========================

High-level reflection orchestration layer.

Compatibility wrapper around ReflectionEngine
with complete pipeline contract.

Python 3.11+
"""

from __future__ import annotations

from typing import Any


try:
    from .reflection import ReflectionEngine

except ImportError:

    try:
        from .reflection import Reflector as ReflectionEngine

    except ImportError:

        class ReflectionEngine:
            """
            Minimal fallback reflection engine.
            """

            def __init__(
                self,
                *args: Any,
                **kwargs: Any,
            ) -> None:

                self.state = {}


            def run(
                self,
                data: dict[str, Any] | None = None,
            ) -> dict[str, Any]:

                return data or {}


            def process(
                self,
                data: dict[str, Any] | None = None,
            ) -> dict[str, Any]:

                return self.run(
                    data
                )



__all__ = [
    "ReflectionPipeline",
]



class ReflectionPipeline(ReflectionEngine):
    """
    SciOS Reflection Pipeline.

    Extends ReflectionEngine with:

    - improvement generation
    - report aggregation
    - self review
    - validation

    Supported APIs:

    - run()
    - process()
    - execute()
    - status()
    - reset()
    """



    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            *args,
            **kwargs
        )



    # ======================================================
    # Main Pipeline Execution
    # ======================================================

    def run(
        self,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute full reflection pipeline.
        """

        data = data or {}


        # --------------------------------------------------
        # Execute ReflectionEngine
        # --------------------------------------------------

        try:

            base_report = super().run(
                data
            )


        except Exception:

            base_report = {}



        if not isinstance(
            base_report,
            dict,
        ):

            base_report = {}



        # --------------------------------------------------
        # Extract pipeline components
        # --------------------------------------------------

        evaluation = base_report.get(
            "evaluation",
            {
                "success": False,
            },
        )


        critique = base_report.get(
            "critique",
            {},
        )


        analysis = base_report.get(
            "analysis",
            {},
        )


        metrics = base_report.get(
            "metrics",
            {},
        )


        score = base_report.get(
            "score",
            {
                "final_score": 0.0,
            },
        )


        improvement = base_report.get(
            "improvement",
            {},
        )


        feedback = base_report.get(
            "feedback",
            {},
        )



        # --------------------------------------------------
        # Improvement fallback
        # --------------------------------------------------

        if not improvement:

            improvement = self._generate_improvement(
                analysis,
                critique,
                score,
            )



        # --------------------------------------------------
        # Build final report object
        # --------------------------------------------------

        report = {

            "evaluation":
                evaluation,

            "critique":
                critique,

            "analysis":
                analysis,

            "metrics":
                metrics,

            "score":
                score,

            "improvement":
                improvement,

            "feedback":
                feedback,

            "summary":
                (
                    "Reflection completed successfully"
                    if evaluation.get(
                        "success",
                        False,
                    )
                    else
                    "Reflection detected execution failure"
                ),

        }



        # --------------------------------------------------
        # Self review
        # --------------------------------------------------

        self_review = {

            "status":
                "completed",

            "components":
                list(
                    report.keys()
                ),

            "quality":
                (
                    "good"
                    if evaluation.get(
                        "success",
                        False,
                    )
                    else
                    "needs_improvement"
                ),

        }



        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        validation = {

            "status":
                (
                    "valid"
                    if evaluation.get(
                        "success",
                        False,
                    )
                    else
                    "invalid"
                ),

            "valid":
                evaluation.get(
                    "success",
                    False,
                ),

            "checked":
                True,

            "missing":
                [],

        }



        return {

            **report,

            "report":
                report,

            "self_review":
                self_review,

            "validation":
                validation,

        }



    # ======================================================
    # Compatibility APIs
    # ======================================================

    def process(
        self,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        return self.run(
            data
        )



    def execute(
        self,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        return self.run(
            data
        )



    # ======================================================
    # Improvement fallback
    # ======================================================

    def _generate_improvement(
        self,
        analysis: dict[str, Any],
        critique: dict[str, Any],
        score: dict[str, Any],
    ) -> dict[str, list[str]]:
        """
        Generate safe improvement suggestions.
        """

        result = {

            "execution": [],

            "planning": [],

            "reasoning": [],

        }



        for item in analysis.get(
            "mismatches",
            [],
        ):

            result["execution"].append(
                f"Resolve mismatch: {item}"
            )



        for item in critique.get(
            "weaknesses",
            [],
        ):

            result["execution"].append(
                f"Improve weakness: {item}"
            )



        for item in critique.get(
            "risks",
            [],
        ):

            result["execution"].append(
                f"Mitigate risk: {item}"
            )



        final_score = score.get(
            "final_score",
            1.0,
        )


        if final_score < 0.5:

            result["execution"].append(
                f"Low score: improve execution quality ({final_score})"
            )



        return result



    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset pipeline state.
        """

        if hasattr(
            super(),
            "reset",
        ):

            super().reset()



    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "component":
                self.__class__.__name__,

            "status":
                "ready",

        }



    # ======================================================
    # Protocol
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            "(status=ready)"
        )