"""
SciOS Kernel State
==================

Kernel and pipeline lifecycle state definitions.

Responsibilities
-----------------
- Define pipeline lifecycle states
- Manage cognitive kernel runtime state
- Provide serialization support
- Support snapshot / restore
- Lifecycle transition helpers

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



# ==========================================================
# Pipeline State
# ==========================================================


class PipelineState(str, Enum):
    """
    Cognitive pipeline lifecycle state.
    """


    # ------------------------------------------------------
    # Initialization
    # ------------------------------------------------------

    CREATED = "created"

    INITIALIZED = "initialized"



    # ------------------------------------------------------
    # Execution
    # ------------------------------------------------------

    RUNNING = "running"

    PAUSED = "paused"



    # ------------------------------------------------------
    # Terminal states
    # ------------------------------------------------------

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    STOPPED = "stopped"

    CLOSED = "closed"



    # ------------------------------------------------------
    # Recovery
    # ------------------------------------------------------

    RESET = "reset"



    @property
    def terminal(
        self,
    ) -> bool:
        """
        Whether pipeline reached final state.
        """

        return self in {

            PipelineState.COMPLETED,

            PipelineState.FAILED,

            PipelineState.CANCELLED,

            PipelineState.STOPPED,

            PipelineState.CLOSED,

        }



    @property
    def running(
        self,
    ) -> bool:
        """
        Whether pipeline can execute.
        """

        return self in {

            PipelineState.INITIALIZED,

            PipelineState.RUNNING,

        }



    def to_dict(
        self,
    ) -> dict[str, str]:

        return {

            "state":
                self.value

        }



# ==========================================================
# Pipeline Helpers
# ==========================================================


def pipeline_state_from_value(
    value: str | PipelineState,
) -> PipelineState:
    """
    Convert raw value into PipelineState.

    Supports:
        PipelineState.RUNNING
        "running"
    """

    if isinstance(
        value,
        PipelineState,
    ):

        return value


    return PipelineState(
        value
    )



# ==========================================================
# Kernel Status
# ==========================================================


class KernelStatus(str, Enum):
    """
    Cognitive kernel runtime status.
    """


    IDLE = "idle"

    INITIALIZING = "initializing"

    RUNNING = "running"

    PAUSED = "paused"

    ERROR = "error"

    STOPPED = "stopped"

    CLOSED = "closed"



    @property
    def terminal(
        self,
    ) -> bool:

        return self in {

            KernelStatus.STOPPED,

            KernelStatus.CLOSED,

        }



# ==========================================================
# Kernel State Object
# ==========================================================


class KernelState:
    """
    Runtime state container for CognitiveKernel.
    """



    def __init__(
        self,
        status: KernelStatus = KernelStatus.IDLE,
        message: str | None = None,
    ) -> None:


        self.status = status

        self.message = message



    # ======================================================
    # Mutation
    # ======================================================


    def set_status(
        self,
        status: KernelStatus,
        message: str | None = None,
    ) -> "KernelState":
        """
        Update runtime state.
        """

        self.status = status

        self.message = message

        return self



    # ======================================================
    # Checks
    # ======================================================


    def is_idle(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.IDLE
        )



    def is_running(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.RUNNING
        )



    def is_paused(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.PAUSED
        )



    def is_error(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.ERROR
        )



    def is_stopped(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.STOPPED
        )



    def is_closed(
        self,
    ) -> bool:

        return (
            self.status
            ==
            KernelStatus.CLOSED
        )



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize state.
        """

        return {

            "status":
                self.status.value,


            "message":
                self.message,

        }



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "KernelState":
        """
        Restore state.
        """

        return cls(

            status=KernelStatus(
                data.get(
                    "status",
                    KernelStatus.IDLE.value,
                )
            ),


            message=data.get(
                "message"
            ),

        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:

        return self.to_dict()



    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "KernelState":

        restored = self.from_dict(
            snapshot
        )

        self.status = restored.status

        self.message = restored.message

        return self



    # ======================================================
    # Python Protocols
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "<KernelState "

            f"status={self.status.value!r} "

            f"message={self.message!r}>"

        )