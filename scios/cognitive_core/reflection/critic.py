"""
SciOS Reflection Critic
=======================

Analyzes evaluation results and identifies:
- strengths
- weaknesses
- risks
- issues

Compatible APIs:
- analyze()
- process()
- evaluate()

Python 3.11+
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "Critic",
]


class Critic:
    """
    Critic component of reflection pipeline.
    """


    def __init__(self) -> None:

        self.count = 0


    # ======================================================
    # Core Analysis
    # ======================================================

    def analyze(
        self,
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze execution evaluation.

        Expected input:

        {
            "success": True | False,
            "error": optional
        }

        Returns normalized critic report.
        """

        self.count += 1


        success = bool(
            evaluation.get(
                "success",
                False,
            )
        )


        strengths: list[str] = []

        weaknesses: list[str] = []

        risks: list[str] = []


        # --------------------------------------------------
        # Success case
        # --------------------------------------------------

        if success:

            strengths.append(
                "Execution succeeded"
            )


        # --------------------------------------------------
        # Failure case
        # --------------------------------------------------

        else:

            weaknesses.append(
                "Execution failed"
            )


            error = evaluation.get(
                "error"
            )


            if error:

                risks.append(
                    str(error)
                )


        return {

            "success":
                success,


            "strengths":
                strengths,


            "weaknesses":
                weaknesses,


            "risks":
                risks,


            # Backward compatibility
            "issues":
                weaknesses,


            "severity":
                (
                    "low"
                    if success
                    else "high"
                ),


            "criticized":
                True,

        }


    # ======================================================
    # Generic Process API
    # ======================================================

    def process(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generic processing entrypoint.

        Supports:

        {
            "evaluation": {
                "success": True
            }
        }

        """

        evaluation = data.get(
            "evaluation",
            data,
        )


        return self.analyze(
            evaluation
        )


    # ======================================================
    # Compatibility API
    # ======================================================

    def evaluate(
        self,
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Backward compatible alias.
        """

        return self.analyze(
            evaluation
        )


    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return critic statistics.
        """

        return {

            "count":
                self.count,


            "criticized":
                self.count,

        }


    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset critic state.
        """

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