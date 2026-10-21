# ==============================================================================
# SciOS Runtime Science
# Hypothesis Model Tests
# ==============================================================================

from datetime import datetime

import pytest

from scios.runtime.science.hypothesis.models import (
    Hypothesis,
    HypothesisError,
    HypothesisStatus,
    InvalidHypothesisError,
)


# ==============================================================================
# Creation
# ==============================================================================


def test_hypothesis_creation():
    hypothesis = Hypothesis(
        id="H001",
        statement="temperature >= 10 produces response=True",
    )

    assert hypothesis.id == "H001"
    assert hypothesis.statement == (
        "temperature >= 10 produces response=True"
    )
    assert hypothesis.status is HypothesisStatus.PROPOSED
    assert hypothesis.created_at.tzinfo is not None
    assert hypothesis.metadata == {}


def test_hypothesis_created_at_is_timezone_aware():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    assert hypothesis.created_at.utcoffset() is not None


def test_custom_status():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
        status=HypothesisStatus.TESTED,
    )

    assert hypothesis.status is HypothesisStatus.TESTED


# ==============================================================================
# Validation
# ==============================================================================


def test_empty_id_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="",
            statement="x > 0",
        )


def test_whitespace_id_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="   ",
            statement="x > 0",
        )


def test_empty_statement_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="",
        )


def test_whitespace_statement_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="   ",
        )


def test_invalid_status_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="x > 0",
            status="tested",
        )


def test_naive_datetime_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="x > 0",
            created_at=datetime(2026, 1, 1),
        )


def test_invalid_created_at_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="x > 0",
            created_at="2026-01-01",
        )


def test_invalid_metadata_is_rejected():
    with pytest.raises(InvalidHypothesisError):
        Hypothesis(
            id="H001",
            statement="x > 0",
            metadata=[],
        )


# ==============================================================================
# Immutability
# ==============================================================================


def test_hypothesis_is_immutable():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    with pytest.raises(AttributeError):
        hypothesis.id = "H002"


def test_metadata_is_read_only():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
        metadata={"source": "human"},
    )

    with pytest.raises(TypeError):
        hypothesis.metadata["source"] = "ai"


def test_metadata_is_copied():
    metadata = {"source": "human"}

    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
        metadata=metadata,
    )

    metadata["source"] = "ai"

    assert hypothesis.metadata["source"] == "human"


# ==============================================================================
# Terminal state
# ==============================================================================


@pytest.mark.parametrize(
    "status",
    [
        HypothesisStatus.PROPOSED,
        HypothesisStatus.TESTED,
    ],
)
def test_non_terminal_status(status):
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
        status=status,
    )

    assert hypothesis.is_terminal() is False


@pytest.mark.parametrize(
    "status",
    [
        HypothesisStatus.SUPPORTED,
        HypothesisStatus.REFUTED,
        HypothesisStatus.INCONCLUSIVE,
        HypothesisStatus.SURPRISE,
    ],
)
def test_terminal_status(status):
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
        status=status,
    )

    assert hypothesis.is_terminal() is True


# ==============================================================================
# Functional status update
# ==============================================================================


def test_with_status_returns_new_hypothesis():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    updated = hypothesis.with_status(
        HypothesisStatus.TESTED
    )

    assert updated is not hypothesis
    assert updated.id == hypothesis.id
    assert updated.statement == hypothesis.statement
    assert updated.created_at == hypothesis.created_at
    assert updated.metadata == hypothesis.metadata
    assert updated.status is HypothesisStatus.TESTED


def test_with_same_status_returns_same_hypothesis():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    result = hypothesis.with_status(
        HypothesisStatus.PROPOSED
    )

    assert result is hypothesis


def test_with_invalid_status_is_rejected():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    with pytest.raises(InvalidHypothesisError):
        hypothesis.with_status("tested")


# ==============================================================================
# Enum semantics
# ==============================================================================


def test_status_is_string_enum():
    assert HypothesisStatus.PROPOSED.value == "proposed"
    assert HypothesisStatus.TESTED.value == "tested"
    assert HypothesisStatus.SUPPORTED.value == "supported"
    assert HypothesisStatus.REFUTED.value == "refuted"
    assert HypothesisStatus.INCONCLUSIVE.value == "inconclusive"
    assert HypothesisStatus.SURPRISE.value == "surprise"


# ==============================================================================
# Exception hierarchy
# ==============================================================================


def test_exception_hierarchy():
    assert issubclass(
        InvalidHypothesisError,
        HypothesisError,
    )

    assert issubclass(
        InvalidHypothesisError,
        ValueError,
    )


# ==============================================================================
# Representation
# ==============================================================================


def test_hypothesis_repr_contains_identity():
    hypothesis = Hypothesis(
        id="H001",
        statement="x > 0",
    )

    representation = repr(hypothesis)

    assert "Hypothesis" in representation
    assert "H001" in representation