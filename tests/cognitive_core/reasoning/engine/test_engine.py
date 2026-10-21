"""Tests for the reasoning engine."""

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.engine.engine import ReasoningEngine


def test_reasoning_engine_can_be_created():
    engine = ReasoningEngine()

    assert engine is not None


def test_reasoning_engine_has_default_deductive_strategy():
    engine = ReasoningEngine()

    strategy = engine.get_strategy(ReasoningType.DEDUCTIVE)

    assert strategy is not None
    assert strategy.reasoning_type is ReasoningType.DEDUCTIVE


def test_reasoning_engine_has_inductive_strategy():
    engine = ReasoningEngine()

    strategy = engine.get_strategy(ReasoningType.INDUCTIVE)

    assert strategy is not None
    assert strategy.reasoning_type is ReasoningType.INDUCTIVE


def test_reasoning_engine_has_abductive_strategy():
    engine = ReasoningEngine()

    strategy = engine.get_strategy(ReasoningType.ABDUCTIVE)

    assert strategy is not None
    assert strategy.reasoning_type is ReasoningType.ABDUCTIVE


def test_reasoning_engine_can_execute_problem():
    engine = ReasoningEngine()
    problem = ReasoningProblem(
        query="All humans are mortal. Socrates is human.",
        reasoning_type=ReasoningType.DEDUCTIVE,
    )

    result = engine.execute(problem)

    assert isinstance(result, ReasoningResult)
    assert result.problem is problem
    assert result.metadata["reasoning_type"] == ReasoningType.DEDUCTIVE.value


def test_reasoning_engine_uses_problem_reasoning_type():
    engine = ReasoningEngine()

    problem = ReasoningProblem(
        query="Several observations support a pattern.",
        reasoning_type=ReasoningType.INDUCTIVE,
    )

    result = engine.execute(problem)

    assert result.metadata["reasoning_type"] == ReasoningType.INDUCTIVE.value


def test_reasoning_engine_can_execute_abductive_problem():
    engine = ReasoningEngine()

    problem = ReasoningProblem(
        query="Find the most plausible explanation.",
        reasoning_type=ReasoningType.ABDUCTIVE,
    )

    result = engine.execute(problem)

    assert result.metadata["reasoning_type"] == ReasoningType.ABDUCTIVE.value


def test_reasoning_engine_rejects_invalid_problem():
    engine = ReasoningEngine()

    with pytest.raises(TypeError):
        engine.execute("not a reasoning problem")


def test_reasoning_engine_rejects_unknown_strategy_type():
    engine = ReasoningEngine()

    with pytest.raises(KeyError):
        engine.get_strategy("unknown")
