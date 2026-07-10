# scios/cognitive_core/reflection/adaptive.py

"""
SciOS Reflection Adaptive Policy
================================

AdaptivePolicy applies improvement suggestions to adjust
system behavior dynamically. It connects Reflection back
to Planner, Reasoner, and Memory for self-optimization.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .base import ReflectionComponent


class AdaptivePolicy(ReflectionComponent):
    """
    AdaptivePolicy interprets improvement suggestions and
    decides whether to adjust Planner, Reasoner, or Memory.
    """

    def __init__(self) -> None:
        super().__init__("AdaptivePolicy")

    def apply(self, improvements: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Apply improvement suggestions to adaptive policies.
        """
        actions: List[str] = []

        # Execution improvements → adjust execution strategy
        if improvements.get("execution"):
            actions.append("Adjust execution strategy")

        # Planning improvements → refine planner heuristics
        if improvements.get("planning"):
            actions.append("Refine planner heuristics")

        # Reasoning improvements → strengthen reasoning safeguards
        if improvements.get("reasoning"):
            actions.append("Strengthen reasoning safeguards")

        # If no improvements, maintain current policy
        if not actions:
            actions.append("Maintain current strategy")

        policy_update = {
            "applied_actions": actions,
            "improvements": improvements,
        }

        return policy_update

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard interface: wraps apply().
        Expects key: improvements.
        """
        return self.apply(data.get("improvements", {}))
