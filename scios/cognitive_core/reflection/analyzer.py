"""
SciOS Reflection Analyzer
=========================

Reflection analyzer for comparing reasoning, planning,
and execution results.

This implementation is intentionally lightweight,
deterministic and fully compatible with the unit tests.
"""

from __future__ import annotations

from typing import Any

from .base import ReflectionComponent

__all__ = [
    "Analyzer",
]


class Analyzer(ReflectionComponent):
    """
    Reflection Analyzer.
    """

    def __init__(self) -> None:
        super().__init__("Analyzer")

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    # ==========================================================
    # Core
    # ==========================================================

    def analyze(
        self,
        reasoning: dict[str, Any] | None = None,
        plan: dict[str, Any] | None = None,
        execution_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        reasoning = self._dict(reasoning)
        plan = self._dict(plan)
        execution_result = self._dict(execution_result)

        insights: list[str] = []
        mismatches: list[str] = []

        success = bool(execution_result.get("success", False))

        # ------------------------------------------------------
        # Compare prediction vs execution
        # ------------------------------------------------------

        prediction = reasoning.get("prediction")
        output = execution_result.get("output")

        if prediction is not None and output is not None:

            if prediction == output:

                insights.append(
                    "Execution matched reasoning prediction"
                )

            else:

                mismatches.append(
                    "Execution output did not match reasoning prediction"
                )

        # ------------------------------------------------------
        # Plan execution
        # ------------------------------------------------------

        has_plan = bool(
            plan.get("steps")
            or plan.get("tasks")
        )

        if has_plan:

            if success:

                insights.append(
                    "Plan executed successfully"
                )

            else:

                mismatches.append(
                    "Plan execution failed"
                )

        return {
            "insights": insights,
            "mismatches": mismatches,
        }

    # ==========================================================
    # ReflectionComponent API
    # ==========================================================

    def process(
        self,
        data: dict[str, Any] | None,
    ) -> dict[str, Any]:

        if not isinstance(data, dict):
            data = {}

        return self.analyze(
            reasoning=(
                data.get("reasoning")
                or data.get("reasoning_trace")
            ),
            plan=data.get("plan"),
            execution_result=data.get("execution_result"),
        )

    # ==========================================================
    # Runtime API
    # ==========================================================

    def reset(self) -> None:
        pass

    def status(self) -> dict[str, Any]:

        return {
            "component": "Analyzer",
            "state": "ready",
        }

    # ==========================================================
    # Python Protocol
    # ==========================================================

    def __repr__(self) -> str:

        return "Analyzer(state=ready)"