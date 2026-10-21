# ==============================================================================
# SciOS Runtime Science
# Synthetic World Rules
# ==============================================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import Any, Mapping

from .models import (
    InvalidSyntheticWorldError,
    WorldResult,
    WorldState,
)


# ==============================================================================
# World Rule
# ==============================================================================


class WorldRule(ABC):
    """
    Deterministic rule governing synthetic-world behavior.

    A rule transforms:

        WorldState + experiment parameters
                    ↓
                WorldResult

    Rules must not classify scientific outcomes or create knowledge.
    """

    @abstractmethod
    def apply(
        self,
        state: WorldState,
        parameters: Mapping[str, Any],
    ) -> WorldResult:
        """
        Apply the rule to the current world state and parameters.
        """

        raise NotImplementedError


# ==============================================================================
# Threshold Rule
# ==============================================================================


class ThresholdRule(WorldRule):
    """
    Deterministic threshold rule.

    This is intentionally primitive. Its purpose is to validate
    the scientific loop before introducing nonlinear dynamics.
    """

    __slots__ = (
        "_parameter",
        "_threshold",
        "_output",
    )

    def __init__(
        self,
        parameter: str,
        threshold: float,
        output: str = "response",
    ) -> None:
        if not isinstance(parameter, str) or not parameter.strip():
            raise InvalidSyntheticWorldError(
                "parameter must be a non-empty string"
            )

        if not isinstance(threshold, (int, float)):
            raise InvalidSyntheticWorldError(
                "threshold must be numeric"
            )

        if isinstance(threshold, bool):
            raise InvalidSyntheticWorldError(
                "threshold must be numeric"
            )

        if not isinstance(output, str) or not output.strip():
            raise InvalidSyntheticWorldError(
                "output must be a non-empty string"
            )

        object.__setattr__(
            self,
            "_parameter",
            parameter,
        )

        object.__setattr__(
            self,
            "_threshold",
            threshold,
        )

        object.__setattr__(
            self,
            "_output",
            output,
        )

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def parameter(self) -> str:
        """Return the input parameter name."""

        return self._parameter

    @property
    def threshold(self) -> float:
        """Return the threshold value."""

        return self._threshold

    @property
    def output(self) -> str:
        """Return the output field name."""

        return self._output

    # ==========================================================================
    # Execution
    # ==========================================================================

    def apply(
        self,
        state: WorldState,
        parameters: Mapping[str, Any],
    ) -> WorldResult:
        """
        Apply the threshold rule.

        The rule is deterministic:

            value >= threshold → True
            value <  threshold → False
        """

        if not isinstance(state, WorldState):
            raise InvalidSyntheticWorldError(
                "state must be a WorldState"
            )

        if not isinstance(parameters, Mapping):
            raise InvalidSyntheticWorldError(
                "parameters must be a mapping"
            )

        value = parameters.get(self._parameter)

        if not isinstance(value, (int, float)):
            raise InvalidSyntheticWorldError(
                f"parameter '{self._parameter}' must be numeric"
            )

        if isinstance(value, bool):
            raise InvalidSyntheticWorldError(
                f"parameter '{self._parameter}' must be numeric"
            )

        response = value >= self._threshold

        values = MappingProxyType(
            {
                self._output: response,
                "input": value,
                "threshold": self._threshold,
            }
        )

        return WorldResult(
            values=values,
            state=state,
        )