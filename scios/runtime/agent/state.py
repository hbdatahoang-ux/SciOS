"""
SciOS Runtime Agent State
=========================

Agent lifecycle state container.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Any


__all__ = [
    "AgentState",
]


@dataclass
class AgentState:
    """
    Runtime state of an Agent.
    """

    status: str = "idle"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    def update(
        self,
        *,
        status: str | None = None,
        **metadata,
    ) -> None:
        """
        Update agent state.
        """

        if status is not None:
            self.status = status


        self.metadata.update(
            metadata
        )


    def reset(self) -> None:
        """
        Reset state.
        """

        self.status = "idle"

        self.metadata.clear()



    def to_dict(self) -> dict[str, Any]:

        return {
            "status": self.status,
            "metadata": self.metadata,
        }



    def __repr__(self) -> str:

        return (
            "AgentState("
            f"status={self.status!r}"
            ")"
        )