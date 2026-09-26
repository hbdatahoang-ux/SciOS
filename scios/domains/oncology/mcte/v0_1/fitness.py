"""
MCTE v0.1
=========

Fitness interface and minimal toy fitness implementation.

Defines the mapping:

    F_i = F_i(x, E, H, t)

The v0.1 toy model is intentionally frequency-independent:
fitness depends on environment and host state, but not on phenotype
frequencies x.

This module does not implement:
    - phenotype dynamics
    - numerical integration
    - therapeutic control
    - objective evaluation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

import numpy as np

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)
from scios.domains.oncology.mcte.v0_1.state import (
    PHENOTYPES,
    STATE_DIMENSION,
    PhenotypeState,
)


__all__ = [
    "FitnessModel",
    "BaseFitnessModel",
    "ToyLinearFitnessModel",
]


# =============================================================================
# Fitness interface
# =============================================================================


@runtime_checkable
class FitnessModel(Protocol):
    """
    Protocol defining the MCTE fitness-model interface.
    """

    def compute_fitness(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> np.ndarray:
        """
        Compute fitness F for all phenotypes.

        Parameters
        ----------
        state:
            Current phenotype state x(t).

        env:
            Current environment state E(t).

        host:
            Current host state H(t).

        time:
            Current simulation time t.

        Returns
        -------
        np.ndarray
            Fitness vector of shape (STATE_DIMENSION,).
        """
        ...


# =============================================================================
# Abstract base
# =============================================================================


class BaseFitnessModel(ABC):
    """
    Abstract base class for MCTE fitness models.
    """

    @abstractmethod
    def compute_fitness(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> np.ndarray:
        """
        Compute phenotype fitness vector.
        """
        raise NotImplementedError


# =============================================================================
# Minimal v0.1 toy model
# =============================================================================


class ToyLinearFitnessModel(BaseFitnessModel):
    """
    Minimal frequency-independent linear fitness model.

    Phenotype order
    ---------------
    S : Sensitive
    R : Resistant
    I : Invasive
    D : Differentiated / less malignant

    Model
    -----
    F_S = b_S - c_S * d

    F_R = b_R - c_R * d

    F_I = b_I + c_I * a - c_Q * q - c_H * immune

    F_D = b_D + c_D * q

    where:

        d      = drug pressure
        a      = acidity / environmental stress
        q      = host support
        immune  = host immune competence

    The phenotype fractions x do NOT appear in these equations.
    Therefore the v0.1 model is frequency-independent.

    Notes
    -----
    This is deliberately a toy computational model. Its coefficients
    encode modeling assumptions and are not experimentally validated
    biological parameters.
    """

    def __init__(
        self,
        base_fitness: np.ndarray | None = None,
        drug_penalty_s: float = 2.0,
        drug_penalty_r: float = 0.1,
        stress_benefit_i: float = 1.0,
        host_support_benefit_d: float = 1.5,
        host_support_penalty_i: float = 0.5,
        immune_penalty_i: float = 0.3,
    ) -> None:
        if base_fitness is None:
            base = np.array(
                [1.0, 0.8, 0.9, 0.7],
                dtype=float,
            )
        else:
            base = np.asarray(
                base_fitness,
                dtype=float,
            )

        if base.shape != (STATE_DIMENSION,):
            raise ValueError(
                f"Base fitness must have shape "
                f"({STATE_DIMENSION},), got {base.shape}"
            )

        if not np.all(np.isfinite(base)):
            raise ValueError(
                "Base fitness values must be finite."
            )

        if np.any(base < 0.0):
            raise ValueError(
                "Base fitness values must be >= 0."
            )

        coefficients = {
            "drug_penalty_s": drug_penalty_s,
            "drug_penalty_r": drug_penalty_r,
            "stress_benefit_i": stress_benefit_i,
            "host_support_benefit_d": host_support_benefit_d,
            "host_support_penalty_i": host_support_penalty_i,
            "immune_penalty_i": immune_penalty_i,
        }

        for name, value in coefficients.items():
            value = float(value)

            if not np.isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if value < 0.0:
                raise ValueError(
                    f"{name} must be >= 0, got {value}"
                )

            coefficients[name] = value

        # Store a private immutable copy.
        self.base_fitness = base.copy()
        self.base_fitness.setflags(write=False)

        self.drug_penalty_s = coefficients["drug_penalty_s"]
        self.drug_penalty_r = coefficients["drug_penalty_r"]
        self.stress_benefit_i = coefficients["stress_benefit_i"]
        self.host_support_benefit_d = (
            coefficients["host_support_benefit_d"]
        )
        self.host_support_penalty_i = (
            coefficients["host_support_penalty_i"]
        )
        self.immune_penalty_i = (
            coefficients["immune_penalty_i"]
        )

    def compute_fitness(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> np.ndarray:
        """
        Compute the v0.1 fitness vector.

        The state argument is intentionally accepted as part of the
        general interface but phenotype frequencies are not used by
        this toy model.
        """
        t = float(time)

        if not np.isfinite(t):
            raise ValueError(
                "Time must be finite."
            )

        # Explicitly access the state to validate that the expected
        # state object reaches this model without introducing any
        # frequency-dependent term.
        if not isinstance(state, PhenotypeState):
            raise TypeError(
                "state must be a PhenotypeState."
            )

        d = env.drug_pressure
        a = env.acidity_stress
        q = env.host_support
        immune = host.immune_competence

        f = self.base_fitness.copy()

        # -----------------------------------------------------------------
        # S: drug-sensitive phenotype
        # -----------------------------------------------------------------
        f[0] -= self.drug_penalty_s * d

        # -----------------------------------------------------------------
        # R: resistant phenotype
        # -----------------------------------------------------------------
        f[1] -= self.drug_penalty_r * d

        # -----------------------------------------------------------------
        # I: invasive phenotype
        # -----------------------------------------------------------------
        f[2] += self.stress_benefit_i * a
        f[2] -= self.host_support_penalty_i * q
        f[2] -= self.immune_penalty_i * immune

        # -----------------------------------------------------------------
        # D: differentiated phenotype
        # -----------------------------------------------------------------
        f[3] += self.host_support_benefit_d * q

        return f