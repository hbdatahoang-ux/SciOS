"""
SciOS Runtime Agent State
=========================

Agent lifecycle state.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass
from enum import Enum



__all__ = [
    "AgentState",
    "AgentStatus",
]



class AgentStatus(
    str,
    Enum,
):

    IDLE = "idle"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"



@dataclass
class AgentState:
    """
    Runtime state of Agent.
    """


    status: str = AgentStatus.IDLE.value


    task: str | None = None


    error: str | None = None


    result: object | None = None



    # ======================================================
    # Lifecycle
    # ======================================================


    def start(
        self,
        task: str,
    ) -> None:

        self.status = AgentStatus.RUNNING.value

        self.task = task

        self.error = None



    def complete(
        self,
        result=None,
    ) -> None:

        self.status = AgentStatus.COMPLETED.value

        self.result = result



    def fail(
        self,
        error,
    ) -> None:

        self.status = AgentStatus.FAILED.value

        self.error = str(error)



    def reset(
        self,
    ) -> None:

        self.status = AgentStatus.IDLE.value

        self.task = None

        self.error = None

        self.result = None



    # ======================================================
    # Update API
    # ======================================================


    def update(
        self,
        **kwargs,
    ) -> None:

        for key, value in kwargs.items():

            if hasattr(
                self,
                key,
            ):

                setattr(
                    self,
                    key,
                    value,
                )



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict:

        return {

            "status":
                self.status,


            "task":
                self.task,


            "error":
                self.error,


            "result":
                self.result,

        }



    def __repr__(
        self,
    ) -> str:

        return (
            "AgentState("
            f"status={self.status!r}"
            ")"
        )