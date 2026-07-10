"""
SciOS Task Graph
================

Directed Acyclic Graph (DAG) representation for planning.

Responsibilities
----------------
- Represent executable tasks
- Track task dependencies
- Support topological execution order
- Provide serialization utilities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Task",
    "TaskGraph",
]


# ==========================================================
# Task
# ==========================================================

@dataclass(slots=True)
class Task:
    """
    Executable planning task.
    """

    name: str

    payload: dict[str, Any] = field(default_factory=dict)

    dependencies: set[str] = field(default_factory=set)

    metadata: dict[str, Any] = field(default_factory=dict)

    completed: bool = False

    def to_dict(self) -> dict[str, Any]:

        return {

            "name": self.name,

            "payload": self.payload,

            "dependencies": sorted(self.dependencies),

            "metadata": self.metadata,

            "completed": self.completed,
        }


# ==========================================================
# Task Graph
# ==========================================================

class TaskGraph:
    """
    Directed Acyclic Graph of executable tasks.
    """

    def __init__(self) -> None:

        self._tasks: dict[str, Task] = {}

    # ======================================================
    # Task Management
    # ======================================================

    def add_task(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
    ) -> Task:
        """
        Add a task to the graph.
        """

        if name in self._tasks:
            raise ValueError(
                f"Task '{name}' already exists."
            )

        task = Task(
            name=name,
            payload=payload or {},
        )

        self._tasks[name] = task

        return task

    def add_dependency(
        self,
        task: str,
        depends_on: str,
    ) -> None:
        """
        Add dependency between tasks.
        """

        if task not in self._tasks:
            raise KeyError(task)

        if depends_on not in self._tasks:
            raise KeyError(depends_on)

        self._tasks[task].dependencies.add(depends_on)

    # ======================================================
    # Queries
    # ======================================================

    def get(
        self,
        name: str,
    ) -> Task | None:

        return self._tasks.get(name)

    def ready_tasks(self) -> list[Task]:
        """
        Return tasks whose dependencies are satisfied.
        """

        ready = []

        for task in self._tasks.values():

            if task.completed:
                continue

            if all(
                self._tasks[d].completed
                for d in task.dependencies
            ):
                ready.append(task)

        return ready

    def mark_completed(
        self,
        name: str,
    ) -> None:
        """
        Mark task as completed.
        """

        self._tasks[name].completed = True

    # ======================================================
    # Graph State
    # ======================================================

    @property
    def completed(self) -> bool:
        """
        Whether all tasks are completed.
        """

        return all(
            t.completed
            for t in self._tasks.values()
        )

    def status(self) -> dict[str, Any]:

        return {

            "tasks": len(self._tasks),

            "completed": sum(
                t.completed
                for t in self._tasks.values()
            ),

            "ready": len(
                self.ready_tasks()
            ),
        }

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        return {

            "tasks": {

                name: task.to_dict()

                for name, task in self._tasks.items()

            }

        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:

        return len(self._tasks)

    def __iter__(self):

        return iter(self._tasks.values())

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._tasks

    def __repr__(self) -> str:

        return (
            "TaskGraph("
            f"tasks={len(self)}, "
            f"completed={self.completed})"
        )
