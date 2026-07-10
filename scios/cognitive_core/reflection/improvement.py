# scios/cognitive_core/reflection/improvement.py

"""
SciOS Reflection Improvement
============================

Improvement generates proposals for enhancing reasoning,
planning, and execution based on analysis, critique, and scores.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class Improvement(ReflectionComponent):
    """
    Improvement suggests actionable changes to improve
    system performance and reliability.
    """

    def __init__(self) -> None:
        super().__init__("Improvement")

    def suggest(
        self,
        analysis: Dict[str, Any],
        critique: Dict[str, Any],
        score: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """
        Generate improvement suggestions based on analysis, critique, and score.
        """
        suggestions: Dict[str, List[str]] = {
            "execution": [],
            "planning": [],
            "reasoning": [],
        }

        # If mismatches exist, suggest reviewing execution pipeline
        if analysis.get("mismatches"):
            suggestions["execution"].append("Review execution pipeline for reliability")

        # If weaknesses are present, suggest strengthening planning
        if critique.get("weaknesses"):
            suggestions["planning"].append("Refine planning strategy to address weaknesses")

        # If risks are present, suggest improving reasoning safeguards
        if critique.get("risks"):
            suggestions["reasoning"].append("Add safeguards in reasoning to mitigate risks")

        # If score is low, suggest overall improvement
        final_score = score.get("final_score", 0.0)
        if final_score < 0.5:
            suggestions["execution"].append("Investigate low performance causes")
            suggestions["planning"].append("Optimize task scheduling")
            suggestions["reasoning"].append("Re-evaluate assumptions in reasoning")

        return suggestions

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps suggest().
        Expects keys: analysis, critique, score.
        """
        return self.suggest(
            data.get("analysis", {}),
            data.get("critique", {}),
            data.get("score", {}),
        )
