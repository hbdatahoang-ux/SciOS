"""
SciOS Task Graph
================

Directed Acyclic Graph (DAG) representation for planning tasks.

Responsibilities
----------------
- Store tasks
- Manage dependencies
- Topological sorting
- Cycle detection
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List

from .task import Task


class TaskGraph:
    """
    Directed Acyclic Graph of planning tasks.
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
        Add a task to graph.
        """

        self.tasks[task_id] = task
        self.edges.setdefault(
            task_id,
            [],
        )


    def add_dependency(
        self,
        task_id: str,
        depends_on: str,
    ) -> None:
        """
        task_id depends on depends_on.
        """

        self.edges.setdefault(
            task_id,
            [],
        )

        self.edges.setdefault(
            depends_on,
            [],
        )

        if depends_on not in self.edges[task_id]:
            self.edges[task_id].append(depends_on)

        if task_id in self.tasks:
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
        Return task by id.
        """

        return self.tasks.get(task_id)


    def get_dependencies(
        self,
        task_id: str,
    ) -> List[str]:
        """
        Return dependencies.
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

        return task_id in self.tasks


    def clear(self) -> None:

        self.tasks.clear()
        self.edges.clear()


    # ======================================================
    # Compatibility API
    # ======================================================

    @property
    def graph(self) -> Dict[str, dict]:
        """
        Legacy graph view.

        Example:

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
        Return dependency order.
        """

        indegree = {
            node: 0
            for node in self.edges
        }

        for node, deps in self.edges.items():
            indegree[node] = len(deps)

            for dep in deps:
                indegree.setdefault(
                    dep,
                    0,
                )


        queue = deque(
            node
            for node, degree in indegree.items()
            if degree == 0
        )


        reverse: Dict[str, List[str]] = {}

        for node, deps in self.edges.items():
            for dep in deps:
                reverse.setdefault(
                    dep,
                    [],
                ).append(node)


        order = []


        while queue:

            node = queue.popleft()

            order.append(node)


            for nxt in reverse.get(
                node,
                [],
            ):

                indegree[nxt] -= 1

                if indegree[nxt] == 0:
                    queue.append(nxt)


        if len(order) != len(indegree):
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