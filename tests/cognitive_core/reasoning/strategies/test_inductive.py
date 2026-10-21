"""Tests for the inductive reasoning strategy."""

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy
from scios.cognitive_core.reasoning.strategies.inductive import InductiveStrategy


def test_inductive_strategy_inherits_base_strategy():
    assert issubclass(InductiveStrategy, BaseReasoningStrategy)


def test_inductive_strategy_has_inductive_reasoning_type():
    strategy = InductiveStrategy()

    assert strategy.reasoning_type is ReasoningType.INDUCTIVE


def test_inductive_strategy_executes_problem():
    strategy = InductiveStrategy()
    problem = ReasoningProblem(query="Observed A, B, and C share a property.")

    result = strategy.execute(problem)

    assert isinstance(result, ReasoningResult)
    assert result.problem is problem


def test_inductive_strategy_returns_inductive_result():
    strategy = InductiveStrategy()
    problem = ReasoningProblem(query="Several observations support a pattern.")

    result = strategy.execute(problem)

    assert result.problem is problem
    assert result.metadata["reasoning_type"] == ReasoningType.INDUCTIVE.value


def test_inductive_strategy_default_result_is_not_accepted():
    strategy = InductiveStrategy()
    problem = ReasoningProblem(query="Test")

    result = strategy.execute(problem)

    assert result.accepted is False
