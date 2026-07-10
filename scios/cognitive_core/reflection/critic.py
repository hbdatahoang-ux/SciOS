# scios/cognitive_core/reflection/critic.py

"""
SciOS Reflection Critic
=======================

Critic inspects evaluation results and highlights
strengths, weaknesses, and potential issues.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class Critic(ReflectionComponent):
    """
    Critic analyzes evaluation output to identify
    strengths, weaknesses, and risks.
    """

    def __init__(self) -> None:
        super().__init__("Critic")

    def analyze(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze evaluation results and return critique.
        """
        strengths: List[str] = []
        weaknesses: List[str] = []
        risks: List[str] = []

        # Basic heuristic: success → strength, failure → weakness
        if evaluation.get("success"):
            strengths.append("Task executed successfully")
        else:
            weaknesses.append("Task execution failed")

        # Check metrics quality
        quality = evaluation.get("metrics", {}).get("quality")
        if quality is not None:
            if quality >= 0.8:
                strengths.append(f"High quality score ({quality})")
            elif quality < 0.5:
                weaknesses.append(f"Low quality score ({quality})")
                risks.append("Output may be unreliable")

        # Notes can reveal warnings
        notes = evaluation.get("notes", "")
        if "warning" in notes.lower():
            risks.append("Execution produced warnings")

        critique = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "risks": risks,
        }

        return critique

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps analyze().
        """
        return self.analyze(data)
