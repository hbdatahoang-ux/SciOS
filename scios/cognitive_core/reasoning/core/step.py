"""Reasoning step model."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from .types import ReasoningType


@dataclass
class ReasoningStep:
    """Represents one step in a reasoning process."""

    description: str
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    input: Any = None
    output: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")


__all__ = [
    "ReasoningStep",
]
