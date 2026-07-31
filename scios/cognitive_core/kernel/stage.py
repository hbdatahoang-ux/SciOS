"""
SciOS Cognitive Stage
=====================

Base abstraction for CognitivePipeline stages.

Responsibilities
-----------------
- Define stage execution contract.
- Manage lifecycle state.
- Provide serialization.
- Support backward compatibility.

Stages:
    Perception
    Memory
    Reasoning
    Planner
    ToolUse
    Reflection

Python 3.11+
"""

from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Any


from .context import CognitiveContext



__all__ = [
    "CognitiveStage",
    "Stage",
]



class CognitiveStage(ABC):
    """
    Abstract cognitive processing stage.

    Every cognitive component in SciOS
    should inherit from this class.
    """



    # =========================================================
    # Construction
    # =========================================================

    def __init__(
        self,
        name: str,
    ) -> None:

        self.name: str = name

        self.status: str = "idle"

        self.message: str | None = None

        self.executions: int = 0



    # =========================================================
    # Lifecycle
    # =========================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize stage resources.
        """

        self.status = "ready"



    def reset(
        self,
    ) -> None:
        """
        Reset stage state.
        """

        self.status = "idle"

        self.message = None



    # =========================================================
    # Execution
    # =========================================================

    @abstractmethod
    def run(
        self,
        context: CognitiveContext,
    ) -> Any:
        """
        Execute stage logic.

        Parameters
        ----------
        context:
            Cognitive execution context.

        Returns
        -------
        Any
            Stage output.
        """

        raise NotImplementedError



    def execute(
        self,
        context: CognitiveContext,
    ) -> Any:
        """
        Standard execution wrapper.

        Dispatcher should call this method.
        """

        try:

            self.status = "running"


            result = self.run(
                context
            )


            self.executions += 1


            self.status = "completed"


            return result


        except Exception as exc:


            self.status = "failed"

            self.message = str(exc)

            raise



    # =========================================================
    # State Helpers
    # =========================================================

    @property
    def is_ready(
        self,
    ) -> bool:

        return self.status == "ready"



    @property
    def is_running(
        self,
    ) -> bool:

        return self.status == "running"



    @property
    def is_completed(
        self,
    ) -> bool:

        return self.status == "completed"



    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self.name,

            "status":
                self.status,

            "message":
                self.message,

            "executions":
                self.executions,

        }



    def status_info(
        self,
    ) -> dict[str, Any]:

        return self.to_dict()



    # =========================================================
    # Protocol
    # =========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "<CognitiveStage "
            f"name={self.name!r} "
            f"status={self.status!r}>"
        )



# =============================================================
# Backward Compatibility
# =============================================================

Stage = CognitiveStage