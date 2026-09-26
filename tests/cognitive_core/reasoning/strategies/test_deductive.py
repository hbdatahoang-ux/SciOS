"""Tests for the deductive reasoning strategy."""

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy
from scios.cognitive_core.reasoning.strategies.deductive import DeductiveStrategy


def test_deductive_strategy_inherits_base_strategy():
    assert issubclass(DeductiveStrategy, BaseReasoningStrategy)


def test_deductive_strategy_has_deductive_reasoning_type():
    strategy = DeductiveStrategy()

    assert strategy.reasoning_type is ReasoningType.DEDUCTIVE


def test_deductive_strategy_executes_problem():
    strategy = DeductiveStrategy()
    problem = ReasoningProblem(query="All humans are mortal. Socrates is human.")

    result = strategy.execute(problem)

    assert isinstance(result, ReasoningResult)
    assert result.problem is problem


def test_deductive_strategy_returns_deductive_result():
    strategy = DeductiveStrategy()
    problem = ReasoningProblem(query="A implies B.")

    result = strategy.execute(problem)

    assert result.problem is problem
    assert result.metadata["reasoning_type"] == ReasoningType.DEDUCTIVE.value


def test_deductive_strategy_default_result_is_not_accepted():
    strategy = DeductiveStrategy()
    problem = ReasoningProblem(query="Test")

    result = strategy.execute(problem)

    assert result.accepted is False
