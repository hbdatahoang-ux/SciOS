# scios/cognitive_core/reflection/scorer.py

"""
SciOS Reflection Scorer
=======================

Scorer computes a quality score from metrics.
It aggregates accuracy, confidence, latency, and other measures
into a single numeric score for evaluation.
"""

from __future__ import annotations
from typing import Any, Dict
from .base import ReflectionComponent


class Scorer(ReflectionComponent):
    """
    Scorer aggregates metrics into a quality score.
    """

    def __init__(self) -> None:
        super().__init__("Scorer")

    def score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute a score from metrics.
        """
        accuracy = metrics.get("accuracy", 0.0)
        confidence = metrics.get("confidence", 0.0)
        latency = metrics.get("latency", 1.0)  # default to 1s if missing

        # Simple heuristic: weighted average
        # Accuracy and confidence are positive, latency penalizes
        base_score = (0.6 * accuracy) + (0.3 * confidence)
        penalty = 0.1 * (latency / max(latency, 1.0))  # normalize

        final_score = max(0.0, min(1.0, base_score - penalty))

        return {
            "accuracy": accuracy,
            "confidence": confidence,
            "latency": latency,
            "final_score": final_score,
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps score().
        """
        return self.score(data)
