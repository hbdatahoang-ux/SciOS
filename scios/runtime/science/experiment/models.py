# ==============================================================================
# SciOS Runtime Science
# Experiment Models
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


class ExperimentError(RuntimeError):
    """Base exception for experiment model failures."""


class InvalidExperimentError(ExperimentError, ValueError):
    """Raised when an experiment model is invalid."""


# ==============================================================================
# Outcome
# ==============================================================================


class Outcome(str, Enum):
    """Scientific outcome classification."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    SURPRISE = "surprise"


# ==============================================================================
# Experiment
# ==============================================================================


@dataclass(frozen=True, slots=True)
class Experiment:
    """
    Immutable description of a scientific experiment.

    An Experiment represents an intentional action against a synthetic
    or physical world.

    It does not contain observations or conclusions.
    """

    id: str
    hypothesis_id: str
    parameters: Mapping[str, Any]
    created_at: datetime
    metadata: Mapping[str, Any]

    def __init__(
        self,
        id: str,
        hypothesis_id: str,
        parameters: Mapping[str, Any] | None = None,
        created_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise InvalidExperimentError(
                "id must be a non-empty string"
            )

        if not isinstance(hypothesis_id, str) or not hypothesis_id.strip():
            raise InvalidExperimentError(
                "hypothesis_id must be a non-empty string"
            )

        if parameters is None:
            parameters = {}

        if not isinstance(parameters, Mapping):
            raise InvalidExperimentError(
                "parameters must be a mapping"
            )

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if not isinstance(created_at, datetime):
            raise InvalidExperimentError(
                "created_at must be a datetime"
            )

        if created_at.tzinfo is None:
            raise InvalidExperimentError(
                "created_at must be timezone-aware"
            )

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidExperimentError(
                "metadata must be a mapping"
            )

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "hypothesis_id", hypothesis_id)
        object.__setattr__(
            self,
            "parameters",
            MappingProxyType(dict(parameters)),
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    @property
    def parameter_count(self) -> int:
        """Return the number of experiment parameters."""
        return len(self.parameters)


# ==============================================================================
# Observation
# ==============================================================================


@dataclass(frozen=True, slots=True)
class Observation:
    """
    Immutable observation produced by an experiment.

    Observation represents what the world returned. It does not encode
    interpretation or scientific conclusion.
    """

    id: str
    experiment_id: str
    values: Mapping[str, Any]
    observed_at: datetime
    metadata: Mapping[str, Any]

    def __init__(
        self,
        id: str,
        experiment_id: str,
        values: Mapping[str, Any],
        observed_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise InvalidExperimentError(
                "id must be a non-empty string"
            )

        if not isinstance(experiment_id, str) or not experiment_id.strip():
            raise InvalidExperimentError(
                "experiment_id must be a non-empty string"
            )

        if not isinstance(values, Mapping):
            raise InvalidExperimentError(
                "values must be a mapping"
            )

        if observed_at is None:
            observed_at = datetime.now(timezone.utc)

        if not isinstance(observed_at, datetime):
            raise InvalidExperimentError(
                "observed_at must be a datetime"
            )

        if observed_at.tzinfo is None:
            raise InvalidExperimentError(
                "observed_at must be timezone-aware"
            )

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidExperimentError(
                "metadata must be a mapping"
            )

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "experiment_id", experiment_id)
        object.__setattr__(
            self,
            "values",
            MappingProxyType(dict(values)),
        )
        object.__setattr__(self, "observed_at", observed_at)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    @property
    def value_count(self) -> int:
        """Return the number of observed values."""
        return len(self.values)