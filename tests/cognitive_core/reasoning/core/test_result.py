"""Tests for ReasoningResult."""

from uuid import UUID

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType


def test_result_creation():
    problem = ReasoningProblem(query="What is 2 + 2?")

    result = ReasoningResult(problem=problem)

    assert isinstance(result.id, UUID)
    assert result.problem is problem
    assert result.steps == []
    assert result.conclusion is None
    assert result.accepted is False
    assert result.metadata == {}


def test_result_accepts_conclusion():
    problem = ReasoningProblem(query="What is 2 + 2?")

    result = ReasoningResult(
        problem=problem,
        conclusion=4,
        accepted=True,
    )

    assert result.conclusion == 4
    assert result.accepted is True


def test_result_accepts_steps():
    problem = ReasoningProblem(query="What should we do?")
    step = ReasoningStep(
        description="Evaluate evidence",
        reasoning_type=ReasoningType.DEDUCTIVE,
        output="carry umbrella",
    )

    result = ReasoningResult(
        problem=problem,
        steps=[step],
    )

    assert result.steps == [step]
    assert result.steps[0] is step


def test_result_accepts_metadata():
    problem = ReasoningProblem(query="Evaluate evidence")

    result = ReasoningResult(
        problem=problem,
        metadata={"confidence": 0.9},
    )

    assert result.metadata == {"confidence": 0.9}


def test_result_rejects_invalid_problem():
    with pytest.raises(TypeError):
        ReasoningResult(problem={"query": "invalid"})


def test_result_ids_are_unique():
    problem = ReasoningProblem(query="A")

    first = ReasoningResult(problem=problem)
    second = ReasoningResult(problem=problem)

    assert first.id != second.id


def test_result_steps_are_not_shared():
    problem = ReasoningProblem(query="A")

    first = ReasoningResult(problem=problem)
    second = ReasoningResult(problem=problem)

    first.steps.append(ReasoningStep(description="A"))

    assert second.steps == []


def test_result_metadata_is_not_shared():
    problem = ReasoningProblem(query="A")

    first = ReasoningResult(problem=problem)
    second = ReasoningResult(problem=problem)

    first.metadata["x"] = 1

    assert second.metadata == {}


def test_result_accepts_any_conclusion():
    problem = ReasoningProblem(query="Return structured data")

    result = ReasoningResult(
        problem=problem,
        conclusion={"answer": 42},
    )

    assert result.conclusion == {"answer": 42}
