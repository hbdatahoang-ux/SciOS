# scios/cognitive_core/reflection/scorer.py

"""
SciOS Reflection Scorer
=======================

Scorer computes a bounded quality score from runtime metrics.

Contract
--------
- accuracy contributes positively.
- confidence contributes positively.
- latency contributes a small penalty.
- zero or negative latency has no penalty.
- final_score is always bounded to [0.0, 1.0].
"""

from __future__ import annotations

from typing import Any, Dict

from .base import ReflectionComponent


class Scorer(ReflectionComponent):
    """
    Aggregate quality metrics into a normalized score.

    Scoring contract
    ----------------
    accuracy   : 60%
    confidence : 40%
    latency    : small penalty, maximum 5%

    The result is always clamped to [0.0, 1.0].
    """

    def __init__(self) -> None:
        super().__init__("Scorer")

    def score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute a bounded quality score from metrics.
        """

        accuracy = float(metrics.get("accuracy", 0.0))
        confidence = float(metrics.get("confidence", 0.0))
        latency = float(metrics.get("latency", 0.0))

        # Keep input metrics within their expected normalized range.
        accuracy = max(0.0, min(1.0, accuracy))
        confidence = max(0.0, min(1.0, confidence))

        # Accuracy and confidence form the primary quality score.
        base_score = (
            0.6 * accuracy
            + 0.4 * confidence
        )

        # Latency is a secondary penalty.
        #
        # Zero/negative latency represents no measurable penalty.
        # Penalty is capped at 5% so latency cannot dominate quality.
        if latency <= 0.0:
            penalty = 0.0
        else:
            penalty = 0.05 * min(latency, 1.0)

        final_score = max(
            0.0,
            min(
                1.0,
                base_score - penalty,
            ),
        )

        return {
            "accuracy": accuracy,
            "confidence": confidence,
            "latency": latency,
            "final_score": final_score,
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard ReflectionComponent interface.
        """
        return self.score(data)
