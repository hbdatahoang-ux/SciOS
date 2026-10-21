"""
SciOS Runtime Agent Decision Provider
=====================================

Runtime decision provider used by Agent.

``RuntimeDecisionProvider`` is the canonical semantic abstraction.
``Planner`` is retained as a public compatibility name.

Python 3.11+
"""

from __future__ import annotations

__all__ = [
    "RuntimeDecisionProvider",
    "Planner",
]


class RuntimeDecisionProvider:
    """
    Provide a runtime decision for an agent task.

    This is intentionally minimal. It does not create cognitive
    ``Plan`` objects and does not know about ``TaskGraph`` or
    ``ExecutionGraph``.

    The default provider preserves the historical runtime behavior:
    a goal is returned as a single-item list.
    """

    def create_plan(
        self,
        goal: str,
    ) -> list[str]:
        """
        Return the runtime decision for ``goal``.

        ``create_plan`` is retained as the compatibility-facing
        operation used by ``Agent``.
        """
        return self.plan(goal)

    def plan(
        self,
        goal: str,
    ) -> list[str]:
        """
        Produce the default runtime decision.
        """
        return [goal]

    def reset(self) -> None:
        """
        Reset provider state.

        The default provider is stateless.
        """
        pass

    def __repr__(self) -> str:
        """
        Preserve the historical public representation.
        """
        return "Planner()"


# Compatibility name.
Planner = RuntimeDecisionProvider