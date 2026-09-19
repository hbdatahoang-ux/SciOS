"""
SciOS Cognitive Core - Planning Task
====================================

Core task abstraction for the cognitive planner.

A Task represents a single unit of planned work.

Responsibilities
----------------
- Represent a planning task.
- Manage planning constraints.
- Manage task dependencies.
- Store planning metadata.
- Support structural serialization.

Non-responsibilities
--------------------
- Runtime execution.
- Execution lifecycle.
- Runtime status tracking.
- Success/failure tracking.
- Retry or recovery.
"""

from __future__ import annotations

from typing import Any

__all__ = ["Task"]


class Task:
    """
    A single cognitive planning task.

    Task is a planning-domain object only.

    Execution state belongs to the Runtime / Execution layer and must
    not be represented by this object.
    """

    def __init__(
        self,
        description: str,
        constraints: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        task_id: str | None = None,
    ) -> None:
        if not isinstance(description, str):
            raise TypeError("description must be a string")

        if constraints is not None and not isinstance(constraints, dict):
            raise TypeError("constraints must be a dictionary")

        if dependencies is not None and not isinstance(dependencies, list):
            raise TypeError("dependencies must be a list")

        if dependencies is not None and not all(
            isinstance(dependency, str)
            for dependency in dependencies
        ):
            raise TypeError(
                "dependencies must contain only strings"
            )

        if task_id is not None and not isinstance(task_id, str):
            raise TypeError("task_id must be a string or None")

        self.id = task_id
        self.description = description

        self.constraints: dict[str, Any] = (
            dict(constraints)
            if constraints is not None
            else {}
        )

        self.dependencies: list[str] = (
            list(dependencies)
            if dependencies is not None
            else []
        )

        self.metadata: dict[str, Any] = {}

    # ======================================================
    # Constraint Management
    # ======================================================

    def add_constraint(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Add or update a planning constraint."""
        if not isinstance(key, str):
            raise TypeError("constraint key must be a string")

        self.constraints[key] = value

    def get_constraint(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve a planning constraint."""
        if not isinstance(key, str):
            raise TypeError("constraint key must be a string")

        return self.constraints.get(key, default)

    def has_constraint(
        self,
        key: str,
    ) -> bool:
        """Check whether a planning constraint exists."""
        if not isinstance(key, str):
            raise TypeError("constraint key must be a string")

        return key in self.constraints

    def remove_constraint(
        self,
        key: str,
    ) -> None:
        """Remove a planning constraint if present."""
        if not isinstance(key, str):
            raise TypeError("constraint key must be a string")

        self.constraints.pop(key, None)

    # ======================================================
    # Dependency Management
    # ======================================================

    def add_dependency(
        self,
        task_id: str,
    ) -> None:
        """
        Add a dependency by task identifier.

        Dependency existence and graph validity are validated by
        TaskGraph, not by Task.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        if task_id == self.id:
            raise ValueError("task cannot depend on itself")

        if task_id not in self.dependencies:
            self.dependencies.append(task_id)

    def remove_dependency(
        self,
        task_id: str,
    ) -> None:
        """Remove a dependency if present."""
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        if task_id in self.dependencies:
            self.dependencies.remove(task_id)

    def has_dependency(
        self,
        task_id: str,
    ) -> bool:
        """Check whether this task depends on another task."""
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")

        return task_id in self.dependencies

    # ======================================================
    # Metadata
    # ======================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store planning metadata."""
        if not isinstance(key, str):
            raise TypeError("metadata key must be a string")

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve planning metadata."""
        if not isinstance(key, str):
            raise TypeError("metadata key must be a string")

        return self.metadata.get(key, default)

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the structural planning representation.

        Runtime execution state is intentionally excluded.
        """
        return {
            "id": self.id,
            "description": self.description,
            "constraints": dict(self.constraints),
            "dependencies": list(self.dependencies),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Task":
        """
        Restore a Task from its structural representation.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        task = cls(
            description=data.get("description", ""),
            constraints=data.get("constraints", {}),
            dependencies=data.get("dependencies", []),
            task_id=data.get("id"),
        )

        metadata = data.get("metadata", {})

        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary")

        task.metadata = dict(metadata)

        return task

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<Task "
            f"id={self.id!r} "
            f"description={self.description!r}>"
        )