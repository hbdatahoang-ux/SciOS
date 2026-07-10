# scios/cognitive_core/reflection/feedback.py

"""
SciOS Reflection Feedback
=========================

Feedback generates actionable suggestions and reflective notes
based on improvement proposals. It provides human-readable
guidance for the system and user.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class Feedback(ReflectionComponent):
    """
    Feedback transforms improvement suggestions into
    actionable guidance and reflective notes.
    """

    def __init__(self) -> None:
        super().__init__("Feedback")

    def generate(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate feedback messages from improvement suggestions.
        """
        suggestions: List[str] = []
        notes: List[str] = []

        # Turn improvements into feedback
        for category, items in improvements.items():
            if not items:
                continue
            for item in items:
                suggestions.append(f"Consider {item} in {category}")
                notes.append(f"Improvement identified in {category}: {item}")

        feedback = {
            "suggestions": suggestions,
            "notes": notes,
        }

        return feedback

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps generate().
        """
        return self.generate(data)
