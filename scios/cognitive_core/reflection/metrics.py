# scios/cognitive_core/reflection/metrics.py

"""
SciOS Reflection Metrics
========================

Metrics computes quantitative measures from execution results
and analysis, such as accuracy, confidence, latency, and coverage.
"""

from __future__ import annotations
from typing import Any, Dict
from .base import ReflectionComponent


class Metrics(ReflectionComponent):
    """
    Metrics computes evaluation measures from execution and analysis.
    """

    def __init__(self) -> None:
        super().__init__("Metrics")

    def compute(self, execution_result: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute metrics based on execution result and analysis.
        """
        success = execution_result.get("success", False)
        quality = execution_result.get("metrics", {}).get("quality", 0.0)
        latency = execution_result.get("metrics", {}).get("latency", 1.0)

        # Accuracy: proxy by success flag
        accuracy = 1.0 if success else 0.0

        # Confidence: proxy by quality score
        confidence = quality

        # Coverage: how many insights/mismatches were found
        coverage = len(analysis.get("insights", [])) + len(analysis.get("mismatches", []))

        metrics = {
            "accuracy": accuracy,
            "confidence": confidence,
            "latency": latency,
            "coverage": coverage,
        }

        return metrics

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps compute().
        Expects keys: execution_result, analysis.
        """
        return self.compute(
            data.get("execution_result", {}),
            data.get("analysis", {}),
        )

