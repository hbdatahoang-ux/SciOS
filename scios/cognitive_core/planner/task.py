"""
SciOS Planner Task
==================

Core task abstraction for SciOS cognitive planner.

Responsibilities
----------------
- Represent atomic execution unit.
- Manage constraints.
- Manage dependencies.
- Track lifecycle state.
- Support serialization.
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "Task",
]


class Task:
    """
    A single executable planning task.
    """

    # ======================================================
    # Lifecycle states
    # ======================================================

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        description: str,
        constraints: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        task_id: str | None = None,
    ) -> None:

        self.id = task_id

        self.description = description

        self.constraints: dict[str, Any] = (
            constraints.copy()
            if constraints
            else {}
        )

        self.dependencies: list[str] = (
            list(dependencies)
            if dependencies
            else []
        )

        self.completed: bool = False

        self.status: str = self.PENDING

        self.metadata: dict[str, Any] = {}


    # ======================================================
    # Constraint Management
    # ======================================================

    def add_constraint(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or update constraint.

        Example
        -------
        task.add_constraint(
            "priority",
            5,
        )
        """

        self.constraints[key] = value


    def get_constraint(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve constraint value.
        """

        return self.constraints.get(
            key,
            default,
        )


    def has_constraint(
        self,
        key: str,
    ) -> bool:
        """
        Check constraint existence.
        """

        return key in self.constraints


    def remove_constraint(
        self,
        key: str,
    ) -> None:
        """
        Remove constraint.
        """

        self.constraints.pop(
            key,
            None,
        )


    # ======================================================
    # Dependency Management
    # ======================================================

    def add_dependency(
        self,
        task_id: str,
    ) -> None:
        """
        Add dependency task id.
        """

        if task_id not in self.dependencies:

            self.dependencies.append(
                task_id
            )


    def remove_dependency(
        self,
        task_id: str,
    ) -> None:

        if task_id in self.dependencies:

            self.dependencies.remove(
                task_id
            )


    def has_dependency(
        self,
        task_id: str,
    ) -> bool:

        return task_id in self.dependencies


    # ======================================================
    # Lifecycle Management
    # ======================================================

    def start(self) -> None:
        """
        Start execution.
        """

        self.status = self.RUNNING


    def mark_completed(self) -> None:
        """
        Mark task completed.
        """

        self.completed = True

        self.status = self.COMPLETED


    def mark_failed(
        self,
        error: Exception | str,
    ) -> None:
        """
        Mark task failed.
        """

        self.completed = False

        self.status = self.FAILED

        self.metadata["error"] = str(error)


    def reset(self) -> None:
        """
        Reset task lifecycle.
        """

        self.completed = False

        self.status = self.PENDING

        self.metadata.clear()


    def is_completed(self) -> bool:
        """
        Check completed state.
        """

        return self.completed


    def is_running(self) -> bool:

        return self.status == self.RUNNING


    def is_failed(self) -> bool:

        return self.status == self.FAILED


    # ======================================================
    # Metadata
    # ======================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value


    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert task into dictionary.
        """

        return {
            "id": self.id,
            "description": self.description,
            "constraints": dict(
                self.constraints
            ),
            "dependencies": list(
                self.dependencies
            ),
            "completed": self.completed,
            "status": self.status,
            "metadata": dict(
                self.metadata
            ),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Task":
        """
        Restore task from dictionary.
        """

        task = cls(
            description=data.get(
                "description",
                "",
            ),
            constraints=data.get(
                "constraints",
                {},
            ),
            dependencies=data.get(
                "dependencies",
                [],
            ),
            task_id=data.get(
                "id",
            ),
        )

        task.completed = data.get(
            "completed",
            False,
        )

        task.status = data.get(
            "status",
            cls.PENDING,
        )

        task.metadata = dict(
            data.get(
                "metadata",
                {},
            )
        )

        return task


    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"<Task "
            f"id={self.id!r} "
            f"description='{self.description}' "
            f"status={self.status}>"
        )