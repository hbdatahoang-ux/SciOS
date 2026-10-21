"""
SciOS Cognitive Stage
=====================

Base abstraction for stages executed by the SciOS Cognitive Kernel.

Responsibilities
-----------------
- Define the stage execution contract.
- Manage stage lifecycle state.
- Track successful executions.
- Provide serialization.
- Preserve backward compatibility through ``Stage``.

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
    Abstract base class for all cognitive processing stages.

    A stage receives a :class:`CognitiveContext`, performs its
    cognitive operation, and returns an arbitrary result.

    Lifecycle
    ---------
    idle
        Newly created or reset stage.

    ready
        Stage initialized and ready for execution.

    running
        Stage is currently executing.

    completed
        Last execution completed successfully.

    failed
        Last execution raised an exception.
    """

    # =========================================================
    # Construction
    # =========================================================

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.status: str = "idle"
        self.message: str | None = None
        self.executions: int = 0

    # =========================================================
    # Lifecycle
    # =========================================================

    def initialize(self) -> None:
        """
        Initialize stage resources.

        Initialization changes lifecycle status to ``ready``.
        Existing diagnostic message is preserved.
        """
        self.status = "ready"

    def reset(self) -> None:
        """
        Reset the stage lifecycle state.

        The execution counter is intentionally preserved because it
        represents historical successful executions.
        """
        self.status = "idle"
        self.message = None

    # =========================================================
    # Execution
    # =========================================================

    @abstractmethod
    def run(self, context: CognitiveContext) -> Any:
        """
        Execute the stage-specific cognitive operation.

        Parameters
        ----------
        context:
            Shared cognitive execution context.

        Returns
        -------
        Any
            Stage-specific result.

        Raises
        ------
        NotImplementedError
            If a subclass does not implement the method.
        """
        raise NotImplementedError

    def execute(self, context: CognitiveContext) -> Any:
        """
        Execute the stage through the standard lifecycle wrapper.

        Successful execution:

            running -> completed

        Failed execution:

            running -> failed

        The original exception is re-raised after the stage state
        has been updated.
        """
        self.status = "running"
        self.message = None

        try:
            result = self.run(context)

        except Exception as exc:
            self.status = "failed"
            self.message = str(exc)
            raise

        self.executions += 1
        self.status = "completed"

        return result

    # =========================================================
    # State Helpers
    # =========================================================

    @property
    def is_ready(self) -> bool:
        """Return True when the stage is ready."""
        return self.status == "ready"

    @property
    def is_running(self) -> bool:
        """Return True when the stage is executing."""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """Return True when the latest execution completed."""
        return self.status == "completed"

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the current stage state.
        """
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "executions": self.executions,
        }

    def status_info(self) -> dict[str, Any]:
        """
        Return the current serialized stage status.
        """
        return self.to_dict()

    # =========================================================
    # Python Protocols
    # =========================================================

    def __repr__(self) -> str:
        return (
            "<CognitiveStage "
            f"name={self.name!r} "
            f"status={self.status!r}>"
        )


# =============================================================
# Backward Compatibility
# =============================================================

Stage = CognitiveStage