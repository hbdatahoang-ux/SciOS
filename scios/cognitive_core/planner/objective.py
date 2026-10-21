"""
SciOS Cognitive Core - Planning Objective
=========================================

Structural sub-goal representation for cognitive planning.

An Objective groups planning tasks under a sub-goal. It is purely a
planning-domain object and contains no execution lifecycle or runtime
state.
"""

from __future__ import annotations

from typing import Any

from .task import Task

__all__ = ["Objective"]


class Objective:
    """
    A structural sub-goal used during cognitive planning.

    An Objective:
        - describes a sub-goal,
        - optionally references its parent Goal,
        - carries planning constraints,
        - groups planning Tasks.

    It does not execute tasks and does not contain runtime state.
    """

    def __init__(
        self,
        description: str,
        parent_goal: str | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(description, str):
            raise TypeError("description must be a string")

        if parent_goal is not None and not isinstance(parent_goal, str):
            raise TypeError("parent_goal must be a string or None")

        if constraints is not None and not isinstance(constraints, dict):
            raise TypeError("constraints must be a dict or None")

        self.description = description
        self.parent_goal = parent_goal
        self.constraints: dict[str, Any] = (
            dict(constraints) if constraints is not None else {}
        )
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """
        Add a planning Task to this Objective.
        """
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")

        self.tasks.append(task)

    def __repr__(self) -> str:
        return (
            f"<Objective "
            f"desc={self.description!r} "
            f"tasks={len(self.tasks)}>"
        )