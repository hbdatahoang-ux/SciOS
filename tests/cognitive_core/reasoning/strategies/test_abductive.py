"""Tests for the abductive reasoning strategy."""

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.abductive import AbductiveStrategy
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy


def test_abductive_strategy_inherits_base_strategy():
    assert issubclass(AbductiveStrategy, BaseReasoningStrategy)


def test_abductive_strategy_has_abductive_reasoning_type():
    strategy = AbductiveStrategy()

    assert strategy.reasoning_type is ReasoningType.ABDUCTIVE


def test_abductive_strategy_executes_problem():
    strategy = AbductiveStrategy()
    problem = ReasoningProblem(query="The observation is explained by a possible cause.")

    result = strategy.execute(problem)

    assert isinstance(result, ReasoningResult)
    assert result.problem is problem


def test_abductive_strategy_returns_abductive_result():
    strategy = AbductiveStrategy()
    problem = ReasoningProblem(query="Find the most plausible explanation.")

    result = strategy.execute(problem)

    assert result.problem is problem
    assert result.metadata["reasoning_type"] == ReasoningType.ABDUCTIVE.value


def test_abductive_strategy_default_result_is_not_accepted():
    strategy = AbductiveStrategy()
    problem = ReasoningProblem(query="Test")

    result = strategy.execute(problem)

    assert result.accepted is False
