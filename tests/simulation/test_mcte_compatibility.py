from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from scios.simulation import (
    Integrator,
    SimulationModel,
    SimulationResult as GenericSimulationResult,
    SimulationState,
)

from scios.domains.oncology.mcte.v0_1.control import (
    ConstantControlPolicy,
)
from scios.domains.oncology.mcte.v0_1.dynamics import (
    compute_system_derivatives,
)
from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)
from scios.domains.oncology.mcte.v0_1.fitness import (
    ToyLinearFitnessModel,
)
from scios.domains.oncology.mcte.v0_1.simulation import (
    SimulationEngine,
)
from scios.domains.oncology.mcte.v0_1.state import (
    PhenotypeState,
)


# ---------------------------------------------------------------------------
# Test-local compatibility boundary.
#
# These classes are deliberately NOT production adapters.
# They exist only to prove that the existing MCTE implementation can cross
# the generic simulation contracts without modifying MCTE.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MCTECompositeState:
    phenotype: PhenotypeState
    environment: EnvironmentState
    host: HostState

    def copy(self) -> "MCTECompositeState":
        return MCTECompositeState(
            phenotype=self.phenotype,
            environment=self.environment,
            host=self.host,
        )


class MCTEModelAdapter:
    """Test-local projection of the MCTE model onto SimulationModel."""

    def __init__(
        self,
        fitness_model: ToyLinearFitnessModel,
        transition_matrix: np.ndarray | None = None,
    ) -> None:
        self.fitness_model = fitness_model
        self.transition_matrix = transition_matrix

    def derivative(
        self,
        state: MCTECompositeState,
        time: float,
    ) -> np.ndarray:
        fitness = self.fitness_model.compute_fitness(
            state.phenotype,
            state.environment,
            state.host,
            time=time,
        )

        return compute_system_derivatives(
            state.phenotype,
            fitness,
            self.transition_matrix,
        )


class MCTEOneStepAdapter:
    """Test-local one-step boundary preserving current MCTE semantics."""

    def __init__(
        self,
        fitness_model: ToyLinearFitnessModel,
        control_policy: ConstantControlPolicy,
        transition_matrix: np.ndarray | None = None,
        env_relaxation_rate: float = 0.5,
    ) -> None:
        self.fitness_model = fitness_model
        self.control_policy = control_policy
        self.transition_matrix = transition_matrix
        self.env_relaxation_rate = env_relaxation_rate

    def step(
        self,
        model: SimulationModel,
        state: SimulationState,
        time: float,
        dt: float,
    ) -> SimulationState:
        current = state

        derivative = model.derivative(
            current,
            time,
        )

        raw_fractions = (
            current.phenotype.fractions
            + derivative * dt
        )

        clipped = np.clip(
            raw_fractions,
            0.0,
            1.0,
        )

        total = float(np.sum(clipped))

        if total <= 0.0:
            raise RuntimeError(
                "Numerical integration collapsed: "
                "all phenotype fractions reached zero."
            )

        normalized_fractions = clipped / total

        next_phenotype = PhenotypeState(
            fractions=normalized_fractions,
        )

        intervention = self.control_policy.compute_action(
            next_phenotype,
            current.environment,
            current.host,
            time=time,
        )

        alpha = self.env_relaxation_rate * dt
        alpha = min(max(alpha, 0.0), 1.0)

        new_drug = (
            current.environment.drug_pressure
            + alpha
            * (
                intervention.target_drug_pressure
                - current.environment.drug_pressure
            )
        )

        new_stress = (
            current.environment.acidity_stress
            + alpha
            * (
                intervention.target_acidity_stress
                - current.environment.acidity_stress
            )
        )

        next_environment = EnvironmentState(
            drug_pressure=new_drug,
            acidity_stress=new_stress,
            host_support=current.environment.host_support,
        )

        return MCTECompositeState(
            phenotype=next_phenotype,
            environment=next_environment,
            host=current.host,
        )


def make_state() -> MCTECompositeState:
    return MCTECompositeState(
        phenotype=PhenotypeState.default(),
        environment=EnvironmentState.default(),
        host=HostState.default(),
    )


def make_fitness_model() -> ToyLinearFitnessModel:
    return ToyLinearFitnessModel()


def make_control_policy() -> ConstantControlPolicy:
    return ConstantControlPolicy(
        drug_pressure=0.5,
        acidity_stress=0.1,
    )


def make_engine() -> SimulationEngine:
    return SimulationEngine(
        fitness_model=make_fitness_model(),
        control_policy=make_control_policy(),
    )


def test_mcte_composite_state_satisfies_generic_state_boundary():
    state = make_state()

    copied = state.copy()

    assert isinstance(copied, MCTECompositeState)
    assert copied.phenotype is state.phenotype
    assert copied.environment is state.environment
    assert copied.host is state.host

    # The generic contract is structural: copy() is the required boundary.
    assert callable(getattr(state, "copy", None))


def test_mcte_model_adapter_satisfies_generic_model_boundary():
    state = make_state()

    model = MCTEModelAdapter(
        fitness_model=make_fitness_model(),
    )

    derivative = model.derivative(
        state,
        time=0.0,
    )

    assert isinstance(derivative, np.ndarray)
    assert derivative.shape == state.phenotype.fractions.shape
    assert np.all(np.isfinite(derivative))


def test_mcte_one_step_adapter_satisfies_generic_integrator_boundary():
    state = make_state()

    model = MCTEModelAdapter(
        fitness_model=make_fitness_model(),
    )

    integrator = MCTEOneStepAdapter(
        fitness_model=make_fitness_model(),
        control_policy=make_control_policy(),
    )

    next_state = integrator.step(
        model=model,
        state=state,
        time=0.0,
        dt=0.1,
    )

    assert isinstance(next_state, MCTECompositeState)

    fractions = next_state.phenotype.fractions

    assert fractions.shape == state.phenotype.fractions.shape
    assert np.all(np.isfinite(fractions))
    assert np.all(fractions >= 0.0)
    assert np.isclose(
        np.sum(fractions),
        1.0,
    )

    assert np.isfinite(
        next_state.environment.drug_pressure,
    )
    assert np.isfinite(
        next_state.environment.acidity_stress,
    )

    assert next_state.host is state.host


def test_mcte_one_step_matches_real_simulation_engine():
    state = make_state()

    engine = make_engine()

    times = np.array(
        [0.0, 0.1],
        dtype=float,
    )

    reference = engine.run(
        state.phenotype,
        state.environment,
        state.host,
        times,
    )

    model = MCTEModelAdapter(
        fitness_model=make_fitness_model(),
        transition_matrix=engine.transition_matrix,
    )

    integrator = MCTEOneStepAdapter(
        fitness_model=make_fitness_model(),
        control_policy=make_control_policy(),
        transition_matrix=engine.transition_matrix,
        env_relaxation_rate=engine.env_relaxation_rate,
    )

    adapted = integrator.step(
        model=model,
        state=state,
        time=times[0],
        dt=times[1] - times[0],
    )

    np.testing.assert_allclose(
        adapted.phenotype.fractions,
        reference.trajectory[1],
    )

    assert np.isclose(
        adapted.environment.drug_pressure,
        reference.drug_pressures[1],
    )

    assert np.isclose(
        adapted.environment.acidity_stress,
        reference.acidity_stresses[1],
    )

    assert np.isclose(
        adapted.environment.host_support,
        reference.host_supports[1],
    )

    assert adapted.host is state.host


def test_mcte_result_can_be_projected_to_generic_result():
    state = make_state()

    engine = make_engine()

    times = np.array(
        [0.0, 0.1],
        dtype=float,
    )

    mcte_result = engine.run(
        state.phenotype,
        state.environment,
        state.host,
        times,
    )

    states: list[MCTECompositeState] = [
        MCTECompositeState(
            phenotype=PhenotypeState(
                fractions=mcte_result.trajectory[idx].copy(),
            ),
            environment=EnvironmentState(
                drug_pressure=float(
                    mcte_result.drug_pressures[idx],
                ),
                acidity_stress=float(
                    mcte_result.acidity_stresses[idx],
                ),
                host_support=float(
                    mcte_result.host_supports[idx],
                ),
            ),
            host=state.host,
        )
        for idx in range(len(mcte_result.times))
    ]

    generic_result = GenericSimulationResult(
        times=mcte_result.times.tolist(),
        states=states,
        metadata={
            "source": "mcte",
            "projection": "compatibility-test",
        },
    )

    assert isinstance(
        generic_result,
        GenericSimulationResult,
    )

    assert len(generic_result.times) == 2
    assert len(generic_result.states) == 2

    assert (
        generic_result.metadata["source"]
        == "mcte"
    )

    assert np.allclose(
        generic_result.states[-1].phenotype.fractions,
        mcte_result.trajectory[-1],
    )
