"""
MCTE v0.1
=========

Therapeutic control and policy interface.

Defines how interventions are generated from the current:
    x(t), E(t), H(t), t

The control layer only proposes intervention targets.

It does not:
- mutate phenotype state,
- mutate environment state,
- run simulation loops,
- compute fitness,
- evaluate objectives.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)
from scios.domains.oncology.mcte.v0_1.state import (
    PhenotypeState,
)


__all__ = [
    "Intervention",
    "ControlPolicy",
    "BaseControlPolicy",
    "ConstantControlPolicy",
    "MetronomicControlPolicy",
]


@dataclass(frozen=True)
class Intervention:
    """
    Immutable intervention target.

    The values represent desired environmental targets.

    Attributes
    ----------
    target_drug_pressure:
        Desired drug-pressure target. Must be >= 0.

    target_acidity_stress:
        Desired acidity/stress target. Must be >= 0.

    Notes
    -----
    Intervention is a target description only.

    It is NOT:
    - a derivative,
    - a state update,
    - a mutation of EnvironmentState.
    """

    target_drug_pressure: float
    target_acidity_stress: float

    def __post_init__(self) -> None:
        drug = float(self.target_drug_pressure)
        stress = float(self.target_acidity_stress)

        if not np.isfinite(drug):
            raise ValueError(
                "Target drug pressure must be finite."
            )

        if not np.isfinite(stress):
            raise ValueError(
                "Target acidity stress must be finite."
            )

        if drug < 0.0:
            raise ValueError(
                "Target drug pressure must be >= 0."
            )

        if stress < 0.0:
            raise ValueError(
                "Target acidity stress must be >= 0."
            )

        object.__setattr__(
            self,
            "target_drug_pressure",
            drug,
        )

        object.__setattr__(
            self,
            "target_acidity_stress",
            stress,
        )


@runtime_checkable
class ControlPolicy(Protocol):
    """
    Protocol defining the control-policy interface.
    """

    def compute_action(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> Intervention:
        """
        Compute an intervention target from the current system state.
        """
        ...


class BaseControlPolicy(ABC):
    """
    Abstract base class for MCTE control policies.
    """

    @abstractmethod
    def compute_action(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> Intervention:
        """
        Compute an intervention target.
        """
        raise NotImplementedError


class ConstantControlPolicy(BaseControlPolicy):
    """
    Baseline policy applying a constant intervention target.

    The returned Intervention is immutable and is not applied
    directly to the environment.
    """

    def __init__(
        self,
        drug_pressure: float = 1.0,
        acidity_stress: float = 0.1,
    ) -> None:
        self._intervention = Intervention(
            target_drug_pressure=drug_pressure,
            target_acidity_stress=acidity_stress,
        )

    @property
    def intervention(self) -> Intervention:
        """
        Return the immutable configured intervention.
        """
        return self._intervention

    def compute_action(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> Intervention:
        """
        Return the configured constant intervention.
        """

        t = float(time)

        if not np.isfinite(t):
            raise ValueError(
                "Time must be finite."
            )

        return self._intervention


class MetronomicControlPolicy(BaseControlPolicy):
    """
    Periodic metronomic drug-pressure policy.

    Drug pressure is active during the duty-cycle portion
    of each period.

    Example
    -------
    period = 10
    duty_cycle = 0.5

    Drug is active during:

        [0, 5)

    and inactive during:

        [5, 10)

    The cycle repeats periodically.
    """

    def __init__(
        self,
        peak_drug_pressure: float = 1.5,
        period: float = 10.0,
        duty_cycle: float = 0.5,
    ) -> None:
        peak = float(peak_drug_pressure)
        period_value = float(period)
        duty = float(duty_cycle)

        if not np.isfinite(peak):
            raise ValueError(
                "Peak drug pressure must be finite."
            )

        if not np.isfinite(period_value):
            raise ValueError(
                "Period must be finite."
            )

        if not np.isfinite(duty):
            raise ValueError(
                "Duty cycle must be finite."
            )

        if peak < 0.0:
            raise ValueError(
                "Peak drug pressure must be >= 0."
            )

        if period_value <= 0.0:
            raise ValueError(
                "Period must be > 0."
            )

        if not 0.0 <= duty <= 1.0:
            raise ValueError(
                "Duty cycle must be within [0, 1]."
            )

        self._peak_drug_pressure = peak
        self._period = period_value
        self._duty_cycle = duty

    @property
    def peak_drug_pressure(self) -> float:
        return self._peak_drug_pressure

    @property
    def period(self) -> float:
        return self._period

    @property
    def duty_cycle(self) -> float:
        return self._duty_cycle

    def compute_action(
        self,
        state: PhenotypeState,
        env: EnvironmentState,
        host: HostState,
        time: float,
    ) -> Intervention:
        """
        Compute the intervention target at time t.
        """

        t = float(time)

        if not np.isfinite(t):
            raise ValueError(
                "Time must be finite."
            )

        phase = (t % self._period) / self._period

        if phase < self._duty_cycle:
            drug = self._peak_drug_pressure
        else:
            drug = 0.0

        return Intervention(
            target_drug_pressure=drug,
            target_acidity_stress=env.acidity_stress,
        )