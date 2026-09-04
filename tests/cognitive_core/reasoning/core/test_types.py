"""Tests for reasoning core types."""

from scios.cognitive_core.reasoning.core.types import ReasoningType


def test_reasoning_type_members():
    assert ReasoningType.DEDUCTIVE.value == "deductive"
    assert ReasoningType.INDUCTIVE.value == "inductive"
    assert ReasoningType.ABDUCTIVE.value == "abductive"


def test_reasoning_type_is_enum():
    from enum import Enum

    assert issubclass(ReasoningType, Enum)


def test_reasoning_type_has_exact_members():
    assert set(ReasoningType) == {
        ReasoningType.DEDUCTIVE,
        ReasoningType.INDUCTIVE,
        ReasoningType.ABDUCTIVE,
    }
