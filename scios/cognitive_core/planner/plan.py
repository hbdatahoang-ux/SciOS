"""
SciOS Planner Plan
==================

Canonical plan representation for the SciOS Cognitive Core.

Responsibilities
----------------
- Hold planning goal.
- Manage planning tasks.
- Maintain dependency graph.
- Track planning constraints.
- Provide execution summary.
"""

from __future__ import annotations

from typing import Any

from .constraint import ConstraintSet
from .goal import Goal
from .task import Task
from .task_graph import TaskGraph


__all__ = [
    "Plan",
]


class Plan:
    """
    Canonical planning object.
    """

    def __init__(
        self,
        goal: Goal,
        tasks: list[Task] | None = None,
        task_graph: TaskGraph | None = None,
        constraints: ConstraintSet | None = None,
    ) -> None:

        self.goal = goal

        self.tasks = tasks or []

        self.task_graph = task_graph or TaskGraph()

        self.constraints = (
            constraints
            or ConstraintSet()
        )

        self.metadata: dict[str, Any] = {
            "status": "created",
        }

    # ======================================================
    # Tasks
    # ======================================================

    def add_task(
        self,
        task: Task,
        task_id: str,
    ) -> None:
        """
        Add task to the plan.
        """

        self.tasks.append(task)

        self.task_graph.add_task(
            task_id,
            task,
        )

    # ======================================================
    # Status
    # ======================================================

    def is_completed(self) -> bool:
        """
        Whether every task has completed.
        """

        return all(
            task.is_completed()
            for task in self.tasks
        )

    # ======================================================
    # Summary
    # ======================================================

    def summary(self) -> dict[str, Any]:
        """
        Return plan summary.
        """

        completed = sum(
            1
            for task in self.tasks
            if task.is_completed()
        )

        return {

            "goal": self.goal.description,

            "tasks_total": len(self.tasks),

            "tasks_completed": completed,

            "status": self.metadata.get(
                "status",
                "unknown",
            ),
        }

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            "Plan("
            f"goal={self.goal.description!r}, "
            f"tasks={len(self.tasks)}, "
            f"status={self.metadata.get('status', 'unknown')!r}"
            ")"
        )