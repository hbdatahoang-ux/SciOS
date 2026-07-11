"""
SciOS Runtime State
===================

Canonical runtime state definitions for the SciOS Runtime.

Responsibilities
----------------
- Define runtime lifecycle states.
- Provide immutable runtime status snapshots.
- Shared by ExecutionEngine, Executor, Worker and Scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

__all__ = [
    "RuntimeState",
    "RuntimeStatus",
]


# ==========================================================
# Runtime State
# ==========================================================


class RuntimeState(str, Enum):
    """
    Runtime lifecycle states.
    """

    CREATED = "created"

    INITIALIZING = "initializing"

    IDLE = "idle"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPING = "stopping"

    STOPPED = "stopped"

    COMPLETED = "completed"

    FAILED = "failed"


# ==========================================================
# Runtime Status
# ==========================================================


@dataclass(slots=True)
class RuntimeStatus:
    """
    Immutable runtime status snapshot.
    """

    state: RuntimeState = RuntimeState.CREATED

    tasks_executed: int = 0

    active_workers: int = 0

    queued_tasks: int = 0

    last_error: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    # ======================================================
    # Helpers
    # ======================================================

    @property
    def healthy(self) -> bool:
        """
        Whether the runtime is healthy.
        """

        return self.state not in (
            RuntimeState.FAILED,
            RuntimeState.STOPPED,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize status.
        """

        return {
            "state": self.state.value,
            "tasks_executed": self.tasks_executed,
            "active_workers": self.active_workers,
            "queued_tasks": self.queued_tasks,
            "last_error": self.last_error,
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp,
            "healthy": self.healthy,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RuntimeStatus":
        """
        Restore from serialized dictionary.
        """

        return cls(
            state=RuntimeState(
                data.get("state", RuntimeState.CREATED.value)
            ),
            tasks_executed=data.get(
                "tasks_executed",
                0,
            ),
            active_workers=data.get(
                "active_workers",
                0,
            ),
            queued_tasks=data.get(
                "queued_tasks",
                0,
            ),
            last_error=data.get(
                "last_error",
            ),
            metadata=dict(
                data.get("metadata", {})
            ),
            timestamp=data.get(
                "timestamp",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"state={self.state.value!r}, "
            f"tasks={self.tasks_executed}, "
            f"workers={self.active_workers}, "
            f"queued={self.queued_tasks})"
        )