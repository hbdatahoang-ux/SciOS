"""
SciOS Runtime State
===================

Global runtime lifecycle state.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass

from enum import Enum



__all__ = [
    "RuntimeState",
    "RuntimeStatus",
]



# ==========================================================
# Runtime Status
# ==========================================================


class RuntimeStatus(
    str,
    Enum,
):

    CREATED = "created"

    INITIALIZING = "initializing"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"



# ==========================================================
# Runtime State
# ==========================================================


@dataclass
class RuntimeState:
    """
    Global execution runtime state.

    Used by:

    - ExecutionEngine
    - ExecutionContext
    - Kernel
    """


    status: RuntimeStatus = (
        RuntimeStatus.CREATED
    )


    error: str | None = None



    # ======================================================
    # Lifecycle
    # ======================================================


    def initialize(
        self,
    ) -> None:

        self.status = (
            RuntimeStatus.INITIALIZING
        )



    def start(
        self,
    ) -> None:

        self.status = (
            RuntimeStatus.RUNNING
        )



    def stop(
        self,
    ) -> None:

        self.status = (
            RuntimeStatus.STOPPED
        )



    def fail(
        self,
        error: Exception | str,
    ) -> None:

        self.status = (
            RuntimeStatus.FAILED
        )

        self.error = str(
            error
        )



    # ======================================================
    # Query
    # ======================================================


    @property
    def running(
        self,
    ) -> bool:

        return (
            self.status
            ==
            RuntimeStatus.RUNNING
        )



    @property
    def stopped(
        self,
    ) -> bool:

        return (
            self.status
            ==
            RuntimeStatus.STOPPED
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


        if status is not None:

            if isinstance(
                status,
                RuntimeStatus,
            ):

                self.status = status

            else:

                self.status = RuntimeStatus(
                    status
                )


        if error is not None:

            self.error = error



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict:

        return {

            "status":
                self.status.value,


            "error":
                self.error,

        }



    def __repr__(
        self,
    ) -> str:

        return (
            "RuntimeState("
            f"status={self.status.value!r}"
            ")"
        )