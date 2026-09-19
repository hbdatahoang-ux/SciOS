"""Problem model for the Reasoning subsystem."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from .types import ReasoningType


@dataclass
class ReasoningProblem:
    """Represents a problem submitted to the reasoning engine."""

    query: str
    context: dict[str, Any] = field(default_factory=dict)
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError("query must be a non-empty string")


__all__ = [
    "ReasoningProblem",
]
