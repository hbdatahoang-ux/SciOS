"""
SciOS Cognitive Core Planning Objective
========================================

Structural sub-goal representation for cognitive planning.

An Objective groups planning tasks under a sub-goal. It contains no
execution lifecycle or execution state.
"""

from __future__ import annotations

from typing import Any

from .task import Task


__all__ = [
    "Objective",
]


class Objective:
    """
    Structural sub-goal used during cognitive planning.

    An Objective groups Tasks that contribute to a sub-goal. It is a
    planning-domain object and does not track execution state.
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
        self.constraints = dict(constraints) if constraints else {}
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a planning task to this objective."""

        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")

        self.tasks.append(task)

    def __repr__(self) -> str:
        return (
            f"<Objective "
            f"desc={self.description!r} "
            f"tasks={len(self.tasks)}>"
        )
