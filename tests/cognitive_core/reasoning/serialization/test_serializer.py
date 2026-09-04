"""Tests for the reasoning serializer."""

from uuid import UUID

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.serialization.serializer import ReasoningSerializer


def make_result() -> ReasoningResult:
    problem = ReasoningProblem(
        query="Why?",
        context={"source": "test"},
        reasoning_type=ReasoningType.DEDUCTIVE,
    )
    step = ReasoningStep(
        description="Evaluate evidence",
        reasoning_type=ReasoningType.DEDUCTIVE,
        input={"x": 1},
        output={"y": 2},
        metadata={"stage": 1},
    )

    return ReasoningResult(
        problem=problem,
        steps=[step],
        conclusion="Because",
        accepted=True,
        metadata={"confidence": 0.9},
    )


def test_serializer_can_be_created():
    serializer = ReasoningSerializer()

    assert serializer is not None


def test_serialize_requires_reasoning_result():
    serializer = ReasoningSerializer()

    with pytest.raises(TypeError):
        serializer.serialize("invalid")


def test_serialize_returns_dict():
    serializer = ReasoningSerializer()

    result = serializer.serialize(make_result())

    assert isinstance(result, dict)


def test_serialize_contains_result_fields():
    serializer = ReasoningSerializer()

    data = serializer.serialize(make_result())

    assert set(data) == {
        "id",
        "problem",
        "steps",
        "conclusion",
        "accepted",
        "metadata",
    }


def test_serialize_preserves_problem_and_steps():
    serializer = ReasoningSerializer()

    data = serializer.serialize(make_result())

    assert data["problem"]["query"] == "Why?"
    assert data["problem"]["context"] == {"source": "test"}
    assert data["problem"]["reasoning_type"] == "deductive"

    assert len(data["steps"]) == 1
    assert data["steps"][0]["description"] == "Evaluate evidence"
    assert data["steps"][0]["reasoning_type"] == "deductive"


def test_deserialize_recreates_reasoning_result():
    serializer = ReasoningSerializer()
    original = make_result()

    restored = serializer.deserialize(serializer.serialize(original))

    assert isinstance(restored, ReasoningResult)
    assert isinstance(restored.problem, ReasoningProblem)
    assert isinstance(restored.steps[0], ReasoningStep)


def test_round_trip_preserves_semantic_data():
    serializer = ReasoningSerializer()
    original = make_result()

    restored = serializer.deserialize(serializer.serialize(original))

    assert restored.id == original.id
    assert restored.problem.id == original.problem.id
    assert restored.problem.query == original.problem.query
    assert restored.problem.context == original.problem.context
    assert restored.problem.reasoning_type == original.problem.reasoning_type

    assert len(restored.steps) == len(original.steps)
    assert restored.steps[0].description == original.steps[0].description
    assert restored.steps[0].input == original.steps[0].input
    assert restored.steps[0].output == original.steps[0].output
    assert restored.accepted == original.accepted
    assert restored.conclusion == original.conclusion
    assert restored.metadata == original.metadata


def test_deserialize_requires_dict():
    serializer = ReasoningSerializer()

    with pytest.raises(TypeError):
        serializer.deserialize("invalid")
