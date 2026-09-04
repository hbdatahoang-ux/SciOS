"""Reasoning result model."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from .problem import ReasoningProblem
from .step import ReasoningStep


@dataclass
class ReasoningResult:
    """Represents the result of one reasoning execution."""

    problem: ReasoningProblem
    steps: list[ReasoningStep] = field(default_factory=list)
    conclusion: Any = None
    accepted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.problem, ReasoningProblem):
            raise TypeError("problem must be a ReasoningProblem")


__all__ = [
    "ReasoningResult",
]
