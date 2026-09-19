# ==============================================================================
# SciOS Runtime Science
# Hypothesis Models
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


# ==============================================================================
# Exceptions
# ==============================================================================


class HypothesisError(RuntimeError):
    """Base exception for hypothesis model failures."""


class InvalidHypothesisError(HypothesisError, ValueError):
    """Raised when a hypothesis model is invalid."""


# ==============================================================================
# Hypothesis Status
# ==============================================================================


class HypothesisStatus(str, Enum):
    """Lifecycle status of a scientific hypothesis."""

    PROPOSED = "proposed"
    TESTED = "tested"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    SURPRISE = "surprise"


# ==============================================================================
# Hypothesis
# ==============================================================================


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """
    Immutable scientific hypothesis.

    A Hypothesis is a testable scientific claim.

    Important semantic boundaries:

        Hypothesis != Knowledge
        Observation != Evaluation
        SURPRISE != KNOWLEDGE

    A hypothesis may eventually contribute evidence toward a knowledge claim,
    but it is not knowledge merely because it exists or is supported once.
    """

    id: str
    statement: str
    status: HypothesisStatus
    created_at: datetime
    metadata: Mapping[str, Any]

    def __init__(
        self,
        id: str,
        statement: str,
        status: HypothesisStatus = HypothesisStatus.PROPOSED,
        created_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        # ------------------------------------------------------------------
        # ID
        # ------------------------------------------------------------------

        if not isinstance(id, str) or not id.strip():
            raise InvalidHypothesisError(
                "id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Statement
        # ------------------------------------------------------------------

        if not isinstance(statement, str) or not statement.strip():
            raise InvalidHypothesisError(
                "statement must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Status
        # ------------------------------------------------------------------

        if not isinstance(status, HypothesisStatus):
            raise InvalidHypothesisError(
                "status must be a HypothesisStatus"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if not isinstance(created_at, datetime):
            raise InvalidHypothesisError(
                "created_at must be a datetime"
            )

        if created_at.tzinfo is None:
            raise InvalidHypothesisError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidHypothesisError(
                "metadata must be a mapping"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "statement", statement)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    # ==========================================================================
    # Status API
    # ==========================================================================

    def is_terminal(self) -> bool:
        """
        Return True if the hypothesis has reached a terminal outcome.
        """

        return self.status in {
            HypothesisStatus.SUPPORTED,
            HypothesisStatus.REFUTED,
            HypothesisStatus.INCONCLUSIVE,
            HypothesisStatus.SURPRISE,
        }

    # ==========================================================================
    # Functional update API
    # ==========================================================================

    def with_status(
        self,
        status: HypothesisStatus,
    ) -> Hypothesis:
        """
        Return a new hypothesis with the supplied status.

        If the status is unchanged, return this record unchanged.
        """

        if not isinstance(status, HypothesisStatus):
            raise InvalidHypothesisError(
                "status must be a HypothesisStatus"
            )

        if status is self.status:
            return self

        return Hypothesis(
            id=self.id,
            statement=self.statement,
            status=status,
            created_at=self.created_at,
            metadata=self.metadata,
        )