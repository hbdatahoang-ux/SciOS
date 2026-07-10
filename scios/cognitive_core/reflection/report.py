# scios/cognitive_core/reflection/report.py

"""
SciOS Reflection Report
=======================

ReflectionReport aggregates all outputs from the reflection pipeline
into a structured report. This report can be stored in history,
serialized, or used for memory updates.
"""

from __future__ import annotations
from typing import Any, Dict
from .base import ReflectionComponent


class ReflectionReport(ReflectionComponent):
    """
    ReflectionReport compiles evaluation, critique, analysis,
    metrics, score, and feedback into a unified report.
    """

    def __init__(self) -> None:
        super().__init__("ReflectionReport")

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
        Generate a reflection report from pipeline outputs.
        """
        report = {
            "evaluation": evaluation,
            "critique": critique,
            "analysis": analysis,
            "metrics": metrics,
            "score": score,
            "feedback": feedback,
            "summary": self._summarize(evaluation, critique, score),
        }
        return report

    def _summarize(
        self,
        evaluation: Dict[str, Any],
        critique: Dict[str, Any],
        score: Dict[str, Any],
    ) -> str:
        """
        Create a short textual summary of reflection outcome.
        """
        success = "successful" if evaluation.get("success") else "unsuccessful"
        weaknesses = critique.get("weaknesses", [])
        risks = critique.get("risks", [])
        final_score = score.get("final_score", 0.0)

        summary = (
            f"Execution was {success}. "
            f"Final score: {final_score:.2f}. "
        )
        if weaknesses:
            summary += f"Weaknesses noted: {', '.join(weaknesses)}. "
        if risks:
            summary += f"Risks identified: {', '.join(risks)}. "

        return summary.strip()

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps generate().
        Expects keys: evaluation, critique, analysis, metrics, score, feedback.
        """
        return self.generate(
            data.get("evaluation", {}),
            data.get("critique", {}),
            data.get("analysis", {}),
            data.get("metrics", {}),
            data.get("score", {}),
            data.get("feedback", {}),
        )
