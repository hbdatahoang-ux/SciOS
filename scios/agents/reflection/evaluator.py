"""
SciOS Evaluator

Evaluates cognitive execution quality.
"""

from typing import Any, Dict


class Evaluator:
    """
    Reflection evaluator.

    Responsibilities
    ----------------
    - Evaluate execution quality
    - Compute confidence score
    - Decide whether execution is accepted
    """

    def evaluate(
        self,
        result: Dict[str, Any],
        critique: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate execution result.
        """

        issues = critique.get("issues", [])

        score = max(
            0.0,
            1.0 - 0.2 * len(issues)
        )

        accepted = (
            critique.get("accepted", False)
            and score >= 0.7
        )

        return {
            "accepted": accepted,
            "score": round(score, 2),
            "confidence": self._confidence(score),
            "recommendation": (
                "continue"
                if accepted
                else "replan"
            ),
        }

    def _confidence(self, score: float) -> str:
        """
        Convert numeric score to confidence level.
        """

        if score >= 0.90:
            return "very_high"

        if score >= 0.75:
            return "high"

        if score >= 0.50:
            return "medium"

        return "low"

    def status(self):
        """
        Evaluator status.
        """

        return {
            "component": "Evaluator",
            "status": "ready",
        }