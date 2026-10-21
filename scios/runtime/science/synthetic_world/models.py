# ==============================================================================
# SciOS Runtime Science
# Synthetic World Models
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


# ==============================================================================
# Exceptions
# ==============================================================================


class SyntheticWorldError(RuntimeError):
    """Base exception for synthetic world failures."""


class InvalidSyntheticWorldError(
    SyntheticWorldError,
    ValueError,
):
    """Raised when a synthetic world model is invalid."""


# ==============================================================================
# World State
# ==============================================================================


@dataclass(frozen=True, slots=True)
class WorldState:
    """
    Immutable snapshot of the synthetic world's state.

    WorldState describes the state of the world at a specific point in time.

    Semantic boundary:

        WorldState != Observation
        WorldState != Outcome
        WorldState != Knowledge

    The state contains only world variables and their timestamp.
    """

    values: Mapping[str, Any]
    timestamp: datetime

    def __init__(
        self,
        values: Mapping[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        # ------------------------------------------------------------------
        # Values
        # ------------------------------------------------------------------

        if values is None:
            values = {}

        if not isinstance(values, Mapping):
            raise InvalidSyntheticWorldError(
                "values must be a mapping"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if not isinstance(timestamp, datetime):
            raise InvalidSyntheticWorldError(
                "timestamp must be a datetime"
            )

        if timestamp.tzinfo is None:
            raise InvalidSyntheticWorldError(
                "timestamp must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(
            self,
            "values",
            MappingProxyType(dict(values)),
        )

        object.__setattr__(
            self,
            "timestamp",
            timestamp,
        )

    # ==========================================================================
    # Query API
    # ==========================================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a state value by key.
        """

        return self.values.get(key, default)


# ==============================================================================
# World Result
# ==============================================================================


@dataclass(frozen=True, slots=True)
class WorldResult:
    """
    Immutable result produced by a synthetic-world execution.

    WorldResult contains raw computational output from the synthetic world
    together with the resulting world state.

    It deliberately does not contain:

        - scientific Outcome
        - Surprise classification
        - Knowledge claim
        - AI interpretation

    Those belong to higher scientific-analysis layers.
    """

    values: Mapping[str, Any]
    state: WorldState

    def __init__(
        self,
        values: Mapping[str, Any],
        state: WorldState,
    ) -> None:
        # ------------------------------------------------------------------
        # Values
        # ------------------------------------------------------------------

        if not isinstance(values, Mapping):
            raise InvalidSyntheticWorldError(
                "values must be a mapping"
            )

        # ------------------------------------------------------------------
        # State
        # ------------------------------------------------------------------

        if not isinstance(state, WorldState):
            raise InvalidSyntheticWorldError(
                "state must be a WorldState"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(
            self,
            "values",
            MappingProxyType(dict(values)),
        )

        object.__setattr__(
            self,
            "state",
            state,
        )