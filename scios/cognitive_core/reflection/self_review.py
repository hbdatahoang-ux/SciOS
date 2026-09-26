# scios/cognitive_core/reflection/self_review.py

"""
SciOS Reflection Self-Review
============================

SelfReview performs a meta-level audit of the reflection process.
It checks for consistency, completeness, and potential biases
in the generated reflection report.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class SelfReview(ReflectionComponent):
    """
    SelfReview audits reflection reports to ensure quality and consistency.
    """

    def __init__(self) -> None:
        super().__init__("SelfReview")

    def review(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform self-review on a reflection report.
        """
        issues: List[str] = []
        confirmations: List[str] = []

        # Check if all major sections exist
        required_sections = ["evaluation", "critique", "analysis", "metrics", "score", "feedback"]
        for section in required_sections:
            if section not in report:
                issues.append(f"Missing section: {section}")
            else:
                confirmations.append(f"Section {section} present")

        # Check if score is consistent
        score = report.get("score", {}).get("final_score")
        if score is None:
            issues.append("Score missing in report")
        elif not (0.0 <= score <= 1.0):
            issues.append(f"Score out of bounds: {score}")
        else:
            confirmations.append(f"Score valid: {score:.2f}")

        # Check if feedback has actionable suggestions
        feedback = report.get("feedback", {})
        if not feedback.get("suggestions"):
            issues.append("No actionable feedback provided")
        else:
            confirmations.append("Feedback contains actionable suggestions")

        self_review = {
            "issues": issues,
            "confirmations": confirmations,
            "status": "passed" if not issues else "needs_revision",
        }

        return self_review

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps review().
        Expects key: report.
        """
        return self.review(data.get("report", {}))
