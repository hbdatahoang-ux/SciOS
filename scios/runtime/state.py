"""
SciOS Runtime State
===================

Canonical global runtime lifecycle state.

Responsibilities
----------------
- Define canonical runtime lifecycle statuses.
- Store global runtime status and failure information.
- Provide lifecycle transition helpers.
- Provide lightweight state queries.
- Provide deterministic serialization.

Scope
-----
RuntimeState describes the lifecycle of the Runtime itself.

It is intentionally different from ExecutionContext.state:

    RuntimeState
        |
        +-- Runtime lifecycle
            created
            initializing
            running
            stopping
            stopped
            failed

    ExecutionContext.state
        |
        +-- Individual execution lifecycle
            created
            running
            completed
            failed

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


__all__ = [
    "RuntimeStatus",
    "RuntimeState",
]


# ==========================================================
# Runtime Status
# ==========================================================


class RuntimeStatus(
    str,
    Enum,
):
    """
    Canonical lifecycle status of the SciOS Runtime.
    """

    CREATED = "created"

    INITIALIZING = "initializing"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"


# ==========================================================
# Runtime State
# ==========================================================


@dataclass(slots=True)
class RuntimeState:
    """
    Global SciOS Runtime lifecycle state.

    This object represents the lifecycle of the Runtime itself,
    not an individual execution.

    Parameters
    ----------
    status:
        Current runtime lifecycle status.

    error:
        Human-readable failure information, if any.

    Examples
    --------
    >>> state = RuntimeState()
    >>> state.status is RuntimeStatus.CREATED
    True

    >>> state.start()
    >>> state.running
    True

    >>> state.fail("worker unavailable")
    >>> state.failed
    True
    """

    status: RuntimeStatus = RuntimeStatus.CREATED

    error: str | None = None

    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self) -> None:
        """
        Move runtime into the initializing state.
        """

        self.status = RuntimeStatus.INITIALIZING

        self.error = None

    def start(self) -> None:
        """
        Move runtime into the running state.
        """

        self.status = RuntimeStatus.RUNNING

        self.error = None

    def stop(self) -> None:
        """
        Move runtime into the stopped state.
        """

        self.status = RuntimeStatus.STOPPED

    def fail(
        self,
        error: Exception | str,
    ) -> None:
        """
        Mark runtime as failed.

        Parameters
        ----------
        error:
            Exception or human-readable failure message.
        """

        self.status = RuntimeStatus.FAILED

        self.error = str(error)

    # ======================================================
    # Queries
    # ======================================================

    @property
    def created(self) -> bool:
        """
        Return True when runtime has not started yet.
        """

        return self.status is RuntimeStatus.CREATED

    @property
    def initializing(self) -> bool:
        """
        Return True while runtime is initializing.
        """

        return self.status is RuntimeStatus.INITIALIZING

    @property
    def running(self) -> bool:
        """
        Return True while runtime is running.
        """

        return self.status is RuntimeStatus.RUNNING

    @property
    def stopping(self) -> bool:
        """
        Return True while runtime is stopping.
        """

        return self.status is RuntimeStatus.STOPPING

    @property
    def stopped(self) -> bool:
        """
        Return True when runtime has stopped.
        """

        return self.status is RuntimeStatus.STOPPED

    @property
    def failed(self) -> bool:
        """
        Return True when runtime has failed.
        """

        return self.status is RuntimeStatus.FAILED

    @property
    def terminal(self) -> bool:
        """
        Return True when runtime reached a terminal state.
        """

        return (
            self.status is RuntimeStatus.STOPPED
            or self.status is RuntimeStatus.FAILED
        )

    # ======================================================
    # Update
    # ======================================================

    def update(
        self,
        *,
        status: str | RuntimeStatus | None = None,
        error: str | None = None,
    ) -> None:
        """
        Update runtime state.

        Parameters
        ----------
        status:
            RuntimeStatus or its string value.

        error:
            Optional failure message.

        Raises
        ------
        ValueError
            If status is not a valid RuntimeStatus value.
        """

        if status is not None:

            if isinstance(
                status,
                RuntimeStatus,
            ):
                self.status = status

            else:
                self.status = RuntimeStatus(status)

        if error is not None:

            self.error = str(error)

    # ======================================================
    # Reset
    # ======================================================

    def reset(self) -> None:
        """
        Reset runtime state to CREATED.
        """

        self.status = RuntimeStatus.CREATED

        self.error = None

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize runtime state into plain Python data.
        """

        return {
            "status": self.status.value,
            "error": self.error,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RuntimeState":
        """
        Restore RuntimeState from serialized data.
        """

        status = data.get(
            "status",
            RuntimeStatus.CREATED.value,
        )

        error = data.get(
            "error",
        )

        return cls(
            status=(
                status
                if isinstance(status, RuntimeStatus)
                else RuntimeStatus(status)
            ),
            error=error,
        )

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            "RuntimeState("
            f"status={self.status.value!r}, "
            f"error={self.error!r}"
            ")"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.status.value