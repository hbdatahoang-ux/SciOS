"""
SciOS Kernel State Model
========================

Canonical state definitions for the SciOS Kernel.

Responsibilities
----------------
- Represent kernel lifecycle state.
- Track runtime statistics.
- Provide immutable snapshots.
- Support serialization.

Design Goals
------------
- Lightweight
- Strongly typed
- Serializable
- Thread-safe friendly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

__all__ = [
    "KernelStatus",
    "KernelState",
]


# ==========================================================
# Kernel Lifecycle State
# ==========================================================

class KernelStatus(str, Enum):
    """
    Kernel lifecycle states.
    """

    CREATED = "created"

    BOOTING = "booting"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"


# ==========================================================
# Kernel State
# ==========================================================

@dataclass(slots=True)
class KernelState:
    """
    Complete runtime state of the SciOS Kernel.
    """

    state: KernelStatus = KernelStatus.CREATED

    boot_count: int = 0

    tasks_executed: int = 0

    plugins_loaded: int = 0

    services_registered: int = 0

    artifacts_created: int = 0

    scheduler_queue_size: int = 0

    last_error: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # ======================================================
    # State Transition
    # ======================================================

    def transition(
        self,
        new_state: KernelStatus,
    ) -> None:
        """
        Change kernel lifecycle state.
        """

        self.state = new_state
        self.touch()

    # ======================================================
    # Statistics
    # ======================================================

    def increment_tasks(
        self,
        count: int = 1,
    ) -> None:

        self.tasks_executed += count
        self.touch()

    def increment_boots(self) -> None:

        self.boot_count += 1
        self.touch()

    def set_services(
        self,
        count: int,
    ) -> None:

        self.services_registered = count
        self.touch()

    def set_plugins(
        self,
        count: int,
    ) -> None:

        self.plugins_loaded = count
        self.touch()

    def set_artifacts(
        self,
        count: int,
    ) -> None:

        self.artifacts_created = count
        self.touch()

    def set_scheduler_queue(
        self,
        size: int,
    ) -> None:

        self.scheduler_queue_size = size
        self.touch()

    def set_error(
        self,
        message: str | None,
    ) -> None:

        self.last_error = message
        self.touch()

    # ======================================================
    # Metadata
    # ======================================================

    def update_metadata(
        self,
        **kwargs: Any,
    ) -> None:

        self.metadata.update(kwargs)
        self.touch()

    # ======================================================
    # Utilities
    # ======================================================

    def touch(self) -> None:
        """
        Update modification timestamp.
        """

        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_running(self) -> bool:

        return self.state == KernelStatus.RUNNING

    @property
    def is_stopped(self) -> bool:

        return self.state == KernelStatus.STOPPED

    @property
    def is_failed(self) -> bool:

        return self.state == KernelStatus.FAILED

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize state.
        """

        return {
            "state": self.state.value,
            "boot_count": self.boot_count,
            "tasks_executed": self.tasks_executed,
            "plugins_loaded": self.plugins_loaded,
            "services_registered": self.services_registered,
            "artifacts_created": self.artifacts_created,
            "scheduler_queue_size": self.scheduler_queue_size,
            "last_error": self.last_error,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "KernelState":
        """
        Restore state from a dictionary.
        """

        state = cls()

        state.state = KernelStatus(
            data.get("state", KernelStatus.CREATED.value)
        )

        state.boot_count = data.get("boot_count", 0)
        state.tasks_executed = data.get("tasks_executed", 0)
        state.plugins_loaded = data.get("plugins_loaded", 0)
        state.services_registered = data.get("services_registered", 0)
        state.artifacts_created = data.get("artifacts_created", 0)
        state.scheduler_queue_size = data.get("scheduler_queue_size", 0)
        state.last_error = data.get("last_error")
        state.metadata = dict(data.get("metadata", {}))

        return state

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            "KernelState("
            f"state={self.state.value!r}, "
            f"tasks={self.tasks_executed}, "
            f"services={self.services_registered}, "
            f"plugins={self.plugins_loaded}, "
            f"artifacts={self.artifacts_created})"
        )