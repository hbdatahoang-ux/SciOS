"""
SciOS Cognitive Core - Task Graph
=================================

Directed Acyclic Graph (DAG) representation for cognitive planning tasks.

Responsibilities
----------------
- Register planning tasks.
- Manage task dependencies.
- Preserve graph consistency.
- Provide dependency queries.
- Provide topological ordering.
- Detect dependency cycles.

Invariants
----------
- Every graph node is a registered Task.
- Every dependency references a registered Task.
- Self-dependencies are forbidden.
- Unknown dependencies are rejected.
- The graph contains no phantom nodes.
- Task dependencies and graph edges remain synchronized.

Non-responsibilities
--------------------
- Runtime execution.
- Runtime scheduling.
- Execution lifecycle.
- Retry or recovery.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from .task import Task

__all__ = ["TaskGraph"]


class TaskGraph:
    """
    Directed Acyclic Graph of cognitive planning tasks.

    Edge representation:

        edges[task_id] = [dependency_id, ...]

    Therefore:

        B depends on A

    is represented as:

        edges["B"] = ["A"]

    TaskGraph owns topology. Task itself only stores structural
    dependency identifiers.
    """

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.edges: dict[str, list[str]] = {}

    # ======================================================
    # Task Management
    # ======================================================

    def add_task(
        self,
        task_id: str,
        task: Task,
    ) -> None:
        """
        Register a Task in the graph.

        A Task may already contain dependency identifiers. Those
        dependencies must already be registered in the graph.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        if not isinstance(task, Task):
            raise TypeError(
                "task must be an instance of Task"
            )

        if task_id in self.tasks:
            raise ValueError(
                f"Task '{task_id}' is already registered."
            )

        if task.id is not None and task.id != task_id:
            raise ValueError(
                "task_id does not match task.id"
            )

        if task.id is None:
            task.id = task_id

        # Validate all pre-existing dependencies before mutating
        # the graph. This preserves graph atomicity on failure.
        for dependency in task.dependencies:
            if dependency == task_id:
                raise ValueError(
                    f"Task '{task_id}' cannot depend on itself."
                )

            if dependency not in self.tasks:
                raise ValueError(
                    f"Unknown dependency: '{dependency}'"
                )

        self.tasks[task_id] = task
        self.edges[task_id] = list(task.dependencies)

    # ======================================================
    # Dependency Management
    # ======================================================

    def add_dependency(
        self,
        task_id: str,
        depends_on: str,
    ) -> None:
        """
        Add a dependency edge.

        ``task_id`` depends on ``depends_on``.

        Both tasks must already be registered.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        if not isinstance(depends_on, str):
            raise TypeError("depends_on must be a string")

        if task_id not in self.tasks:
            raise ValueError(
                f"Unknown task: '{task_id}'"
            )

        if depends_on not in self.tasks:
            raise ValueError(
                f"Unknown dependency: '{depends_on}'"
            )

        if task_id == depends_on:
            raise ValueError(
                f"Task '{task_id}' cannot depend on itself."
            )

        if depends_on not in self.edges[task_id]:
            self.edges[task_id].append(depends_on)

        self.tasks[task_id].add_dependency(depends_on)

    def remove_dependency(
        self,
        task_id: str,
        depends_on: str,
    ) -> None:
        """
        Remove a dependency edge if present.

        Both task identifiers must refer to registered tasks.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        if not isinstance(depends_on, str):
            raise TypeError("depends_on must be a string")

        if task_id not in self.tasks:
            raise ValueError(
                f"Unknown task: '{task_id}'"
            )

        if depends_on not in self.tasks:
            raise ValueError(
                f"Unknown dependency: '{depends_on}'"
            )

        if depends_on in self.edges[task_id]:
            self.edges[task_id].remove(depends_on)

        self.tasks[task_id].remove_dependency(depends_on)

    # ======================================================
    # Queries
    # ======================================================

    def get_task(
        self,
        task_id: str,
    ) -> Task | None:
        """Return a registered Task by identifier."""
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        return self.tasks.get(task_id)

    def get_dependencies(
        self,
        task_id: str,
    ) -> list[str]:
        """
        Return dependencies for a registered task.

        Unknown task identifiers return an empty list for
        compatibility with the existing query API.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        return list(self.edges.get(task_id, []))

    def has_task(
        self,
        task_id: str,
    ) -> bool:
        """Check whether a task is registered."""
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        return task_id in self.tasks

    def clear(self) -> None:
        """Remove all tasks and dependency edges."""
        self.tasks.clear()
        self.edges.clear()

    # ======================================================
    # Compatibility API
    # ======================================================

    @property
    def graph(self) -> dict[str, dict[str, Any]]:
        """
        Return the compatibility graph view.

        Example
        -------

        {
            "task1": {
                "task": Task,
                "dependencies": []
            }
        }

        The returned structure is a view/copy and does not expose
        the internal dependency lists directly.
        """
        return {
            task_id: {
                "task": task,
                "dependencies": list(
                    self.edges.get(task_id, [])
                ),
            }
            for task_id, task in self.tasks.items()
        }

    # ======================================================
    # Topological Sort
    # ======================================================

    def topological_sort(self) -> list[str]:
        """
        Return tasks in dependency order.

        Dependencies are emitted before the tasks that depend
        on them.

        Raises
        ------
        ValueError
            If the graph contains an unknown dependency or cycle.
        """
        indegree = {
            task_id: len(
                self.edges.get(task_id, [])
            )
            for task_id in self.tasks
        }

        reverse: dict[str, list[str]] = {
            task_id: []
            for task_id in self.tasks
        }

        for task_id, dependencies in self.edges.items():
            for dependency in dependencies:
                if dependency not in self.tasks:
                    raise ValueError(
                        f"Unknown dependency: '{dependency}'"
                    )

                reverse[dependency].append(task_id)

        queue = deque(
            task_id
            for task_id, degree in indegree.items()
            if degree == 0
        )

        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for dependent in reverse[node]:
                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(self.tasks):
            raise ValueError(
                "TaskGraph contains a dependency cycle."
            )

        return order

    # ======================================================
    # Structural Properties
    # ======================================================

    @property
    def task_count(self) -> int:
        """Return the number of registered tasks."""
        return len(self.tasks)

    @property
    def edge_count(self) -> int:
        """Return the number of dependency edges."""
        return sum(
            len(dependencies)
            for dependencies in self.edges.values()
        )

    # ======================================================
    # Representation
    # ======================================================

    def __len__(self) -> int:
        return len(self.tasks)

    def __contains__(
        self,
        task_id: str,
    ) -> bool:
        return task_id in self.tasks

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(tasks={self.task_count}, "
            f"edges={self.edge_count})"
        )