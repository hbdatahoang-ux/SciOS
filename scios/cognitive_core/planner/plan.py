"""
SciOS Cognitive Core - Planning Plan
====================================

Canonical structural plan representation for the SciOS Cognitive Core.

Responsibilities
----------------
- Hold a planning Goal.
- Hold planning Tasks.
- Maintain the Task dependency graph.
- Hold planning constraints.
- Preserve structural planning metadata.

Non-responsibilities
--------------------
- Runtime execution.
- Execution lifecycle.
- Progress tracking.
- Success/failure tracking.
- Runtime tool invocation.
- Scheduling.
- Execution graph compilation.
"""

from __future__ import annotations

from typing import Any

from .constraint import ConstraintSet
from .goal import Goal
from .task import Task
from .task_graph import TaskGraph

__all__ = ["Plan"]


class Plan:
    """
    Canonical cognitive planning representation.

    A Plan describes what should be done and how its planned Tasks
    depend on one another.

    Plan is intentionally execution-agnostic.
    """

    def __init__(
        self,
        goal: Goal,
        tasks: list[Task] | None = None,
        task_graph: TaskGraph | None = None,
        constraints: ConstraintSet | None = None,
    ) -> None:
        """
        Create a structural planning Plan.

        When ``task_graph`` is supplied, it is treated as the
        authoritative dependency topology. The supplied ``tasks``
        are validated against that graph and are not registered
        again.

        When ``task_graph`` is omitted, a new TaskGraph is created
        and supplied tasks are registered through ``add_task()``.
        """
        if not isinstance(goal, Goal):
            raise TypeError(
                "goal must be an instance of Goal"
            )

        if tasks is not None:
            if not isinstance(tasks, list):
                raise TypeError(
                    "tasks must be a list of Task"
                )

            for task in tasks:
                if not isinstance(task, Task):
                    raise TypeError(
                        "tasks must contain only Task instances"
                    )

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
        self.task_graph = task_graph or TaskGraph()
        self.constraints = constraints or ConstraintSet()
        self.metadata: dict[str, Any] = {}

        self.tasks: list[Task] = []

        if task_graph is not None:
            self._initialize_from_graph(tasks)
        else:
            for task in tasks or []:
                self.add_task(task)

    # ==========================================================
    # Initialization
    # ==========================================================

    def _initialize_from_graph(
        self,
        tasks: list[Task] | None,
    ) -> None:
        """
        Initialize the Plan from an existing authoritative TaskGraph.

        The graph owns task registration and dependency topology.
        Plan only validates and references those Tasks.
        """
        graph_tasks = self.task_graph.tasks

        if tasks is None:
            self.tasks = list(graph_tasks.values())
            return

        seen_ids: set[str] = set()

        for task in tasks:
            if task.id is None:
                raise ValueError(
                    "Tasks supplied with an existing task_graph "
                    "must have an id."
                )

            if task.id in seen_ids:
                raise ValueError(
                    f"Duplicate task '{task.id}' in tasks."
                )

            seen_ids.add(task.id)

            if task.id not in graph_tasks:
                raise ValueError(
                    f"Task '{task.id}' is not registered "
                    "in task_graph."
                )

            if graph_tasks[task.id] is not task:
                raise ValueError(
                    f"Task '{task.id}' does not match the Task "
                    "registered in task_graph."
                )

        self.tasks = list(tasks)

    # ==========================================================
    # Task Identity
    # ==========================================================

    def _allocate_task_id(self) -> str:
        """
        Allocate a deterministic local Task identifier.

        Automatically generated IDs use the form:

            task-0
            task-1
            task-2
            ...

        Allocation is based on graph occupancy rather than list position.
        """
        index = 0

        while True:
            task_id = f"task-{index}"

            if not self.task_graph.has_task(task_id):
                return task_id

            index += 1

    def _resolve_task_id(
        self,
        task: Task,
        task_id: str | None,
    ) -> str:
        """
        Resolve the canonical identifier for a Task.

        Resolution order:

        1. Explicit ``task_id``.
        2. Existing ``task.id``.
        3. Deterministic local identifier.
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

            if not task_id:
                raise ValueError(
                    "task_id must be a non-empty string"
                )

            resolved_id = task_id

        elif task.id is not None:
            if not isinstance(task.id, str):
                raise TypeError(
                    "task.id must be a string or None"
                )

            if not task.id:
                raise ValueError(
                    "task.id must be a non-empty string"
                )

            resolved_id = task.id

        else:
            resolved_id = self._allocate_task_id()

        if task.id is not None and task.id != resolved_id:
            raise ValueError(
                "task_id does not match task.id"
            )

        return resolved_id

    # ==========================================================
    # Task Management
    # ==========================================================

    def add_task(
        self,
        task: Task,
        task_id: str | None = None,
    ) -> None:
        """
        Add a Task to the Plan.

        Identifier resolution:

        1. explicit ``task_id``
        2. existing ``task.id``
        3. deterministic local identifier

        Dependency validity is delegated to TaskGraph.
        """
        if not isinstance(task, Task):
            raise TypeError(
                "task must be an instance of Task"
            )

        if task in self.tasks:
            return

        resolved_id = self._resolve_task_id(
            task,
            task_id,
        )

        if self.task_graph.has_task(resolved_id):
            raise ValueError(
                f"Task '{resolved_id}' is already registered."
            )

        original_id = task.id

        # Assign identity only immediately before registration.
        # If graph validation fails, restore the original state.
        if task.id is None:
            task.id = resolved_id

        try:
            self.task_graph.add_task(
                resolved_id,
                task,
            )

            self.tasks.append(task)

        except Exception:
            if original_id is None:
                task.id = None

            raise

    def remove_task(
        self,
        task_id: str,
    ) -> Task | None:
        """
        Remove a Task from the Plan.

        All dependency edges involving the removed Task are removed.

        Note:
            TaskGraph currently does not expose a public ``remove_task()``
            operation, so Plan performs the structural removal directly.
        """
        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

        task = self.task_graph.get_task(task_id)

        if task is None:
            return None

        # Remove references from dependent Tasks.
        for other_id in list(self.task_graph.tasks):
            if other_id == task_id:
                continue

            dependencies = self.task_graph.get_dependencies(
                other_id
            )

            if task_id in dependencies:
                self.task_graph.remove_dependency(
                    other_id,
                    task_id,
                )

        # Remove the Task from the graph itself.
        del self.task_graph.tasks[task_id]
        del self.task_graph.edges[task_id]

        # Keep Plan.tasks synchronized.
        self.tasks = [
            planned_task
            for planned_task in self.tasks
            if planned_task is not task
        ]

        return task

    def get_task(
        self,
        task_id: str,
    ) -> Task | None:
        """Retrieve a planned Task by identifier."""
        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

        return self.task_graph.get_task(task_id)

    def has_task(
        self,
        task_id: str,
    ) -> bool:
        """Return whether the Plan contains a Task."""
        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

        return self.task_graph.has_task(task_id)

    # ==========================================================
    # Structural Metadata
    # ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store structural planning metadata."""
        if not isinstance(key, str):
            raise TypeError(
                "metadata key must be a string"
            )

        if not key:
            raise ValueError(
                "metadata key must be a non-empty string"
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve structural planning metadata."""
        if not isinstance(key, str):
            raise TypeError(
                "metadata key must be a string"
            )

        return self.metadata.get(
            key,
            default,
        )

    # ==========================================================
    # Structural Ordering
    # ==========================================================

    def topological_order(self) -> list[Task]:
        """
        Return planned Tasks in dependency order.

        This is a structural graph query.

        It is NOT:

        - runtime scheduling
        - execution ordering
        - dispatch ordering
        - worker assignment
        """
        return [
            self.task_graph.tasks[task_id]
            for task_id in self.task_graph.topological_sort()
        ]

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the structural planning representation.

        Runtime execution state is intentionally absent.

        Task dependencies are serialized through each Task rather
        than duplicating graph topology in the serialized Plan.
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

    # ==========================================================
    # Structural Properties
    # ==========================================================

    @property
    def task_count(self) -> int:
        """Return the number of planned Tasks."""
        return len(self.tasks)

    @property
    def is_empty(self) -> bool:
        """Return True when the Plan contains no Tasks."""
        return not self.tasks

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self.tasks)

    def __contains__(
        self,
        task_id: str,
    ) -> bool:
        return self.has_task(task_id)

    def __repr__(self) -> str:
        return (
            f"Plan("
            f"goal={self.goal.description!r}, "
            f"tasks={len(self.tasks)}"
            f")"
        )