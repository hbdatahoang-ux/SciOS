"""Tests for ReasoningProblem."""

from uuid import UUID

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.types import ReasoningType


def test_problem_creation():
    problem = ReasoningProblem(query="What is 2 + 2?")

    assert isinstance(problem.id, UUID)
    assert problem.query == "What is 2 + 2?"
    assert problem.context == {}
    assert problem.reasoning_type is ReasoningType.DEDUCTIVE


def test_problem_accepts_context():
    context = {"a": 2, "b": 2}

    problem = ReasoningProblem(
        query="What is the sum?",
        context=context,
    )

    assert problem.context == context


def test_problem_accepts_reasoning_type():
    problem = ReasoningProblem(
        query="Find a pattern.",
        reasoning_type=ReasoningType.INDUCTIVE,
    )

    assert problem.reasoning_type is ReasoningType.INDUCTIVE


def test_problem_rejects_empty_query():
    with pytest.raises(ValueError):
        ReasoningProblem(query="")


def test_problem_rejects_whitespace_query():
    with pytest.raises(ValueError):
        ReasoningProblem(query="   ")


def test_problem_ids_are_unique():
    first = ReasoningProblem(query="A")
    second = ReasoningProblem(query="B")

    assert first.id != second.id


def test_problem_context_is_not_shared():
    first = ReasoningProblem(query="A")
    second = ReasoningProblem(query="B")

    first.context["x"] = 1

    assert second.context == {}
