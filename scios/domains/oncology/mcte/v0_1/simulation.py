from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from scios.domains.oncology.mcte.v0_1.control import (
    ControlPolicy,
)
from scios.domains.oncology.mcte.v0_1.dynamics import (
    compute_system_derivatives,
)
from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)
from scios.domains.oncology.mcte.v0_1.fitness import (
    FitnessModel,
)
from scios.domains.oncology.mcte.v0_1.objective import (
    EvaluationMetrics,
    compute_step_metrics,
)
from scios.domains.oncology.mcte.v0_1.state import (
    STATE_DIMENSION,
    PhenotypeState,
)


__all__ = [
    "SimulationResult",
    "SimulationEngine",
]


@dataclass(frozen=True)
class SimulationResult:
    """
    Immutable result container for an MCTE v0.1 simulation.

    The trajectory contains phenotype fractions at each
    requested time point.

    All histories are aligned with the times array.
    """

    times: np.ndarray
    trajectory: np.ndarray
    drug_pressures: np.ndarray
    acidity_stresses: np.ndarray
    host_supports: np.ndarray
    metrics_history: list[EvaluationMetrics]

    def __post_init__(self) -> None:
        times = np.asarray(self.times, dtype=float)
        trajectory = np.asarray(self.trajectory, dtype=float)
        drug_pressures = np.asarray(
            self.drug_pressures,
            dtype=float,
        )
        acidity_stresses = np.asarray(
            self.acidity_stresses,
            dtype=float,
        )
        host_supports = np.asarray(
            self.host_supports,
            dtype=float,
        )

        if times.ndim != 1:
            raise ValueError(
                "times must be a 1D array."
            )

        if trajectory.ndim != 2:
            raise ValueError(
                "trajectory must be a 2D array."
            )

        if trajectory.shape[1] != STATE_DIMENSION:
            raise ValueError(
                "trajectory must have "
                f"{STATE_DIMENSION} phenotype columns."
            )

        n = len(times)

        if trajectory.shape[0] != n:
            raise ValueError(
                "trajectory length must match times length."
            )

        if len(drug_pressures) != n:
            raise ValueError(
                "drug_pressures length must match times length."
            )

        if len(acidity_stresses) != n:
            raise ValueError(
                "acidity_stresses length must match times length."
            )

        if len(host_supports) != n:
            raise ValueError(
                "host_supports length must match times length."
            )

        if len(self.metrics_history) != n:
            raise ValueError(
                "metrics_history length must match times length."
            )

        if not np.all(np.isfinite(times)):
            raise ValueError(
                "times must contain only finite values."
            )

        if not np.all(np.isfinite(trajectory)):
            raise ValueError(
                "trajectory must contain only finite values."
            )

        if not np.all(np.isfinite(drug_pressures)):
            raise ValueError(
                "drug_pressures must contain only finite values."
            )

        if not np.all(np.isfinite(acidity_stresses)):
            raise ValueError(
                "acidity_stresses must contain only finite values."
            )

        if not np.all(np.isfinite(host_supports)):
            raise ValueError(
                "host_supports must contain only finite values."
            )

        object.__setattr__(
            self,
            "times",
            times,
        )
        object.__setattr__(
            self,
            "trajectory",
            trajectory,
        )
        object.__setattr__(
            self,
            "drug_pressures",
            drug_pressures,
        )
        object.__setattr__(
            self,
            "acidity_stresses",
            acidity_stresses,
        )
        object.__setattr__(
            self,
            "host_supports",
            host_supports,
        )


class SimulationEngine:
    """
    MCTE v0.1 time-stepping simulation engine.

    Causal order at each time t:

        1. Observe x(t), E(t), H(t), t.
        2. Compute fitness F(t).
        3. Compute dx/dt.
        4. Advance phenotype state.
        5. Compute control action.
        6. Update environment.
        7. Record metrics.

    Objective evaluation is observation-only and does not feed
    back into the dynamics.
    """

    def __init__(
        self,
        fitness_model: FitnessModel,
        control_policy: ControlPolicy,
        transition_matrix: np.ndarray | None = None,
        env_relaxation_rate: float = 0.5,
    ) -> None:
        self.fitness_model = fitness_model
        self.control_policy = control_policy

        if transition_matrix is not None:
            matrix = np.asarray(
                transition_matrix,
                dtype=float,
            )

            if matrix.shape != (
                STATE_DIMENSION,
                STATE_DIMENSION,
            ):
                raise ValueError(
                    "Transition matrix must have shape "
                    f"({STATE_DIMENSION}, {STATE_DIMENSION})."
                )

            if not np.all(np.isfinite(matrix)):
                raise ValueError(
                    "Transition matrix values must be finite."
                )

            if np.any(matrix < 0.0):
                raise ValueError(
                    "Transition rates must be non-negative."
                )

            matrix = matrix.copy()
            matrix.setflags(write=False)

            self.transition_matrix = matrix
        else:
            self.transition_matrix = None

        rate = float(env_relaxation_rate)

        if not np.isfinite(rate):
            raise ValueError(
                "Environment relaxation rate must be finite."
            )

        if rate < 0.0:
            raise ValueError(
                "Environment relaxation rate must be >= 0."
            )

        self.env_relaxation_rate = rate

    def run(
        self,
        initial_state: PhenotypeState,
        initial_env: EnvironmentState,
        initial_host: HostState,
        times: Sequence[float],
    ) -> SimulationResult:
        """
        Execute the simulation over the supplied time points.
        """

        t_arr = np.asarray(
            times,
            dtype=float,
        )

        if t_arr.ndim != 1:
            raise ValueError(
                "Times must be a 1D array."
            )

        if len(t_arr) < 2:
            raise ValueError(
                "Times must contain at least 2 points."
            )

        if not np.all(np.isfinite(t_arr)):
            raise ValueError(
                "Times must contain only finite values."
            )

        if not np.all(np.diff(t_arr) > 0.0):
            raise ValueError(
                "Time points must be strictly increasing."
            )

        num_steps = len(t_arr)

        trajectory = np.zeros(
            (num_steps, STATE_DIMENSION),
            dtype=float,
        )

        drug_history = np.zeros(
            num_steps,
            dtype=float,
        )

        acidity_history = np.zeros(
            num_steps,
            dtype=float,
        )

        host_support_history = np.zeros(
            num_steps,
            dtype=float,
        )

        metrics_history: list[EvaluationMetrics] = []

        current_state = initial_state
        current_env = initial_env
        current_host = initial_host

        for idx, t in enumerate(t_arr):

            trajectory[idx] = (
                current_state.fractions
            )

            drug_history[idx] = (
                current_env.drug_pressure
            )

            acidity_history[idx] = (
                current_env.acidity_stress
            )

            host_support_history[idx] = (
                current_env.host_support
            )

            metrics = compute_step_metrics(
                current_state,
                current_env,
            )

            metrics_history.append(metrics)

            if idx == num_steps - 1:
                break

            dt = (
                t_arr[idx + 1]
                - t
            )

            fitness = (
                self.fitness_model.compute_fitness(
                    current_state,
                    current_env,
                    current_host,
                    time=t,
                )
            )

            dx = compute_system_derivatives(
                current_state,
                fitness,
                self.transition_matrix,
            )

            raw_fractions = (
                current_state.fractions
                + dx * dt
            )

            clipped = np.clip(
                raw_fractions,
                0.0,
                1.0,
            )

            total = float(
                np.sum(clipped)
            )

            if total <= 0.0:
                raise RuntimeError(
                    "Numerical integration collapsed: "
                    "all phenotype fractions reached zero."
                )

            normalized_fractions = (
                clipped / total
            )

            current_state = PhenotypeState(
                fractions=normalized_fractions
            )

            intervention = (
                self.control_policy.compute_action(
                    current_state,
                    current_env,
                    current_host,
                    time=t,
                )
            )

            alpha = (
                self.env_relaxation_rate
                * dt
            )

            alpha = min(
                max(alpha, 0.0),
                1.0,
            )

            new_drug = (
                current_env.drug_pressure
                + alpha
                * (
                    intervention.target_drug_pressure
                    - current_env.drug_pressure
                )
            )

            new_stress = (
                current_env.acidity_stress
                + alpha
                * (
                    intervention.target_acidity_stress
                    - current_env.acidity_stress
                )
            )

            current_env = EnvironmentState(
                drug_pressure=new_drug,
                acidity_stress=new_stress,
                host_support=current_env.host_support,
            )

        return SimulationResult(
            times=t_arr.copy(),
            trajectory=trajectory,
            drug_pressures=drug_history,
            acidity_stresses=acidity_history,
            host_supports=host_support_history,
            metrics_history=metrics_history,
        )