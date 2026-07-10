# scios/cognitive_core/reflection/validator.py

"""
SciOS Reflection Validator
==========================

Validator checks the integrity and validity of reflection data.
It ensures that evaluation, critique, analysis, metrics, score,
and feedback conform to expected schema and values.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class Validator(ReflectionComponent):
    """
    Validator enforces schema and value checks for reflection pipeline data.
    """

    def __init__(self) -> None:
        super().__init__("Validator")

    def validate(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a reflection report and return issues + status.
        """
        issues: List[str] = []
        confirmations: List[str] = []

        # Required sections
        required_sections = ["evaluation", "critique", "analysis", "metrics", "score", "feedback"]
        for section in required_sections:
            if section not in report:
                issues.append(f"Missing section: {section}")
            else:
                confirmations.append(f"Section {section} present")

        # Validate score
        score = report.get("score", {}).get("final_score")
        if score is None:
            issues.append("Missing final_score in report")
        elif not isinstance(score, (int, float)):
            issues.append("Score must be numeric")
        elif not (0.0 <= score <= 1.0):
            issues.append(f"Score out of bounds: {score}")
        else:
            confirmations.append(f"Score valid: {score:.2f}")

        # Validate metrics
        metrics = report.get("metrics", {})
        for key in ["accuracy", "confidence", "latency", "coverage"]:
            if key not in metrics:
                issues.append(f"Missing metric: {key}")
            else:
                confirmations.append(f"Metric {key} present")

        validation = {
            "issues": issues,
            "confirmations": confirmations,
            "status": "valid" if not issues else "invalid",
        }

        return validation

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps validate().
        Expects key: report.
        """
        return self.validate(data.get("report", {}))
