from __future__ import annotations

import pytest

from scios.cognitive_core.common.errors import (
    CognitiveError,
    MemoryError,
    PipelineError,
    PlannerError,
    ReasoningError,
    ToolError,
)


# ==========================================================
# Base Error
# ==========================================================


def test_cognitive_error_is_exception():
    assert issubclass(CognitiveError, Exception)


def test_cognitive_error_can_be_raised():
    with pytest.raises(CognitiveError):
        raise CognitiveError("cognitive failure")


def test_cognitive_error_preserves_message():
    error = CognitiveError("test error")

    assert str(error) == "test error"


# ==========================================================
# Specialized Errors
# ==========================================================


@pytest.mark.parametrize(
    "error_type",
    [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_specialized_errors_inherit_from_cognitive_error(error_type):
    assert issubclass(error_type, CognitiveError)


@pytest.mark.parametrize(
    "error_type",
    [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_specialized_errors_are_exceptions(error_type):
    assert issubclass(error_type, Exception)


@pytest.mark.parametrize(
    "error_type",
    [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_specialized_errors_preserve_message(error_type):
    error = error_type("test failure")

    assert str(error) == "test failure"


@pytest.mark.parametrize(
    "error_type",
    [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_specialized_errors_can_be_raised(error_type):
    with pytest.raises(error_type):
        raise error_type("failure")


# ==========================================================
# Exception Identity
# ==========================================================


def test_specialized_errors_are_distinct_types():
    error_types = {
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    }

    assert len(error_types) == 5


def test_specialized_errors_do_not_inherit_from_each_other():
    error_types = [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ]

    for current in error_types:
        for other in error_types:
            if current is other:
                continue

            assert not issubclass(current, other)


# ==========================================================
# Catching Through Base Class
# ==========================================================


@pytest.mark.parametrize(
    "error_type",
    [
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_specialized_errors_are_caught_by_cognitive_error(error_type):
    with pytest.raises(CognitiveError):
        raise error_type("failure")


# ==========================================================
# Catching Through Exception
# ==========================================================


@pytest.mark.parametrize(
    "error_type",
    [
        CognitiveError,
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_all_errors_are_caught_by_exception(error_type):
    with pytest.raises(Exception):
        raise error_type("failure")


# ==========================================================
# Empty Messages
# ==========================================================


@pytest.mark.parametrize(
    "error_type",
    [
        CognitiveError,
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_errors_support_empty_message(error_type):
    error = error_type()

    assert str(error) == ""


# ==========================================================
# Arguments
# ==========================================================


@pytest.mark.parametrize(
    "error_type",
    [
        CognitiveError,
        PlannerError,
        ReasoningError,
        MemoryError,
        ToolError,
        PipelineError,
    ],
)
def test_errors_preserve_args(error_type):
    error = error_type("failure", 42)

    assert error.args == ("failure", 42)