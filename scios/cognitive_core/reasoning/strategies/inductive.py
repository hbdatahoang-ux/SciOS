"""Inductive reasoning strategy."""

from ..core.problem import ReasoningProblem
from ..core.result import ReasoningResult
from ..core.types import ReasoningType
from .base import BaseReasoningStrategy


class InductiveStrategy(BaseReasoningStrategy):
    """Reasoning strategy based on induction."""

    @property
    def reasoning_type(self) -> ReasoningType:
        return ReasoningType.INDUCTIVE

    def execute(self, problem: ReasoningProblem) -> ReasoningResult:
        if not isinstance(problem, ReasoningProblem):
            raise TypeError("problem must be a ReasoningProblem")

        return ReasoningResult(
            problem=problem,
            metadata={
                "reasoning_type": self.reasoning_type.value,
            },
        )


__all__ = [
    "InductiveStrategy",
]
