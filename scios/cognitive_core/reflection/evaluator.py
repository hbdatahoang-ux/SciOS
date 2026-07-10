# scios/cognitive_core/reflection/evaluator.py

"""
SciOS Reflection Evaluator
==========================

Evaluator is the first step in the reflection pipeline.
It inspects execution results and produces a structured
evaluation summary (success/failure, metrics, notes).
"""

from __future__ import annotations
from typing import Any, Dict
from .base import ReflectionComponent


class Evaluator(ReflectionComponent):
    """
    Evaluator analyzes execution results and produces
    a structured evaluation dictionary.
    """

    def __init__(self) -> None:
        super().__init__("Evaluator")

    def evaluate(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate execution result and return summary.
        """
        success = execution_result.get("success", False)
        metrics = execution_result.get("metrics", {})
        notes = execution_result.get("notes", "")

        evaluation = {
            "success": success,
            "metrics": metrics,
            "notes": notes,
            "task": execution_result.get("task"),
            "timestamp": execution_result.get("timestamp"),
        }

        return evaluation

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps evaluate().
        """
        return self.evaluate(data)
