"""Tests for the reasoning strategy base contract."""

from abc import ABC

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy


def test_base_reasoning_strategy_is_abstract():
    assert issubclass(BaseReasoningStrategy, ABC)


def test_base_reasoning_strategy_inherits_reasoning_strategy():
    from scios.cognitive_core.reasoning.core.base import ReasoningStrategy

    assert issubclass(BaseReasoningStrategy, ReasoningStrategy)


def test_base_reasoning_strategy_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseReasoningStrategy()


def test_concrete_strategy_implements_execute():
    class DummyStrategy(BaseReasoningStrategy):
        @property
        def reasoning_type(self) -> ReasoningType:
            return ReasoningType.DEDUCTIVE

        def execute(self, problem: ReasoningProblem) -> ReasoningResult:
            return ReasoningResult(
                problem=problem,
                conclusion="dummy",
                accepted=True,
            )

    strategy = DummyStrategy()
    problem = ReasoningProblem(query="test")
    result = strategy.execute(problem)

    assert strategy.reasoning_type is ReasoningType.DEDUCTIVE
    assert isinstance(result, ReasoningResult)
    assert result.problem is problem
    assert result.conclusion == "dummy"
    assert result.accepted is True


def test_concrete_strategy_must_provide_reasoning_type():
    class IncompleteStrategy(BaseReasoningStrategy):
        def execute(self, problem: ReasoningProblem) -> ReasoningResult:
            return ReasoningResult(problem=problem)

    with pytest.raises(TypeError):
        IncompleteStrategy()
