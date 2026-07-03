"""
SciOS Planner
=============

High-level planning engine for the SciOS cognitive runtime.

Responsibilities
----------------
- Accept planning goals
- Build execution plans
- Produce task graphs
- Maintain planning history
"""

from __future__ import annotations

from typing import Any

from .goal import Goal, GoalStatus
from .task_graph import TaskGraph

__all__ = [
    "Planner",
]


class Planner:
    """
    High-level planning engine.

    Planner converts high-level goals into executable task
    graphs. It is intentionally lightweight—the actual
    reasoning strategy belongs to the Reasoning subsystem.
    """

    def __init__(self) -> None:

        self._history: list[Goal] = []

    # ======================================================
    # Public API
    # ======================================================

    def plan(
        self,
        goal: Goal,
    ) -> TaskGraph:
        """
        Build an execution plan.
        """

        goal.ready()

        graph = TaskGraph()

        graph.add_task(
            name="reason",
            payload={
                "goal": goal.description,
            },
        )

        self._history.append(goal)

        return graph

    def execute(
        self,
        goal: Goal,
    ) -> TaskGraph:
        """
        Alias of plan().
        """

        return self.plan(goal)

    # ======================================================
    # Queries
    # ======================================================

    @property
    def history(self) -> list[Goal]:
        """
        Planning history.
        """

        return list(self._history)

    def clear(self) -> None:
        """
        Clear planning history.
        """

        self._history.clear()

    # ======================================================
    # Status
    # ======================================================

    def status(self) -> dict[str, Any]:

        completed = sum(
            1
            for g in self._history
            if g.status is GoalStatus.COMPLETED
        )

        failed = sum(
            1
            for g in self._history
            if g.status is GoalStatus.FAILED
        )

        return {

            "goals": len(self._history),

            "completed": completed,

            "failed": failed,
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:

        return len(self._history)

    def __repr__(self) -> str:

        return (
            "Planner("
            f"goals={len(self._history)})"
        )