# ==============================================================================
# SciOS Runtime Science
# Knowledge Models
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ==============================================================================
# Exceptions
# ==============================================================================


class KnowledgeError(RuntimeError):
    """Base exception for knowledge model failures."""


class InvalidKnowledgeError(KnowledgeError, ValueError):
    """Raised when a knowledge record is invalid."""


# ==============================================================================
# Knowledge Status
# ==============================================================================


class KnowledgeStatus(str, Enum):
    """
    Lifecycle status of a scientific knowledge claim.
    """

    PROVISIONAL = "provisional"
    VALIDATED = "validated"
    REFUTED = "refuted"


# ==============================================================================
# Knowledge Model
# ==============================================================================


@dataclass(frozen=True, slots=True)
class Knowledge:
    """
    Immutable scientific knowledge claim.

    Knowledge represents a scientific statement supported by evidence.

    Important semantic boundary:

        SURPRISE != KNOWLEDGE

    A surprising observation is evidence that may motivate a new claim.
    It is not automatically promoted to knowledge.
    """

    id: str
    statement: str
    evidence_ids: tuple[str, ...]
    status: KnowledgeStatus
    created_at: datetime

    def __init__(
        self,
        id: str,
        statement: str,
        evidence_ids: tuple[str, ...] | list[str] | None = None,
        status: KnowledgeStatus = KnowledgeStatus.PROVISIONAL,
        created_at: datetime | None = None,
    ) -> None:
        # ------------------------------------------------------------------
        # ID
        # ------------------------------------------------------------------

        if not isinstance(id, str) or not id.strip():
            raise InvalidKnowledgeError(
                "id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Statement
        # ------------------------------------------------------------------

        if not isinstance(statement, str) or not statement.strip():
            raise InvalidKnowledgeError(
                "statement must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Evidence
        # ------------------------------------------------------------------

        if evidence_ids is None:
            evidence_ids = ()

        try:
            normalized_evidence_ids = tuple(evidence_ids)
        except TypeError as exc:
            raise InvalidKnowledgeError(
                "evidence_ids must be an iterable of strings"
            ) from exc

        if any(
            not isinstance(evidence_id, str) or not evidence_id.strip()
            for evidence_id in normalized_evidence_ids
        ):
            raise InvalidKnowledgeError(
                "evidence_ids must contain non-empty strings"
            )

        if len(normalized_evidence_ids) != len(
            set(normalized_evidence_ids)
        ):
            raise InvalidKnowledgeError(
                "evidence_ids must not contain duplicates"
            )

        # ------------------------------------------------------------------
        # Status
        # ------------------------------------------------------------------

        if not isinstance(status, KnowledgeStatus):
            raise InvalidKnowledgeError(
                "status must be a KnowledgeStatus"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if not isinstance(created_at, datetime):
            raise InvalidKnowledgeError(
                "created_at must be a datetime"
            )

        if created_at.tzinfo is None:
            raise InvalidKnowledgeError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "statement", statement)
        object.__setattr__(
            self,
            "evidence_ids",
            normalized_evidence_ids,
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "created_at", created_at)

    # ==========================================================================
    # Evidence API
    # ==========================================================================

    def has_evidence(self, evidence_id: str) -> bool:
        """
        Return True if evidence_id directly supports this knowledge claim.
        """

        return evidence_id in self.evidence_ids

    def with_evidence(self, evidence_id: str) -> Knowledge:
        """
        Return a new Knowledge record with additional evidence.

        If the evidence already exists, return this record unchanged.
        """

        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise InvalidKnowledgeError(
                "evidence_id must be a non-empty string"
            )

        if evidence_id in self.evidence_ids:
            return self

        return Knowledge(
            id=self.id,
            statement=self.statement,
            evidence_ids=self.evidence_ids + (evidence_id,),
            status=self.status,
            created_at=self.created_at,
        )