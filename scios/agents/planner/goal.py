"""
SciOS Goal
==========

Goal representation for the SciOS Planner.

Responsibilities
----------------
- Define planning goals
- Track goal status
- Store priority and metadata
- Provide lifecycle management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


__all__ = [
    "Goal",
    "GoalPriority",
    "GoalStatus",
]


# ==========================================================
# Goal Status
# ==========================================================

class GoalStatus(str, Enum):
    """
    Lifecycle state of a goal.
    """

    PENDING = "pending"

    READY = "ready"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ==========================================================
# Goal Priority
# ==========================================================

class GoalPriority(int, Enum):
    """
    Goal priority.
    """

    LOW = 0

    NORMAL = 1

    HIGH = 2

    CRITICAL = 3


# ==========================================================
# Goal
# ==========================================================

@dataclass(slots=True)
class Goal:
    """
    Planning goal.

    A Goal represents the desired outcome of a planning task.
    """

    id: str

    description: str

    priority: GoalPriority = GoalPriority.NORMAL

    status: GoalStatus = GoalStatus.PENDING

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    # ======================================================

    def start(self) -> None:
        """
        Mark goal as running.
        """
        self.status = GoalStatus.RUNNING

    def complete(self) -> None:
        """
        Mark goal as completed.
        """
        self.status = GoalStatus.COMPLETED

    def fail(self) -> None:
        """
        Mark goal as failed.
        """
        self.status = GoalStatus.FAILED

    def cancel(self) -> None:
        """
        Cancel the goal.
        """
        self.status = GoalStatus.CANCELLED

    def ready(self) -> None:
        """
        Mark goal as ready.
        """
        self.status = GoalStatus.READY

    # ======================================================

    @property
    def finished(self) -> bool:
        """
        Whether the goal has finished.
        """
        return self.status in {
            GoalStatus.COMPLETED,
            GoalStatus.FAILED,
            GoalStatus.CANCELLED,
        }

    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the goal.
        """

        return {

            "id": self.id,

            "description": self.description,

            "priority": self.priority.name,

            "status": self.status.value,

            "metadata": self.metadata,

            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Goal":
        """
        Deserialize a goal.
        """

        return cls(

            id=data["id"],

            description=data["description"],

            priority=GoalPriority[
                data.get(
                    "priority",
                    "NORMAL",
                )
            ],

            status=GoalStatus(
                data.get(
                    "status",
                    "pending",
                )
            ),

            metadata=data.get(
                "metadata",
                {},
            ),

            created_at=data.get(
                "created_at",
                datetime.now(
                    timezone.utc
                ).isoformat(),
            ),
        )

    # ======================================================

    def __repr__(self) -> str:

        return (

            "Goal("

            f"id='{self.id}', "

            f"status={self.status.value}, "

            f"priority={self.priority.name})"

        )
