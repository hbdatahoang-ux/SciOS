"""
SciOS Kernel State
==================

Lifecycle state definitions for the SciOS cognitive kernel
and cognitive pipeline.

Python 3.11+
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Mapping


__all__ = [
    "PipelineState",
    "KernelStatus",
    "KernelState",
    "pipeline_state_from_value",
]


# ============================================================
# Pipeline State
# ============================================================


class PipelineState(str, Enum):
    """
    Lifecycle state of a cognitive pipeline.
    """

    CREATED = "created"
    INITIALIZED = "initialized"

    RUNNING = "running"
    PAUSED = "paused"

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STOPPED = "stopped"
    CLOSED = "closed"

    RESET = "reset"

    @property
    def terminal(self) -> bool:
        """Return True when the pipeline is in a terminal state."""
        return self in {
            PipelineState.COMPLETED,
            PipelineState.FAILED,
            PipelineState.CANCELLED,
            PipelineState.STOPPED,
            PipelineState.CLOSED,
        }

    @property
    def running(self) -> bool:
        """
        Return True when the pipeline is in an executable state.
        """
        return self in {
            PipelineState.INITIALIZED,
            PipelineState.RUNNING,
        }

    def to_dict(self) -> dict[str, str]:
        """Serialize the pipeline state."""
        return {
            "state": self.value,
        }


# ============================================================
# Pipeline State Conversion
# ============================================================


def pipeline_state_from_value(
    value: str | PipelineState,
) -> PipelineState:
    """
    Convert a raw value into PipelineState.

    Examples
    --------
    >>> pipeline_state_from_value("running")
    PipelineState.RUNNING

    >>> pipeline_state_from_value(PipelineState.RUNNING)
    PipelineState.RUNNING
    """
    if isinstance(value, PipelineState):
        return value

    return PipelineState(value)


# ============================================================
# Kernel Status
# ============================================================


class KernelStatus(str, Enum):
    """
    Runtime status of the cognitive kernel.
    """

    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    CLOSED = "closed"

    @property
    def terminal(self) -> bool:
        """Return True when the kernel cannot continue execution."""
        return self in {
            KernelStatus.STOPPED,
            KernelStatus.CLOSED,
        }


# ============================================================
# Kernel State
# ============================================================


class KernelState:
    """
    Mutable runtime state container for CognitiveKernel.

    Parameters
    ----------
    status:
        Initial kernel status.
    message:
        Optional human-readable state message.
    """

    def __init__(
        self,
        status: KernelStatus = KernelStatus.IDLE,
        message: str | None = None,
    ) -> None:
        self.status = self._normalize_status(status)
        self.message = message

    # --------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------

    @staticmethod
    def _normalize_status(
        status: KernelStatus | str,
    ) -> KernelStatus:
        """Normalize enum/string status into KernelStatus."""
        if isinstance(status, KernelStatus):
            return status

        return KernelStatus(status)

    # --------------------------------------------------------
    # Mutation
    # --------------------------------------------------------

    def set_status(
        self,
        status: KernelStatus | str,
        message: str | None = None,
    ) -> KernelState:
        """
        Update kernel status and optional message.

        Returns
        -------
        KernelState
            This instance, allowing method chaining.
        """
        self.status = self._normalize_status(status)
        self.message = message
        return self

    # --------------------------------------------------------
    # State checks
    # --------------------------------------------------------

    def is_idle(self) -> bool:
        """Return True when kernel is idle."""
        return self.status is KernelStatus.IDLE

    def is_running(self) -> bool:
        """Return True when kernel is running."""
        return self.status is KernelStatus.RUNNING

    def is_paused(self) -> bool:
        """Return True when kernel is paused."""
        return self.status is KernelStatus.PAUSED

    def is_error(self) -> bool:
        """Return True when kernel is in an error state."""
        return self.status is KernelStatus.ERROR

    def is_stopped(self) -> bool:
        """Return True when kernel is stopped."""
        return self.status is KernelStatus.STOPPED

    def is_closed(self) -> bool:
        """Return True when kernel is closed."""
        return self.status is KernelStatus.CLOSED

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize kernel state to a dictionary."""
        return {
            "status": self.status.value,
            "message": self.message,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> KernelState:
        """
        Restore KernelState from a mapping.
        """
        status = data.get(
            "status",
            KernelStatus.IDLE.value,
        )

        message = data.get(
            "message",
        )

        return cls(
            status=cls._normalize_status(status),
            message=message,
        )

    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot."""
        return self.to_dict()

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> KernelState:
        """
        Restore this instance from a snapshot.

        Returns
        -------
        KernelState
            This instance.
        """
        restored = self.from_dict(snapshot)

        self.status = restored.status
        self.message = restored.message

        return self

    # --------------------------------------------------------
    # Python protocols
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "<KernelState "
            f"status={self.status.value!r} "
            f"message={self.message!r}>"
        )