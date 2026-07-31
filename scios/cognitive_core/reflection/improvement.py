"""
SciOS Reflection Improvement
============================

Generates improvement recommendations
from reflection analysis.

Compatible APIs:
- suggest()
- process()

Python 3.11+
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "Improvement",
]


class Improvement:
    """
    Improvement generator for reflection pipeline.
    """


    def __init__(self) -> None:

        self.count = 0


    # ======================================================
    # Core API
    # ======================================================

    def suggest(
        self,
        analysis: dict[str, Any],
        critique: dict[str, Any],
        score: dict[str, Any],
    ) -> dict[str, list[str]]:
        """
        Generate structured improvement suggestions.

        Output:

        {
            "execution": [],
            "planning": [],
            "reasoning": []
        }
        """

        self.count += 1


        result: dict[str, list[str]] = {

            "execution": [],

            "planning": [],

            "reasoning": [],

        }


        mismatches = analysis.get(
            "mismatches",
            [],
        )


        weaknesses = critique.get(
            "weaknesses",
            [],
        )


        risks = critique.get(
            "risks",
            [],
        )


        final_score = score.get(
            "final_score",
            1.0,
        )


        # ==================================================
        # Execution improvements
        # ==================================================

        for item in mismatches:

            result["execution"].append(
                f"Resolve mismatch: {item}"
            )


        for item in weaknesses:

            result["execution"].append(
                f"Improve weakness: {item}"
            )


        for item in risks:

            result["execution"].append(
                f"Mitigate risk: {item}"
            )


        # ==================================================
        # Low score handling
        # ==================================================

        if final_score < 0.5:

            result["execution"].append(
                f"Low score: improve execution quality ({final_score})"
            )


        # ==================================================
        # Planning improvements
        # ==================================================

        if analysis.get(
            "planning_issue",
            False,
        ):

            result["planning"].append(
                "Improve planning strategy"
            )


        # ==================================================
        # Reasoning improvements
        # ==================================================

        if analysis.get(
            "reasoning_issue",
            False,
        ):

            result["reasoning"].append(
                "Improve reasoning process"
            )


        return result


    # ======================================================
    # Process API
    # ======================================================

    def process(
        self,
        data: dict[str, Any],
    ) -> dict[str, list[str]]:
        """
        Standalone processing API.

        Input:

        {
            "analysis": {},
            "critique": {},
            "score": {}
        }
        """

        return self.suggest(

            analysis=data.get(
                "analysis",
                {},
            ),

            critique=data.get(
                "critique",
                {},
            ),

            score=data.get(
                "score",
                {},
            ),

        )


    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return component status.
        """

        return {

            "count": self.count,

        }


    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset internal state.
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