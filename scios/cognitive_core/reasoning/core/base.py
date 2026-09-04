"""Base contract for reasoning strategies."""

from abc import ABC, abstractmethod

from .problem import ReasoningProblem
from .result import ReasoningResult
from .types import ReasoningType


class ReasoningStrategy(ABC):
    """Abstract interface implemented by reasoning strategies."""

    @property
    @abstractmethod
    def reasoning_type(self) -> ReasoningType:
        """Return the reasoning type supported by the strategy."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, problem: ReasoningProblem) -> ReasoningResult:
        """Execute reasoning for a problem."""
        raise NotImplementedError


__all__ = [
    "ReasoningStrategy",
]
