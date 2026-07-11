"""
SciOS Planner Context
=====================

Execution context for the Cognitive Planner.

Responsibilities
----------------
- Store current goal.
- Store current execution plan.
- Maintain planner tasks.
- Record planner logs.
- Store arbitrary metadata.
"""

from __future__ import annotations

from typing import Any

from .goal import Goal
from .plan import Plan
from .task import Task

__all__ = [
    "Context",
]


class Context:
    """
    Planner execution context.
    """

    def __init__(self) -> None:

        self.current_goal: Goal | None = None

        self.current_plan: Plan | None = None

        self.tasks: list[Task] = []

        self.metadata: dict[str, Any] = {}

        self.log: list[str] = []

    # ======================================================
    # Goal / Plan
    # ======================================================

    def set_goal(
        self,
        goal: Goal,
    ) -> None:

        self.current_goal = goal

    def set_plan(
        self,
        plan: Plan,
    ) -> None:

        self.current_plan = plan

        # Keep task list synchronized.
        self.tasks = list(plan.tasks)

    # ======================================================
    # Tasks
    # ======================================================

    def add_task(
        self,
        task: Task,
    ) -> None:

        self.tasks.append(task)

        if self.current_plan is not None:
            self.current_plan.tasks.append(task)

    # ======================================================
    # Logging
    # ======================================================

    def add_log(
        self,
        message: str,
    ) -> None:

        self.log.append(message)

    # ======================================================
    # Metadata
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(key, default)

    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(self) -> None:

        self.current_goal = None

        self.current_plan = None

        self.tasks.clear()

        self.metadata.clear()

        self.log.clear()

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        goal = None

        if self.current_goal is not None:
            goal = {
                "description": self.current_goal.description,
            }

        plan = None

        if self.current_plan is not None:

            plan = {
                "goal": {
                    "description": self.current_plan.goal.description,
                },
                "tasks": [
                    {
                        "description": task.description,
                    }
                    for task in self.current_plan.tasks
                ],
                "status": self.current_plan.metadata.get(
                    "status",
                    "unknown",
                ),
            }

        return {
            "goal": goal,
            "plan": plan,
            "metadata": dict(self.metadata),
            "log": list(self.log),
        }

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"goal={self.current_goal!r}, "
            f"tasks={len(self.tasks)})"
        )