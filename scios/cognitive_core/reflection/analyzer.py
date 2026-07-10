# scios/cognitive_core/reflection/analyzer.py

"""
SciOS Reflection Analyzer
=========================

Analyzer inspects reasoning traces, plans, and execution results
to detect mismatches, inconsistencies, and provide deeper insights.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class Analyzer(ReflectionComponent):
    """
    Analyzer compares reasoning, planning, and execution
    to identify mismatches and generate insights.
    """

    def __init__(self) -> None:
        super().__init__("Analyzer")

    def analyze(
        self,
        reasoning_trace: Dict[str, Any] | None,
        plan: Dict[str, Any] | None,
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze reasoning, plan, and execution result.
        """
        mismatches: List[str] = []
        insights: List[str] = []

        # Check if plan exists but execution failed
        if plan and execution_result.get("success") is False:
            mismatches.append("Plan was generated but execution failed")

        # Check if reasoning trace predicted success but execution failed
        if reasoning_trace and reasoning_trace.get("expected_success") and not execution_result.get("success"):
            mismatches.append("Reasoning predicted success but execution failed")

        # Check if execution succeeded but quality is low
        quality = execution_result.get("metrics", {}).get("quality")
        if execution_result.get("success") and quality is not None and quality < 0.5:
            mismatches.append("Execution succeeded but quality is low")

        # Generate insights
        if plan:
            insights.append(f"Plan contained {len(plan.get('tasks', []))} tasks")
        if reasoning_trace:
            insights.append("Reasoning trace available for analysis")

        analysis = {
            "mismatches": mismatches,
            "insights": insights,
        }

        return analysis

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps analyze().
        Expects keys: reasoning_trace, plan, execution_result.
        """
        return self.analyze(
            data.get("reasoning_trace"),
            data.get("plan"),
            data.get("execution_result"),
        )
