"""Reasoning engine."""

from ..core.problem import ReasoningProblem
from ..core.result import ReasoningResult
from ..core.types import ReasoningType
from ..strategies.abductive import AbductiveStrategy
from ..strategies.deductive import DeductiveStrategy
from ..strategies.inductive import InductiveStrategy
from ..strategies.base import BaseReasoningStrategy


class ReasoningEngine:
    """Coordinates reasoning problems with their strategies."""

    def __init__(self) -> None:
        self._strategies: dict[ReasoningType, BaseReasoningStrategy] = {
            ReasoningType.DEDUCTIVE: DeductiveStrategy(),
            ReasoningType.INDUCTIVE: InductiveStrategy(),
            ReasoningType.ABDUCTIVE: AbductiveStrategy(),
        }

    def get_strategy(
        self,
        reasoning_type: ReasoningType,
    ) -> BaseReasoningStrategy:
        """Return the strategy registered for a reasoning type."""
        if not isinstance(reasoning_type, ReasoningType):
            raise KeyError(reasoning_type)

        return self._strategies[reasoning_type]

    def execute(self, problem: ReasoningProblem) -> ReasoningResult:
        """Execute the strategy selected by the problem."""
        if not isinstance(problem, ReasoningProblem):
            raise TypeError("problem must be a ReasoningProblem")

        strategy = self.get_strategy(problem.reasoning_type)
        return strategy.execute(problem)


__all__ = [
    "ReasoningEngine",
]
