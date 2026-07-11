"""
SciOS Planner Execution
=======================

Execution engine for planner.

Responsibilities
----------------
- Execute tasks from a plan
- Manage execution lifecycle
- Validate execution result
- Provide execution report
"""

from __future__ import annotations

from typing import Any

from .goal import Goal
from .task import Task


__all__ = [
    "PlannerExecution",
    "ExecutionState",
]


# ==========================================================
# Execution State
# ==========================================================


class ExecutionState:
    """
    Execution lifecycle state machine.
    """

    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


    def __init__(self) -> None:

        self._state = self.INITIALIZED


    def set_state(
        self,
        state: str,
    ) -> None:

        self._state = state


    def get_state(self) -> str:

        return self._state


    def reset(self) -> None:

        self._state = self.INITIALIZED


    def is_terminal(self) -> bool:

        return self._state in (
            self.COMPLETED,
            self.FAILED,
        )


    def __repr__(self) -> str:

        return (
            f"ExecutionState("
            f"{self._state})"
        )


# ==========================================================
# Planner Execution
# ==========================================================


class PlannerExecution:
    """
    High-level planner execution orchestrator.
    """


    def __init__(self) -> None:

        self.state = ExecutionState()

        self.goal: Goal | None = None

        self.tasks: list[Task] = []

        self.result: dict[str, Any] | None = None



    # ======================================================
    # Run
    # ======================================================


    def run(
        self,
        goal: Goal,
        tasks: list[Task],
    ) -> dict[str, Any]:

        self.goal = goal

        self.tasks = list(tasks)

        self.state.set_state(
            ExecutionState.RUNNING
        )


        # -------------------------------
        # Validation
        # -------------------------------

        if not self.tasks:

            self.result = {
                "valid": False,
                "errors": [
                    "No tasks provided."
                ],
            }

            self.state.set_state(
                ExecutionState.FAILED
            )

            return self.result



        errors: list[str] = []


        # -------------------------------
        # Execute tasks
        # -------------------------------

        for task in self.tasks:

            if not isinstance(task, Task):

                errors.append(
                    f"Invalid task: {task}"
                )

                continue


            try:

                task.mark_completed()


            except Exception as exc:

                errors.append(
                    str(exc)
                )



        valid = (
            len(errors) == 0
        )


        self.result = {
            "valid": valid,
            "errors": errors,
        }


        self.state.set_state(
            ExecutionState.COMPLETED
            if valid
            else ExecutionState.FAILED
        )


        return self.result



    # Compatibility alias

    execute = run



    # ======================================================
    # Status
    # ======================================================


    def status(self) -> dict[str, Any]:

        return {

            "state":
                self.state.get_state(),


            "goal":
                (
                    self.goal.description
                    if self.goal
                    else None
                ),


            "tasks":
                [
                    task.description
                    for task in self.tasks
                ],


            "result":
                self.result,
        }



    # ======================================================
    # Reset
    # ======================================================


    def reset(self) -> None:

        self.state.reset()

        self.goal = None

        self.tasks = []

        self.result = None



    # ======================================================
    # Helpers
    # ======================================================


    def last_result(
        self,
    ) -> dict[str, Any] | None:

        return self.result



    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(state="
            f"{self.state.get_state()}, "
            f"tasks={len(self.tasks)})"
        )