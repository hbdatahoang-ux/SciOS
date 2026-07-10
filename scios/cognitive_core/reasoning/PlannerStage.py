"""
SciOS Planner Stage
===================

Pipeline stage for reasoning plan generation.
"""

from __future__ import annotations
from typing import Any, Dict
from .planner import ReasoningPlanner


class PlannerStage:
    """
    PlannerStage = Pipeline stage that generates a reasoning plan
    for a given query and context.
    """

    def __init__(self) -> None:
        self._planner = ReasoningPlanner()

    def run(self, query: str, context: dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Execute the planner stage.
        """
        context = context or {}
        plan = self._planner.create_plan(query=query, context=context)
        return {
            "stage": "PlannerStage",
            "query": query,
            "plan": plan,
        }

    def reset(self) -> None:
        """
        Reset planner state.
        """
        self._planner.reset()

    def status(self) -> Dict[str, Any]:
        """
        Return planner stage status.
        """
        return {
            "stage": "PlannerStage",
            "planner": self._planner.status(),
        }

    def __repr__(self) -> str:
        return f"PlannerStage(plans={self._planner.status()['plans_generated']})"
