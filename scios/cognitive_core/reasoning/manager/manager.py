"""Reasoning manager."""

from ..core.problem import ReasoningProblem
from ..core.result import ReasoningResult
from ..engine.engine import ReasoningEngine


class ReasoningManager:
    """Facade and lifecycle manager for reasoning execution."""

    def __init__(self, engine: ReasoningEngine | None = None) -> None:
        self._engine = engine if engine is not None else ReasoningEngine()
        self._last_result: ReasoningResult | None = None
        self._execution_count = 0

    @property
    def engine(self) -> ReasoningEngine:
        """Return the underlying reasoning engine."""
        return self._engine

    @property
    def last_result(self) -> ReasoningResult | None:
        """Return the most recent reasoning result."""
        return self._last_result

    @property
    def execution_count(self) -> int:
        """Return the number of executions performed."""
        return self._execution_count

    def execute(self, problem: ReasoningProblem) -> ReasoningResult:
        """Execute a reasoning problem through the underlying engine."""
        if not isinstance(problem, ReasoningProblem):
            raise TypeError("problem must be a ReasoningProblem")

        result = self._engine.execute(problem)

        self._last_result = result
        self._execution_count += 1

        return result


__all__ = [
    "ReasoningManager",
]
