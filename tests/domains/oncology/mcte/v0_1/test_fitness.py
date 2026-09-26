"""
Tests for MCTE v0.1 fitness.py.

Fitness contract:

- FitnessModel computes a finite vector of shape (STATE_DIMENSION,).
- v0.1 ToyLinearFitnessModel is frequency-independent.
- base_fitness is immutable after construction.
- Model coefficients must be non-negative.
- Invalid time inputs are rejected.
"""

import numpy as np
import pytest

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)

from scios.domains.oncology.mcte.v0_1.fitness import (
    BaseFitnessModel,
    ToyLinearFitnessModel,
)

from scios.domains.oncology.mcte.v0_1.state import (
    STATE_DIMENSION,
    PhenotypeState,
)


# ============================================================================
# Fixtures
# ============================================================================

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
def model():
    return ToyLinearFitnessModel()


# ============================================================================
# Interface / Construction
# ============================================================================

def test_toy_model_is_base_fitness_model(model):
    assert isinstance(model, BaseFitnessModel)


def test_toy_fitness_shape_and_type(model, state, env, host):
    fitness = model.compute_fitness(
        state,
        env,
        host,
        time=0.0,
    )

    assert isinstance(fitness, np.ndarray)
    assert fitness.shape == (STATE_DIMENSION,)
    assert fitness.dtype.kind == "f"
    assert np.all(np.isfinite(fitness))


# ============================================================================
# Default Fitness Semantics
# ============================================================================

def test_default_base_fitness_has_expected_shape(model):
    assert model.base_fitness.shape == (STATE_DIMENSION,)


def test_default_base_fitness_is_finite(model):
    assert np.all(np.isfinite(model.base_fitness))


def test_default_base_fitness_values(model):
    expected = np.array(
        [1.0, 0.8, 0.9, 0.7],
        dtype=float,
    )

    assert np.allclose(
        model.base_fitness,
        expected,
    )


# ============================================================================
# Frequency Independence
# ============================================================================

def test_v01_fitness_is_frequency_independent(model, env, host):
    state_a = PhenotypeState(
        np.array(
            [0.7, 0.1, 0.1, 0.1],
            dtype=float,
        )
    )

    state_b = PhenotypeState(
        np.array(
            [0.1, 0.7, 0.1, 0.1],
            dtype=float,
        )
    )

    fitness_a = model.compute_fitness(
        state_a,
        env,
        host,
        time=5.0,
    )

    fitness_b = model.compute_fitness(
        state_b,
        env,
        host,
        time=5.0,
    )

    assert np.allclose(
        fitness_a,
        fitness_b,
    )


# ============================================================================
# Environmental Effects
# ============================================================================

def test_drug_pressure_impacts_sensitive_more_than_resistant(
    model,
    state,
    host,
):
    env_low = EnvironmentState(
        drug_pressure=0.0,
        acidity_stress=0.1,
        host_support=0.9,
    )

    env_high = EnvironmentState(
        drug_pressure=2.0,
        acidity_stress=0.1,
        host_support=0.9,
    )

    fitness_low = model.compute_fitness(
        state,
        env_low,
        host,
        time=0.0,
    )

    fitness_high = model.compute_fitness(
        state,
        env_high,
        host,
        time=0.0,
    )

    drop_s = fitness_low[0] - fitness_high[0]
    drop_r = fitness_low[1] - fitness_high[1]

    assert drop_s > drop_r
    assert drop_s > 0.0


def test_acidity_stress_increases_invasive_fitness(
    model,
    state,
    host,
):
    env_low = EnvironmentState(
        drug_pressure=0.0,
        acidity_stress=0.0,
        host_support=0.9,
    )

    env_high = EnvironmentState(
        drug_pressure=0.0,
        acidity_stress=1.0,
        host_support=0.9,
    )

    fitness_low = model.compute_fitness(
        state,
        env_low,
        host,
        time=0.0,
    )

    fitness_high = model.compute_fitness(
        state,
        env_high,
        host,
        time=0.0,
    )

    assert fitness_high[2] > fitness_low[2]


def test_host_support_favors_differentiated_phenotype(
    model,
    state,
    host,
):
    env_low_support = EnvironmentState(
        drug_pressure=0.0,
        acidity_stress=0.1,
        host_support=0.0,
    )

    env_high_support = EnvironmentState(
        drug_pressure=0.0,
        acidity_stress=0.1,
        host_support=1.0,
    )

    fitness_low = model.compute_fitness(
        state,
        env_low_support,
        host,
        time=0.0,
    )

    fitness_high = model.compute_fitness(
        state,
        env_high_support,
        host,
        time=0.0,
    )

    assert fitness_high[3] > fitness_low[3]


# ============================================================================
# Host Effects
# ============================================================================

def test_immune_competence_reduces_invasive_fitness(
    model,
    state,
    env,
):
    weak_immune = HostState(
        inflammation=0.1,
        immune_competence=0.0,
    )

    strong_immune = HostState(
        inflammation=0.1,
        immune_competence=1.0,
    )

    fitness_weak = model.compute_fitness(
        state,
        env,
        weak_immune,
        time=0.0,
    )

    fitness_strong = model.compute_fitness(
        state,
        env,
        strong_immune,
        time=0.0,
    )

    assert fitness_strong[2] < fitness_weak[2]


# ============================================================================
# Time Validation
# ============================================================================

@pytest.mark.parametrize(
    "invalid_time",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_non_finite_time_is_rejected(
    model,
    state,
    env,
    host,
    invalid_time,
):
    with pytest.raises(ValueError):
        model.compute_fitness(
            state,
            env,
            host,
            time=invalid_time,
        )


# ============================================================================
# Constructor Validation
# ============================================================================

def test_invalid_base_fitness_shape_is_rejected():
    with pytest.raises(ValueError):
        ToyLinearFitnessModel(
            base_fitness=np.array(
                [1.0, 0.8, 0.9],
                dtype=float,
            )
        )


@pytest.mark.parametrize(
    "parameter",
    [
        "drug_penalty_s",
        "drug_penalty_r",
        "stress_benefit_i",
        "host_support_benefit_d",
    ],
)
def test_negative_coefficients_are_rejected(parameter):
    with pytest.raises(ValueError):
        ToyLinearFitnessModel(
            **{parameter: -1.0}
        )


# ============================================================================
# Immutability
# ============================================================================

def test_base_fitness_is_immutable(model):
    with pytest.raises(ValueError):
        model.base_fitness[0] = 999.0


def test_base_fitness_does_not_alias_constructor_array():
    original = np.array(
        [1.0, 0.8, 0.9, 0.7],
        dtype=float,
    )

    model = ToyLinearFitnessModel(
        base_fitness=original,
    )

    original[0] = 999.0

    assert model.base_fitness[0] != 999.0


# ============================================================================
# Determinism
# ============================================================================

def test_same_inputs_produce_same_fitness(
    model,
    state,
    env,
    host,
):
    fitness_a = model.compute_fitness(
        state,
        env,
        host,
        time=10.0,
    )

    fitness_b = model.compute_fitness(
        state,
        env,
        host,
        time=10.0,
    )

    assert np.array_equal(
        fitness_a,
        fitness_b,
    )