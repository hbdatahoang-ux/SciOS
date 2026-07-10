"""
SciOS Kernel State
==================

Defines the lifecycle state and runtime status of the SciOS Kernel.

This module is intentionally independent from the rest of the
kernel to avoid circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


__all__ = ["KernelState", "KernelStatus"]


class KernelState(Enum):
    """
    Lifecycle states of the SciOS Kernel.
    """

    CREATED = "created"
    BOOTING = "booting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self is KernelState.RUNNING

    @property
    def is_active(self) -> bool:
        return self in (KernelState.BOOTING, KernelState.RUNNING)

    @property
    def is_terminal(self) -> bool:
        return self in (KernelState.STOPPED, KernelState.FAILED)


@dataclass(slots=True)
class KernelStatus:
    """
    Runtime status of the kernel.

    This object represents the observable state of the kernel
    and can safely be returned to monitoring systems.
    """

    state: KernelState = KernelState.CREATED
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    boot_count: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------

    def mark_booting(self) -> None:
        self.state = KernelState.BOOTING

    def mark_running(self) -> None:
        self.state = KernelState.RUNNING
        self.started_at = datetime.utcnow()
        self.boot_count += 1

    def mark_stopping(self) -> None:
        self.state = KernelState.STOPPING

    def mark_stopped(self) -> None:
        self.state = KernelState.STOPPED
        self.stopped_at = datetime.utcnow()

    def mark_failed(self, error: Exception | str) -> None:
        self.state = KernelState.FAILED
        self.last_error = str(error)
        self.stopped_at = datetime.utcnow()

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    @property
    def uptime(self):
        """Return uptime as timedelta or None."""
        if self.started_at is None:
            return None
        if self.state is KernelState.RUNNING:
            return datetime.utcnow() - self.started_at
        if self.stopped_at is not None:
            return self.stopped_at - self.started_at
        return None

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot."""
        return {
            "state": self.state.value,
            "boot_count": self.boot_count,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "last_error": self.last_error,
            "metadata": dict(self.metadata),
        }

    def reset(self) -> None:
        """Reset status information."""
        self.state = KernelState.CREATED
        self.started_at = None
        self.stopped_at = None
        self.last_error = None
        self.metadata.clear()

    def __repr__(self) -> str:
        return f"KernelStatus(state={self.state.value}, boot_count={self.boot_count})"
