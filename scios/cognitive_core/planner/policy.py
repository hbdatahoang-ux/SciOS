"""
SciOS Cognitive Core Planning Policy
=====================================

Dependency-aware ordering for cognitive planning tasks.

This module orders Task objects only. It does not execute tasks,
schedule runtime work, or manage execution state.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .task import Task

__all__ = [
    "PlanningPolicy",
]


class PlanningPolicy:
    """
    Dependency-aware planning policy.

    Higher-priority tasks are selected first among tasks whose
    dependencies have already been ordered.

    Contract
    --------
    Task iterable -> dependency-safe ordered list[Task]

    Non-responsibilities
    --------------------
    - Runtime execution
    - Runtime scheduling
    - Task status management
    - Retry or recovery
    - ExecutionGraph construction
    """

    def __init__(
        self,
        rules: dict[str, Any] | None = None,
    ) -> None:
        if rules is not None and not isinstance(rules, dict):
            raise TypeError("rules must be a dictionary or None")

        self.rules: dict[str, Any] = (
            dict(rules) if rules is not None else {}
        )

    def apply(
        self,
        tasks: Iterable[Task],
    ) -> list[Task]:
        """
        Return a dependency-safe priority ordering.

        The input iterable is materialized once. The original iterable
        and Task objects are not mutated.

        Priority is read from the Task constraint named ``priority``.
        Higher values are preferred. Missing priority defaults to zero.

        Tasks with equal priority preserve their original input order.

        Raises
        ------
        TypeError
            If the input is not iterable or contains a non-Task value.
        ValueError
            If task IDs are duplicated, a dependency is unresolved,
            or the dependency graph contains a cycle.
        """
        pending = self._materialize_tasks(tasks)

        task_by_id = self._index_tasks(pending)
        self._validate_dependencies(pending, task_by_id)

        remaining = list(pending)
        ordered: list[Task] = []
        completed_ids: set[str] = set()

        while remaining:
            ready = [
                task
                for task in remaining
                if self._dependencies_satisfied(
                    task,
                    completed_ids,
                )
            ]

            if not ready:
                raise ValueError(
                    "Cannot produce dependency-safe ordering; "
                    "the task dependency graph contains a cycle."
                )

            ready.sort(
                key=self._priority,
                reverse=True,
            )

            for task in ready:
                ordered.append(task)
                remaining.remove(task)

                if task.id is not None:
                    completed_ids.add(task.id)

        return ordered

    @staticmethod
    def _materialize_tasks(
        tasks: Iterable[Task],
    ) -> list[Task]:
        """
        Materialize and validate the input task collection.
        """
        if isinstance(tasks, (str, bytes)):
            raise TypeError(
                "tasks must be an iterable of Task instances"
            )

        try:
            pending = list(tasks)
        except TypeError as exc:
            raise TypeError(
                "tasks must be an iterable of Task instances"
            ) from exc

        if not all(isinstance(task, Task) for task in pending):
            raise TypeError(
                "tasks must contain only Task instances"
            )

        return pending

    @staticmethod
    def _index_tasks(
        tasks: list[Task],
    ) -> dict[str, Task]:
        """
        Index tasks by ID and reject duplicate IDs.

        Tasks without IDs are allowed. They cannot be referenced by
        dependencies until an ID is assigned by the owning Plan.
        """
        task_by_id: dict[str, Task] = {}

        for task in tasks:
            if task.id is None:
                continue

            if task.id in task_by_id:
                raise ValueError(
                    f"Duplicate task ID: {task.id!r}"
                )

            task_by_id[task.id] = task

        return task_by_id

    @staticmethod
    def _validate_dependencies(
        tasks: list[Task],
        task_by_id: dict[str, Task],
    ) -> None:
        """
        Ensure every declared dependency resolves to a supplied Task.
        """
        for task in tasks:
            for dependency in task.dependencies:
                if dependency == task.id:
                    raise ValueError(
                        f"Task {task.id!r} cannot depend on itself"
                    )

                if dependency not in task_by_id:
                    raise ValueError(
                        f"Unresolved dependency {dependency!r} "
                        f"for task {task.id!r}"
                    )

    @staticmethod
    def _dependencies_satisfied(
        task: Task,
        completed_ids: set[str],
    ) -> bool:
        """
        Return whether all dependencies have already been ordered.
        """
        return all(
            dependency in completed_ids
            for dependency in task.dependencies
        )

    def _priority(self, task: Task) -> Any:
        """
        Return the task priority.

        A policy-level ``priority`` rule can provide a default.
        Task-level priority takes precedence.
        """
        default_priority = self.rules.get("priority", 0)

        priority = task.constraints.get(
            "priority",
            default_priority,
        )

        if not isinstance(priority, (int, float)):
            raise TypeError(
                f"Priority for task {task.id!r} must be numeric"
            )

        return priority

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"rules={self.rules!r}"
            ")"
        )