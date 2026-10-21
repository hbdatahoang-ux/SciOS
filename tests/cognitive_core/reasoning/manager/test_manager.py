"""Tests for the reasoning manager."""

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.engine.engine import ReasoningEngine
from scios.cognitive_core.reasoning.manager.manager import ReasoningManager


def test_reasoning_manager_can_be_created():
    manager = ReasoningManager()

    assert manager is not None


def test_reasoning_manager_creates_default_engine():
    manager = ReasoningManager()

    assert isinstance(manager.engine, ReasoningEngine)


def test_reasoning_manager_accepts_engine_injection():
    engine = ReasoningEngine()
    manager = ReasoningManager(engine=engine)

    assert manager.engine is engine


def test_reasoning_manager_initial_execution_count_is_zero():
    manager = ReasoningManager()

    assert manager.execution_count == 0


def test_reasoning_manager_initial_last_result_is_none():
    manager = ReasoningManager()

    assert manager.last_result is None


def test_reasoning_manager_delegates_execution_to_engine():
    engine = ReasoningEngine()
    manager = ReasoningManager(engine=engine)
    problem = ReasoningProblem(
        query="Test",
        reasoning_type=ReasoningType.DEDUCTIVE,
    )

    result = manager.execute(problem)

    assert isinstance(result, ReasoningResult)
    assert result.problem is problem
    assert manager.last_result is result


def test_reasoning_manager_increments_execution_count():
    manager = ReasoningManager()

    problem = ReasoningProblem(query="Test")

    manager.execute(problem)
    manager.execute(problem)

    assert manager.execution_count == 2


def test_reasoning_manager_updates_last_result():
    manager = ReasoningManager()

    first_problem = ReasoningProblem(query="First")
    second_problem = ReasoningProblem(query="Second")

    first_result = manager.execute(first_problem)
    second_result = manager.execute(second_problem)

    assert manager.last_result is second_result
    assert manager.last_result is not first_result
    assert manager.execution_count == 2


def test_reasoning_manager_rejects_invalid_problem():
    manager = ReasoningManager()

    with pytest.raises(TypeError):
        manager.execute("not a reasoning problem")
