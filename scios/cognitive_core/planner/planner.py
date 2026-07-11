"""
SciOS Planner
=============

High-level planner orchestrator.
"""

from __future__ import annotations

from typing import Any, Iterable

from .goal import Goal
from .plan import Plan
from .task import Task
from .planner_execution import PlannerExecution
from .monitor import ProgressMonitor
from .recovery import FailureRecovery


__all__ = [
    "Planner",
]


class PlannerState:
    """
    Planner lifecycle state.
    """

    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    def __init__(self) -> None:
        self._state = self.INITIALIZED

    def set_state(self, state: str) -> None:
        self._state = state

    def get_state(self) -> str:
        return self._state

    def is_terminal(self) -> bool:
        return self._state in (
            self.COMPLETED,
            self.FAILED,
        )

    def reset(self) -> None:
        self._state = self.INITIALIZED


class Planner:
    """
    Planner orchestrator.
    """

    def __init__(self) -> None:

        self.state = PlannerState()

        self.execution = PlannerExecution()

        self.monitor = ProgressMonitor()

        self.recovery = FailureRecovery()

        self.current_plan: Plan | None = None

        self.history: list[Plan] = []


    # ======================================================
    # Plan Construction
    # ======================================================

    def create_plan(
        self,
        goal: Goal,
        tasks: Iterable[str | Task] | None = None,
    ) -> Plan:
        """
        Create a plan.

        Strings are automatically converted into Task objects.
        """

        normalized: list[Task] = []

        if tasks:
            for item in tasks:
                if isinstance(item, Task):
                    normalized.append(item)
                else:
                    normalized.append(
                        Task(description=str(item))
                    )

        plan = Plan(
            goal=goal,
            tasks=normalized,
        )

        self.current_plan = plan

        self.history.append(plan)

        return plan


    # ======================================================
    # Execution
    # ======================================================

    def run(
        self,
        plan: Plan | None = None,
    ) -> dict[str, Any]:

        plan = plan or self.current_plan

        if plan is None:
            raise ValueError("No plan available.")

        self.state.set_state(
            PlannerState.RUNNING
        )

        try:

            result = self.execution.run(
                plan.goal,
                plan.tasks,
            )

            if result["valid"]:

                for task in plan.tasks:
                    task.mark_completed()

                plan.metadata["status"] = "completed"

                self.state.set_state(
                    PlannerState.COMPLETED
                )

            else:

                plan.metadata["status"] = "failed"

                self.state.set_state(
                    PlannerState.FAILED
                )

            return result

        except Exception as exc:

            self.recovery.handle_failure(
                plan,
                exc,
            )

            self.state.set_state(
                PlannerState.FAILED
            )

            return {
                "valid": False,
                "errors": [str(exc)],
            }


    # Backward-compatible alias
    execute = run


    # ======================================================
    # Status
    # ======================================================

    def status(self) -> dict[str, Any]:

        if self.current_plan is None:

            return {
                "state": self.state.get_state(),
                "goal": None,
                "tasks": [],
            }

        return {
            "state": self.state.get_state(),
            "goal": self.current_plan.goal.description,
            "tasks": [
                task.description
                for task in self.current_plan.tasks
            ],
            "progress": self.monitor.status(
                self.current_plan
            ),
        }


    # ======================================================
    # Utilities
    # ======================================================

    def reset(self) -> None:

        self.current_plan = None

        self.history.clear()

        self.state.reset()

        self.execution = PlannerExecution()


    def last_plan(self) -> Plan | None:

        if not self.history:
            return None

        return self.history[-1]


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(state={self.state.get_state()}, "
            f"plans={len(self.history)})"
        )