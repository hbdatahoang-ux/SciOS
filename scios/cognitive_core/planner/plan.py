"""
SciOS Planner Plan
==================

Canonical structural plan representation for the SciOS Cognitive Core.

Responsibilities
----------------
- Hold a planning goal.
- Hold planning tasks.
- Maintain the task dependency graph.
- Hold planning constraints.
- Preserve structural planning metadata.

Non-responsibilities
--------------------
- Runtime execution.
- Execution lifecycle.
- Progress tracking.
- Success/failure tracking.
- Runtime tool invocation.
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
    Canonical cognitive planning representation.

    A Plan describes what should be done and how planned tasks
    depend on one another.

    It is intentionally execution-agnostic.
    """

    def __init__(
        self,
        goal: Goal,
        tasks: list[Task] | None = None,
        task_graph: TaskGraph | None = None,
        constraints: ConstraintSet | None = None,
    ) -> None:
        if not isinstance(goal, Goal):
            raise TypeError("goal must be an instance of Goal")

        if tasks is not None and not isinstance(tasks, list):
            raise TypeError("tasks must be a list")

        if task_graph is not None and not isinstance(
            task_graph,
            TaskGraph,
        ):
            raise TypeError(
                "task_graph must be an instance of TaskGraph"
            )

        if constraints is not None and not isinstance(
            constraints,
            ConstraintSet,
        ):
            raise TypeError(
                "constraints must be an instance of ConstraintSet"
            )

        self.goal = goal

        self.tasks: list[Task] = []

        self.task_graph = (
            task_graph
            if task_graph is not None
            else TaskGraph()
        )

        self.constraints = (
            constraints
            if constraints is not None
            else ConstraintSet()
        )

        self.metadata: dict[str, Any] = {}

        if tasks is not None:
            for task in tasks:
                self.add_task(task)


    # ======================================================
    # Task Management
    # ======================================================

    def _allocate_task_id(self) -> str:
        """
        Allocate a deterministic local task identifier.

        Explicit Task.id values are always preferred. Automatically
        generated identifiers are only used for tasks that do not
        already have an identity.
        """

        index = len(self.tasks)

        while True:
            task_id = f"task-{index}"

            if self.task_graph.get_task(task_id) is None:
                return task_id

            index += 1


    def add_task(
        self,
        task: Task,
        task_id: str | None = None,
    ) -> None:
        """
        Add a task to the plan and register it in the dependency graph.

        If task_id is omitted:
        - preserve task.id when present;
        - otherwise allocate a deterministic local identifier.
        """

        if not isinstance(task, Task):
            raise TypeError(
                "task must be an instance of Task"
            )

        if task_id is not None:
            if not isinstance(task_id, str):
                raise TypeError(
                    "task_id must be a string or None"
                )

            resolved_id = task_id

        elif task.id is not None:
            resolved_id = task.id

        else:
            resolved_id = self._allocate_task_id()

        if task.id is None:
            task.id = resolved_id

        elif task.id != resolved_id:
            raise ValueError(
                "task_id does not match task.id"
            )

        if task in self.tasks:
            return

        self.task_graph.add_task(
            resolved_id,
            task,
        )

        for dependency in task.dependencies:
            self.task_graph.add_dependency(
                resolved_id,
                dependency,
            )

        self.tasks.append(task)


    def get_task(
        self,
        task_id: str,
    ) -> Task | None:
        """
        Retrieve a planned task by identifier.
        """

        return self.task_graph.get_task(task_id)


    # ======================================================
    # Structural Metadata
    # ======================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store planning metadata.
        """

        if not isinstance(key, str):
            raise TypeError(
                "metadata key must be a string"
            )

        self.metadata[key] = value


    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve planning metadata.
        """

        return self.metadata.get(
            key,
            default,
        )


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the structural planning representation.

        Runtime execution state is intentionally absent.
        """

        return {
            "goal": self.goal.to_dict(),
            "tasks": [
                task.to_dict()
                for task in self.tasks
            ],
            "constraints": self.constraints.to_dict(),
            "metadata": dict(self.metadata),
        }


    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"Plan("
            f"goal={self.goal.description!r}, "
            f"tasks={len(self.tasks)}"
            ")"
        )
