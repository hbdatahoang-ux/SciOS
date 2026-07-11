"""
SciOS Planner Failure Recovery
==============================

Failure handling and recovery strategies
for Cognitive Planner.

Responsibilities:
- Detect planning failures.
- Record recovery events.
- Retry failed tasks.
- Generate fallback plans.
"""

from __future__ import annotations

from typing import Any

from .plan import Plan
from .task import Task


__all__ = [
    "FailureRecovery",
]


class FailureRecovery:
    """
    Recovery controller for failed plans.
    """

    def __init__(self) -> None:

        self.recovery_log: list[str] = []


    # ======================================================
    # Failure Handling
    # ======================================================

    def handle_failure(
        self,
        plan: Plan | None,
        error: Exception,
    ) -> None:
        """
        Handle execution failure.
        """

        message = (
            f"Failure detected: {error}"
        )

        self.recovery_log.append(
            message
        )


        if plan is not None:

            plan.metadata["status"] = "failed"

            plan.metadata["error"] = str(
                error
            )


    # ======================================================
    # Retry
    # ======================================================

    def retry_task(
        self,
        task: Task,
    ) -> bool:
        """
        Retry a failed task.

        Current implementation:
        simulate successful recovery.
        """

        self.recovery_log.append(
            f"Retrying task: {task.description}"
        )


        try:

            task.mark_completed()

            return True


        except Exception as exc:

            self.recovery_log.append(
                f"Retry failed: {exc}"
            )

            return False



    # ======================================================
    # Fallback
    # ======================================================

    def fallback_plan(
        self,
        plan: Plan,
    ) -> Plan:
        """
        Create fallback plan.

        Current behavior:
        clone plan metadata and mark fallback state.
        """

        fallback = Plan(
            goal=plan.goal,
            tasks=list(plan.tasks),
            task_graph=plan.task_graph,
            constraints=plan.constraints,
        )


        fallback.metadata.update(
            plan.metadata
        )


        fallback.metadata["status"] = (
            "fallback"
        )


        self.recovery_log.append(
            "Fallback plan created"
        )


        return fallback



    # ======================================================
    # Diagnostics
    # ======================================================

    def clear_log(self) -> None:
        """
        Clear recovery history.
        """

        self.recovery_log.clear()


    def report(self) -> dict[str, Any]:
        """
        Return recovery report.
        """

        return {
            "events": list(
                self.recovery_log
            ),
            "count": len(
                self.recovery_log
            ),
        }


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(events={len(self.recovery_log)})"
        )