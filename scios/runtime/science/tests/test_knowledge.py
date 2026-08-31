# ==============================================================================
# SciOS Runtime Science
# Knowledge Model Tests
# ==============================================================================

from datetime import datetime, timezone

import pytest

from scios.runtime.science.knowledge.models import (
    Knowledge,
    KnowledgeError,
    InvalidKnowledgeError,
    KnowledgeStatus,
)


# ==============================================================================
# Creation
# ==============================================================================


def test_knowledge_creation():
    knowledge = Knowledge(
        id="K001",
        statement="Increasing flow rate changes oscillation frequency.",
        evidence_ids=("O001",),
    )

    assert knowledge.id == "K001"
    assert (
        knowledge.statement
        == "Increasing flow rate changes oscillation frequency."
    )
    assert knowledge.evidence_ids == ("O001",)
    assert knowledge.status is KnowledgeStatus.PROVISIONAL


def test_knowledge_defaults_to_provisional():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
    )

    assert knowledge.status is KnowledgeStatus.PROVISIONAL
    assert knowledge.evidence_ids == ()


def test_created_at_defaults_to_utc():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
    )

    assert knowledge.created_at.tzinfo is not None
    assert knowledge.created_at.utcoffset() is not None
    assert knowledge.created_at.tzinfo == timezone.utc


def test_explicit_timezone_aware_created_at_is_preserved():
    created_at = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )

    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        created_at=created_at,
    )

    assert knowledge.created_at == created_at


# ==============================================================================
# Validation
# ==============================================================================


def test_empty_id_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="",
            statement="A scientific statement.",
        )


def test_whitespace_id_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="   ",
            statement="A scientific statement.",
        )


def test_empty_statement_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="K001",
            statement="",
        )


def test_whitespace_statement_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="K001",
            statement="   ",
        )


def test_naive_datetime_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="K001",
            statement="A scientific statement.",
            created_at=datetime(2026, 1, 1),
        )


def test_duplicate_evidence_ids_are_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="K001",
            statement="A scientific statement.",
            evidence_ids=("O001", "O001"),
        )


def test_empty_evidence_id_is_rejected():
    with pytest.raises(InvalidKnowledgeError):
        Knowledge(
            id="K001",
            statement="A scientific statement.",
            evidence_ids=("O001", ""),
        )


# ==============================================================================
# Immutability
# ==============================================================================


def test_knowledge_is_immutable():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
    )

    with pytest.raises(AttributeError):
        knowledge.id = "K002"


def test_evidence_ids_are_immutable():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        evidence_ids=("O001",),
    )

    assert isinstance(knowledge.evidence_ids, tuple)

    with pytest.raises(AttributeError):
        knowledge.evidence_ids += ("O002",)


# ==============================================================================
# Evidence
# ==============================================================================


def test_has_evidence():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        evidence_ids=("O001", "O002"),
    )

    assert knowledge.has_evidence("O001")
    assert knowledge.has_evidence("O002")
    assert not knowledge.has_evidence("O999")


def test_with_evidence_returns_new_knowledge():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        evidence_ids=("O001",),
    )

    updated = knowledge.with_evidence("O002")

    assert knowledge.evidence_ids == ("O001",)
    assert updated.evidence_ids == ("O001", "O002")
    assert updated.id == knowledge.id
    assert updated.statement == knowledge.statement
    assert updated.status is knowledge.status


def test_with_existing_evidence_returns_same_knowledge():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        evidence_ids=("O001",),
    )

    result = knowledge.with_evidence("O001")

    assert result is knowledge


def test_with_empty_evidence_is_rejected():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
    )

    with pytest.raises(InvalidKnowledgeError):
        knowledge.with_evidence("")


# ==============================================================================
# Status
# ==============================================================================


def test_knowledge_status_values():
    assert KnowledgeStatus.PROVISIONAL.value == "provisional"
    assert KnowledgeStatus.VALIDATED.value == "validated"
    assert KnowledgeStatus.REFUTED.value == "refuted"


def test_status_can_be_explicitly_set():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        status=KnowledgeStatus.VALIDATED,
    )

    assert knowledge.status is KnowledgeStatus.VALIDATED


def test_refuted_knowledge_is_not_validated():
    knowledge = Knowledge(
        id="K001",
        statement="A scientific statement.",
        status=KnowledgeStatus.REFUTED,
    )

    assert knowledge.status is KnowledgeStatus.REFUTED
    assert knowledge.status is not KnowledgeStatus.VALIDATED


# ==============================================================================
# Error hierarchy
# ==============================================================================


def test_invalid_knowledge_error_is_knowledge_error():
    assert issubclass(InvalidKnowledgeError, KnowledgeError)


def test_knowledge_error_is_runtime_error():
    assert issubclass(KnowledgeError, RuntimeError)