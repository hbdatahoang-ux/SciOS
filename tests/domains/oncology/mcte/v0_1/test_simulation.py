import numpy as np
import pytest

from dataclasses import FrozenInstanceError

from scios.domains.oncology.mcte.v0_1.control import (
    ConstantControlPolicy,
)

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)

from scios.domains.oncology.mcte.v0_1.fitness import (
    ToyLinearFitnessModel,
)

from scios.domains.oncology.mcte.v0_1.objective import (
    EvaluationMetrics,
)

from scios.domains.oncology.mcte.v0_1.simulation import (
    SimulationEngine,
    SimulationResult,
)

from scios.domains.oncology.mcte.v0_1.state import (
    PhenotypeState,
    STATE_DIMENSION,
)


@pytest.fixture
def state():
    return PhenotypeState.default()


@pytest.fixture
def env():
    return EnvironmentState.default()


@pytest.fixture
def host():
    return HostState.default()


@pytest.fixture
def engine():
    return SimulationEngine(
        fitness_model=ToyLinearFitnessModel(),
        control_policy=ConstantControlPolicy(
            drug_pressure=0.5,
            acidity_stress=0.1,
        ),
    )


def test_simulation_run_completes_successfully(
    engine,
    state,
    env,
    host,
):
    times = np.linspace(
        0.0,
        10.0,
        num=101,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert isinstance(
        result,
        SimulationResult,
    )

    assert result.trajectory.shape == (
        101,
        STATE_DIMENSION,
    )

    assert result.times.shape == (101,)

    assert result.drug_pressures.shape == (101,)

    assert result.acidity_stresses.shape == (101,)

    assert result.host_supports.shape == (101,)

    assert len(result.metrics_history) == 101


def test_trajectory_preserves_simplex(
    engine,
    state,
    env,
    host,
):
    times = np.linspace(
        0.0,
        10.0,
        num=101,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    sums = np.sum(
        result.trajectory,
        axis=1,
    )

    assert np.allclose(
        sums,
        1.0,
        atol=1e-7,
    )

    assert np.all(
        result.trajectory >= 0.0
    )


def test_initial_state_is_recorded(
    engine,
    state,
    env,
    host,
):
    times = np.array(
        [0.0, 1.0, 2.0],
        dtype=float,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.allclose(
        result.trajectory[0],
        state.fractions,
    )


def test_initial_environment_is_recorded(
    engine,
    state,
    env,
    host,
):
    times = np.array(
        [0.0, 1.0, 2.0],
        dtype=float,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert result.drug_pressures[0] == (
        env.drug_pressure
    )

    assert result.acidity_stresses[0] == (
        env.acidity_stress
    )

    assert result.host_supports[0] == (
        env.host_support
    )


def test_metrics_history_is_aligned(
    engine,
    state,
    env,
    host,
):
    times = np.linspace(
        0.0,
        5.0,
        num=6,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert len(
        result.metrics_history
    ) == len(result.times)

    for metrics in result.metrics_history:
        assert isinstance(
            metrics,
            EvaluationMetrics,
        )


def test_constant_control_changes_environment_towards_target(
    state,
    env,
    host,
):
    engine = SimulationEngine(
        fitness_model=ToyLinearFitnessModel(),
        control_policy=ConstantControlPolicy(
            drug_pressure=1.0,
            acidity_stress=0.5,
        ),
        env_relaxation_rate=1.0,
    )

    times = np.array(
        [0.0, 1.0, 2.0],
        dtype=float,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.isclose(
        result.drug_pressures[1],
        1.0,
    )

    assert np.isclose(
        result.acidity_stresses[1],
        0.5,
    )


def test_environment_relaxation_rate_zero(
    state,
    env,
    host,
):
    engine = SimulationEngine(
        fitness_model=ToyLinearFitnessModel(),
        control_policy=ConstantControlPolicy(
            drug_pressure=1.0,
            acidity_stress=0.5,
        ),
        env_relaxation_rate=0.0,
    )

    times = np.array(
        [0.0, 1.0, 2.0],
        dtype=float,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.allclose(
        result.drug_pressures,
        env.drug_pressure,
    )

    assert np.allclose(
        result.acidity_stresses,
        env.acidity_stress,
    )


def test_host_support_is_not_modified_by_control(
    state,
    env,
    host,
):
    engine = SimulationEngine(
        fitness_model=ToyLinearFitnessModel(),
        control_policy=ConstantControlPolicy(
            drug_pressure=1.0,
            acidity_stress=0.5,
        ),
        env_relaxation_rate=1.0,
    )

    times = np.array(
        [0.0, 1.0, 2.0],
        dtype=float,
    )

    result = engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.allclose(
        result.host_supports,
        env.host_support,
    )


def test_invalid_times_are_rejected(
    engine,
    state,
    env,
    host,
):
    with pytest.raises(ValueError):
        engine.run(
            state,
            env,
            host,
            np.array([0.0]),
        )

    with pytest.raises(ValueError):
        engine.run(
            state,
            env,
            host,
            np.array([0.0, 2.0, 1.0]),
        )

    with pytest.raises(ValueError):
        engine.run(
            state,
            env,
            host,
            np.array([0.0, np.nan]),
        )


def test_negative_environment_relaxation_rate_is_rejected():
    with pytest.raises(ValueError):
        SimulationEngine(
            fitness_model=ToyLinearFitnessModel(),
            control_policy=ConstantControlPolicy(),
            env_relaxation_rate=-1.0,
        )


def test_result_history_lengths_must_match():
    with pytest.raises(ValueError):
        SimulationResult(
            times=np.array(
                [0.0, 1.0],
                dtype=float,
            ),
            trajectory=np.ones(
                (2, STATE_DIMENSION),
                dtype=float,
            ),
            drug_pressures=np.array(
                [0.0],
                dtype=float,
            ),
            acidity_stresses=np.array(
                [0.1, 0.1],
                dtype=float,
            ),
            host_supports=np.array(
                [0.9, 0.9],
                dtype=float,
            ),
            metrics_history=[],
        )


def test_result_is_frozen():
    result = SimulationResult(
        times=np.array(
            [0.0, 1.0],
            dtype=float,
        ),
        trajectory=np.array(
            [
                [0.7, 0.1, 0.1, 0.1],
                [0.6, 0.2, 0.1, 0.1],
            ],
            dtype=float,
        ),
        drug_pressures=np.array(
            [0.0, 0.1],
            dtype=float,
        ),
        acidity_stresses=np.array(
            [0.1, 0.1],
            dtype=float,
        ),
        host_supports=np.array(
            [0.9, 0.9],
            dtype=float,
        ),
        metrics_history=[
            EvaluationMetrics(
                malignancy_score=0.3,
                treatment_toxicity=0.0,
                net_utility=-0.3,
            ),
            EvaluationMetrics(
                malignancy_score=0.4,
                treatment_toxicity=0.05,
                net_utility=-0.45,
            ),
        ],
    )

    with pytest.raises(FrozenInstanceError):
        result.times = np.array([0.0, 1.0])


def test_transition_matrix_validation():
    with pytest.raises(ValueError):
        SimulationEngine(
            fitness_model=ToyLinearFitnessModel(),
            control_policy=ConstantControlPolicy(),
            transition_matrix=np.zeros(
                (3, 3)
            ),
        )

    invalid_matrix = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION)
    )
    invalid_matrix[0, 1] = -1.0

    with pytest.raises(ValueError):
        SimulationEngine(
            fitness_model=ToyLinearFitnessModel(),
            control_policy=ConstantControlPolicy(),
            transition_matrix=invalid_matrix,
        )


def test_simulation_does_not_mutate_initial_state(
    engine,
    state,
    env,
    host,
):
    state_before = state.fractions.copy()

    times = np.linspace(
        0.0,
        5.0,
        num=6,
    )

    engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.array_equal(
        state.fractions,
        state_before,
    )


def test_simulation_does_not_mutate_initial_environment(
    engine,
    state,
    env,
    host,
):
    env_before = env.to_array().copy()

    times = np.linspace(
        0.0,
        5.0,
        num=6,
    )

    engine.run(
        state,
        env,
        host,
        times,
    )

    assert np.array_equal(
        env.to_array(),
        env_before,
    )