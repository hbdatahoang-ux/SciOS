"""
SciOS Cognitive Core Planning Policy
=====================================

Dependency-aware policy ordering for cognitive plans.
"""

from __future__ import annotations

from typing import Iterable

from .task import Task


__all__ = [
    "PlanningPolicy",
]


class PlanningPolicy:
    """
    Planning policy.

    Tasks are ordered by priority while preserving dependency
    constraints.

    A task can only appear after all of its declared dependencies.
    """

    def __init__(
        self,
        rules: dict | None = None,
    ) -> None:
        self.rules = dict(rules) if rules else {}

    def apply(
        self,
        tasks: Iterable[Task],
    ) -> list[Task]:
        """
        Return a dependency-safe priority ordering.

        Higher-priority tasks are preferred among tasks whose
        dependencies are already satisfied.

        Every declared dependency must refer to another task in the
        supplied collection. Unresolved dependencies are rejected
        rather than silently ignored.
        """

        pending = list(tasks)

        if not all(isinstance(task, Task) for task in pending):
            raise TypeError(
                "tasks must contain only Task instances"
            )

        task_by_id = {
            task.id: task
            for task in pending
            if task.id is not None
        }

        for task in pending:
            for dependency in task.dependencies:
                if dependency not in task_by_id:
                    raise ValueError(
                        f"Unresolved dependency {dependency!r} "
                        f"for task {task.id!r}"
                    )

        remaining = list(pending)
        ordered: list[Task] = []
        completed_ids: set[str] = set()

        while remaining:
            ready: list[Task] = []

            for task in remaining:
                if all(
                    dependency in completed_ids
                    for dependency in task.dependencies
                ):
                    ready.append(task)

            if not ready:
                raise ValueError(
                    "Cannot produce dependency-safe ordering; "
                    "the task dependency graph contains a cycle."
                )

            ready.sort(
                key=lambda task: task.constraints.get(
                    "priority",
                    0,
                ),
                reverse=True,
            )

            for task in ready:
                ordered.append(task)
                remaining.remove(task)

                if task.id is not None:
                    completed_ids.add(task.id)

        return ordered
