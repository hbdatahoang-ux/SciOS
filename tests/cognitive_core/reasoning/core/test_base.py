"""Tests for the reasoning strategy base contract."""

from abc import ABC

import pytest

from scios.cognitive_core.reasoning.core.base import ReasoningStrategy
from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType


def test_reasoning_strategy_is_abstract_base_class():
    assert issubclass(ReasoningStrategy, ABC)


def test_reasoning_strategy_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ReasoningStrategy()


def test_concrete_strategy_must_implement_contract():
    class DummyStrategy(ReasoningStrategy):
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
    problem = ReasoningProblem(query="Test reasoning")
    result = strategy.execute(problem)

    assert strategy.reasoning_type is ReasoningType.DEDUCTIVE
    assert isinstance(result, ReasoningResult)
    assert result.problem is problem
    assert result.conclusion == "dummy"
    assert result.accepted is True


def test_reasoning_type_is_abstract():
    class IncompleteStrategy(ReasoningStrategy):
        def execute(self, problem: ReasoningProblem) -> ReasoningResult:
            return ReasoningResult(problem=problem)

    with pytest.raises(TypeError):
        IncompleteStrategy()


def test_execute_is_abstract():
    class IncompleteStrategy(ReasoningStrategy):
        @property
        def reasoning_type(self) -> ReasoningType:
            return ReasoningType.DEDUCTIVE

    with pytest.raises(TypeError):
        IncompleteStrategy()
