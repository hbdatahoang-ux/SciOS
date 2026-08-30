"""
MCTE v0.1
=========

Environment and host state semantics, validation, and state primitives.

Environment state E(t):
    - drug_pressure
    - acidity_stress
    - host_support

Host state H(t):
    - inflammation
    - immune_competence

This module is intentionally limited to state representation and
validation. It does not implement fitness, dynamics, control, or
simulation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np


__all__ = [
    "EnvironmentState",
    "HostState",
]


# =============================================================================
# Constants
# =============================================================================

ENVIRONMENT_DIMENSION: Final[int] = 3
HOST_DIMENSION: Final[int] = 2


# =============================================================================
# Environment State
# =============================================================================


@dataclass(frozen=True)
class EnvironmentState:
    """
    Immutable environment state vector E(t).

    Parameters
    ----------
    drug_pressure:
        d(t) >= 0.
        Represents therapeutic drug pressure.

    acidity_stress:
        a(t) >= 0.
        Represents extracellular acidity / metabolic stress proxy.

    host_support:
        q(t) in [0, 1].
        Represents tissue structural constraint or host-support condition.

    Notes
    -----
    This class contains only the environment state semantics.
    It does not define how the environment evolves through time.
    """

    drug_pressure: float
    acidity_stress: float
    host_support: float

    def __post_init__(self) -> None:
        drug = float(self.drug_pressure)
        stress = float(self.acidity_stress)
        support = float(self.host_support)

        values = np.array(
            [drug, stress, support],
            dtype=float,
        )

        if not np.all(np.isfinite(values)):
            raise ValueError(
                "Environment state values must be finite."
            )

        if drug < 0.0:
            raise ValueError(
                f"Drug pressure must be >= 0, got {drug}"
            )

        if stress < 0.0:
            raise ValueError(
                f"Acidity stress must be >= 0, got {stress}"
            )

        if not 0.0 <= support <= 1.0:
            raise ValueError(
                f"Host support must be within [0, 1], got {support}"
            )

        # Normalize scalar types so numpy scalar inputs do not leak
        # through the public state API.
        object.__setattr__(self, "drug_pressure", drug)
        object.__setattr__(self, "acidity_stress", stress)
        object.__setattr__(self, "host_support", support)

    @classmethod
    def default(cls) -> "EnvironmentState":
        """
        Return the canonical MCTE v0.1 default environment state.
        """
        return cls(
            drug_pressure=0.0,
            acidity_stress=0.1,
            host_support=0.9,
        )

    def to_array(self) -> np.ndarray:
        """
        Return the environment state as a new NumPy array.

        Returns
        -------
        np.ndarray
            Array with shape ``(3,)`` ordered as:

            [drug_pressure, acidity_stress, host_support]

        Notes
        -----
        A fresh array is returned so callers cannot mutate the immutable
        dataclass state through a returned array reference.
        """
        return np.array(
            [
                self.drug_pressure,
                self.acidity_stress,
                self.host_support,
            ],
            dtype=float,
        )


# =============================================================================
# Host State
# =============================================================================


@dataclass(frozen=True)
class HostState:
    """
    Immutable host macro-state H(t).

    Parameters
    ----------
    inflammation:
        Systemic inflammatory state proxy in [0, 1].

    immune_competence:
        Host immune surveillance capacity proxy in [0, 1].

    Notes
    -----
    These are deliberately abstract v0.1 state variables.
    They are not claims that these two variables fully represent host
    physiology or cancer biology.
    """

    inflammation: float
    immune_competence: float

    def __post_init__(self) -> None:
        inflammation = float(self.inflammation)
        immune = float(self.immune_competence)

        values = np.array(
            [inflammation, immune],
            dtype=float,
        )

        if not np.all(np.isfinite(values)):
            raise ValueError(
                "Host state values must be finite."
            )

        if not 0.0 <= inflammation <= 1.0:
            raise ValueError(
                f"Inflammation must be within [0, 1], got {inflammation}"
            )

        if not 0.0 <= immune <= 1.0:
            raise ValueError(
                "Immune competence must be within [0, 1], "
                f"got {immune}"
            )

        object.__setattr__(
            self,
            "inflammation",
            inflammation,
        )
        object.__setattr__(
            self,
            "immune_competence",
            immune,
        )

    @classmethod
    def default(cls) -> "HostState":
        """
        Return the canonical MCTE v0.1 default host state.
        """
        return cls(
            inflammation=0.1,
            immune_competence=0.8,
        )

    def to_array(self) -> np.ndarray:
        """
        Return the host state as a new NumPy array.

        Returns
        -------
        np.ndarray
            Array with shape ``(2,)`` ordered as:

            [inflammation, immune_competence]
        """
        return np.array(
            [
                self.inflammation,
                self.immune_competence,
            ],
            dtype=float,
        )