"""
SciOS Planner Progress Monitor
==============================

Monitor execution progress of a Plan.
"""

from __future__ import annotations

from typing import Any

from .plan import Plan


__all__ = [
    "ProgressMonitor",
]


class ProgressMonitor:
    """
    Monitor planning progress.
    """

    def __init__(self) -> None:

        self.history: list[dict[str, Any]] = []

    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
        plan: Plan,
    ) -> dict[str, Any]:
        """
        Return current plan status.
        """

        if plan is None or not plan.tasks:

            return {
                "progress": 0.0,
                "completed": 0,
                "total": 0,
                "status": "empty",
            }

        completed = sum(
            1
            for task in plan.tasks
            if task.is_completed()
        )

        total = len(plan.tasks)

        progress = (
            completed / total
            if total
            else 0.0
        )

        report = {
            "progress": round(progress * 100, 2),
            "completed": completed,
            "total": total,
            "status": (
                "completed"
                if completed == total
                else "running"
            ),
        }

        self.history.append(report.copy())

        return report

    # ======================================================
    # Helpers
    # ======================================================

    def reset(self) -> None:
        """
        Clear monitoring history.
        """

        self.history.clear()

    def snapshot(self) -> list[dict[str, Any]]:
        """
        Return monitoring history.
        """

        return list(self.history)

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(history={len(self.history)})"
        )