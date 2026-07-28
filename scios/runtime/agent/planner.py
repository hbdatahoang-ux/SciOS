"""
SciOS Runtime Agent Planner
===========================

Task planning component.

Python 3.11+
"""

from __future__ import annotations


__all__ = [
    "Planner",
]


class Planner:
    """
    Creates execution plans.
    """

    def create_plan(
        self,
        goal: str,
    ) -> list[str]:
        """
        Public API expected by Agent.
        """
        return self.plan(goal)

    def plan(
        self,
        goal: str,
    ) -> list[str]:

        return [
            goal
        ]

    def reset(
        self,
    ) -> None:

        pass

    def __repr__(
        self,
    ) -> str:

        return "Planner()"