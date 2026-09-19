"""Tests for ReasoningStep."""

from uuid import UUID

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType


def test_step_creation():
    step = ReasoningStep(description="Evaluate evidence")

    assert isinstance(step.id, UUID)
    assert step.description == "Evaluate evidence"
    assert step.reasoning_type is ReasoningType.DEDUCTIVE
    assert step.input is None
    assert step.output is None
    assert step.metadata == {}


def test_step_accepts_input_and_output():
    step = ReasoningStep(
        description="Apply rule",
        input={"rain": True},
        output="carry umbrella",
    )

    assert step.input == {"rain": True}
    assert step.output == "carry umbrella"


def test_step_accepts_reasoning_type():
    step = ReasoningStep(
        description="Find pattern",
        reasoning_type=ReasoningType.INDUCTIVE,
    )

    assert step.reasoning_type is ReasoningType.INDUCTIVE


def test_step_accepts_metadata():
    step = ReasoningStep(
        description="Evaluate evidence",
        metadata={"confidence": 0.9},
    )

    assert step.metadata == {"confidence": 0.9}


def test_step_rejects_empty_description():
    with pytest.raises(ValueError):
        ReasoningStep(description="")


def test_step_rejects_whitespace_description():
    with pytest.raises(ValueError):
        ReasoningStep(description="   ")


def test_step_ids_are_unique():
    first = ReasoningStep(description="A")
    second = ReasoningStep(description="B")

    assert first.id != second.id


def test_step_metadata_is_not_shared():
    first = ReasoningStep(description="A")
    second = ReasoningStep(description="B")

    first.metadata["x"] = 1

    assert second.metadata == {}


def test_step_can_reference_problem():
    problem = ReasoningProblem(query="What should we do?")

    step = ReasoningStep(
        description="Analyze problem",
        input=problem,
    )

    assert step.input is problem
