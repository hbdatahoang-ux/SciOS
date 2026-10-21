# ==============================================================================
# SciOS Runtime Science
# Evaluation Models
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


class EvaluationError(RuntimeError):
    """Base exception for evaluation model failures."""


class InvalidEvaluationError(EvaluationError, ValueError):
    """Raised when an evaluation result is invalid."""


# ==============================================================================
# Evaluation Outcome
# ==============================================================================


class EvaluationOutcome(str, Enum):
    """
    Scientific outcome produced by evaluating an observation
    against a hypothesis.
    """

    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    SURPRISE = "surprise"


# ==============================================================================
# Evaluation Result
# ==============================================================================


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """
    Immutable result of evaluating an observation against a hypothesis.

    EvaluationResult contains interpretation of an observation, but does not
    mutate or own the underlying Hypothesis or Observation.

    Semantic boundary:

        Observation = what the world returned
        EvaluationResult = how that observation relates to the hypothesis
        Knowledge = scientific claim derived from validated evidence
    """

    hypothesis_id: str
    observation_id: str
    outcome: EvaluationOutcome
    score: float
    reason: str
    created_at: datetime
    metadata: Mapping[str, Any]

    def __init__(
        self,
        hypothesis_id: str,
        observation_id: str,
        outcome: EvaluationOutcome,
        score: float,
        reason: str,
        created_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        # ------------------------------------------------------------------
        # Hypothesis ID
        # ------------------------------------------------------------------

        if (
            not isinstance(hypothesis_id, str)
            or not hypothesis_id.strip()
        ):
            raise InvalidEvaluationError(
                "hypothesis_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Observation ID
        # ------------------------------------------------------------------

        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
        ):
            raise InvalidEvaluationError(
                "observation_id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Outcome
        # ------------------------------------------------------------------

        if not isinstance(outcome, EvaluationOutcome):
            raise InvalidEvaluationError(
                "outcome must be an EvaluationOutcome"
            )

        # ------------------------------------------------------------------
        # Score
        # ------------------------------------------------------------------

        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise InvalidEvaluationError(
                "score must be numeric"
            )

        if not 0.0 <= float(score) <= 1.0:
            raise InvalidEvaluationError(
                "score must be between 0.0 and 1.0"
            )

        # ------------------------------------------------------------------
        # Reason
        # ------------------------------------------------------------------

        if not isinstance(reason, str) or not reason.strip():
            raise InvalidEvaluationError(
                "reason must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if not isinstance(created_at, datetime):
            raise InvalidEvaluationError(
                "created_at must be a datetime"
            )

        if created_at.tzinfo is None:
            raise InvalidEvaluationError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidEvaluationError(
                "metadata must be a mapping"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(
            self,
            "hypothesis_id",
            hypothesis_id,
        )
        object.__setattr__(
            self,
            "observation_id",
            observation_id,
        )
        object.__setattr__(
            self,
            "outcome",
            outcome,
        )
        object.__setattr__(
            self,
            "score",
            float(score),
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "created_at",
            created_at,
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    # ==========================================================================
    # Query API
    # ==========================================================================

    @property
    def is_positive(self) -> bool:
        """
        Return True when the hypothesis is confirmed.
        """

        return self.outcome is EvaluationOutcome.CONFIRMED

    @property
    def is_negative(self) -> bool:
        """
        Return True when the hypothesis is refuted.
        """

        return self.outcome is EvaluationOutcome.REFUTED

    @property
    def is_conclusive(self) -> bool:
        """
        Return True when the evaluation produced a confirmed or refuted
        outcome.
        """

        return self.outcome in (
            EvaluationOutcome.CONFIRMED,
            EvaluationOutcome.REFUTED,
        )

    @property
    def is_surprise(self) -> bool:
        """
        Return True when the observation represents a surprising outcome.
        """

        return self.outcome is EvaluationOutcome.SURPRISE