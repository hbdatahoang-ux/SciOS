"""
SciOS Task Graph
================

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
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List

from .task import Task


class TaskGraph:
    """
    Directed Acyclic Graph of planning tasks.

    TaskGraph is a structural planning component. It does not
    execute tasks or track runtime lifecycle state.
    """

    def __init__(self) -> None:
        self.tasks: Dict[str, Task] = {}
        self.edges: Dict[str, List[str]] = {}


    # ======================================================
    # Task Management
    # ======================================================

    def add_task(
        self,
        task_id: str,
        task: Task,
    ) -> None:
        """
        Register a task in the graph.
        """

        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

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

        self.tasks[task_id] = task
        self.edges[task_id] = []


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

        Both tasks must already be registered in the graph.
        """

        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

        if not isinstance(depends_on, str):
            raise TypeError(
                "depends_on must be a string"
            )

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
            self.edges[task_id].append(
                depends_on
            )

        self.tasks[task_id].add_dependency(
            depends_on
        )


    # ======================================================
    # Query
    # ======================================================

    def get_task(
        self,
        task_id: str,
    ) -> Task | None:
        """
        Return a registered task by identifier.
        """

        return self.tasks.get(task_id)


    def get_dependencies(
        self,
        task_id: str,
    ) -> List[str]:
        """
        Return registered dependencies for a task.

        Unknown task identifiers return an empty list for
        compatibility with the existing query API.
        """

        return list(
            self.edges.get(
                task_id,
                [],
            )
        )


    def has_task(
        self,
        task_id: str,
    ) -> bool:
        """
        Check whether a task is registered.
        """

        return task_id in self.tasks


    def clear(self) -> None:
        """
        Remove all tasks and dependency edges.
        """

        self.tasks.clear()
        self.edges.clear()


    # ======================================================
    # Compatibility API
    # ======================================================

    @property
    def graph(self) -> Dict[str, dict]:
        """
        Compatibility graph view.

        Example
        -------

        {
            "task1": {
                "task": Task,
                "dependencies": []
            }
        }
        """

        return {
            task_id: {
                "task": task,
                "dependencies": list(
                    self.edges.get(
                        task_id,
                        [],
                    )
                ),
            }
            for task_id, task in self.tasks.items()
        }


    # ======================================================
    # Topological Sort
    # ======================================================

    def topological_sort(self) -> List[str]:
        """
        Return tasks in dependency order.

        Dependencies are emitted before the tasks that depend
        on them.

        Raises
        ------
        ValueError
            If the graph contains a dependency cycle.
        """

        indegree = {
            task_id: len(
                self.edges.get(
                    task_id,
                    [],
                )
            )
            for task_id in self.tasks
        }

        reverse: Dict[str, List[str]] = {
            task_id: []
            for task_id in self.tasks
        }

        for task_id, dependencies in self.edges.items():
            for dependency in dependencies:
                if dependency not in self.tasks:
                    raise ValueError(
                        f"Unknown dependency: '{dependency}'"
                    )

                reverse[dependency].append(
                    task_id
                )

        queue = deque(
            task_id
            for task_id, degree in indegree.items()
            if degree == 0
        )

        order: List[str] = []

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
            f"(tasks={len(self.tasks)}, "
            f"edges={sum(len(v) for v in self.edges.values())})"
        )
