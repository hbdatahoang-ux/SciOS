"""Tests for reasoning errors."""

from scios.cognitive_core.reasoning.core.errors import (
    ReasoningError,
    ReasoningValidationError,
)


def test_reasoning_error_is_exception():
    assert issubclass(ReasoningError, Exception)


def test_reasoning_validation_error_is_reasoning_error():
    assert issubclass(ReasoningValidationError, ReasoningError)


def test_reasoning_error_can_be_raised():
    error = ReasoningError("reasoning failed")

    assert str(error) == "reasoning failed"


def test_reasoning_validation_error_can_be_raised():
    error = ReasoningValidationError("invalid problem")

    assert str(error) == "invalid problem"
