"""
Tests for MCTE v0.1 dynamics.py.

Dynamics contract:

- Replicator selection conserves total phenotype mass.
- Higher-fitness phenotypes increase under selection.
- Lower-fitness phenotypes decrease under selection.
- Transition dynamics conserve total mass.
- Transition rates must be non-negative.
- Invalid fitness and transition matrices are rejected.
- The dynamics layer does not clip or normalize the state.
"""

import numpy as np
import pytest

from scios.domains.oncology.mcte.v0_1.dynamics import (
    compute_system_derivatives,
)

from scios.domains.oncology.mcte.v0_1.state import (
    STATE_DIMENSION,
    PhenotypeState,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def default_state():
    return PhenotypeState.default()


# ============================================================================
# Pure Replicator Dynamics
# ============================================================================

def test_pure_replicator_zero_sum_derivative(
    default_state,
):
    fitness = np.array(
        [1.0, 1.0, 1.0, 1.0],
        dtype=float,
    )

    dx = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=None,
    )

    assert isinstance(dx, np.ndarray)
    assert dx.shape == (
        STATE_DIMENSION,
    )

    assert np.allclose(
        dx,
        0.0,
        atol=1e-12,
    )

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )


def test_replicator_selection_favors_higher_fitness():
    state = PhenotypeState(
        np.array(
            [0.5, 0.5, 0.0, 0.0],
            dtype=float,
        )
    )

    fitness = np.array(
        [2.0, 1.0, 0.0, 0.0],
        dtype=float,
    )

    dx = compute_system_derivatives(
        state,
        fitness,
    )

    assert dx[0] > 0.0
    assert dx[1] < 0.0

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )


def test_replicator_does_not_change_zero_frequency_phenotypes():
    state = PhenotypeState(
        np.array(
            [0.6, 0.4, 0.0, 0.0],
            dtype=float,
        )
    )

    fitness = np.array(
        [2.0, 1.0, 5.0, 5.0],
        dtype=float,
    )

    dx = compute_system_derivatives(
        state,
        fitness,
    )

    assert np.isclose(
        dx[2],
        0.0,
        atol=1e-12,
    )

    assert np.isclose(
        dx[3],
        0.0,
        atol=1e-12,
    )


# ============================================================================
# Transition Dynamics
# ============================================================================

def test_transition_matrix_mass_conservation(
    default_state,
):
    fitness = np.array(
        [1.0, 1.0, 1.0, 1.0],
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 3] = 0.1

    dx = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K,
    )

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )


def test_transition_moves_mass_from_source_to_target():
    state = PhenotypeState(
        np.array(
            [1.0, 0.0, 0.0, 0.0],
            dtype=float,
        )
    )

    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 3] = 0.2

    dx = compute_system_derivatives(
        state,
        fitness,
        transition_matrix=K,
    )

    assert np.isclose(
        dx[0],
        -0.2,
    )

    assert np.isclose(
        dx[3],
        0.2,
    )

    assert np.isclose(
        dx[1],
        0.0,
    )

    assert np.isclose(
        dx[2],
        0.0,
    )

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )


def test_multiple_transitions_conserve_mass(
    default_state,
):
    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K = np.array(
        [
            [0.0, 0.1, 0.2, 0.0],
            [0.3, 0.0, 0.1, 0.0],
            [0.0, 0.2, 0.0, 0.4],
            [0.1, 0.0, 0.3, 0.0],
        ],
        dtype=float,
    )

    dx = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K,
    )

    assert dx.shape == (
        STATE_DIMENSION,
    )

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )


# ============================================================================
# Combined Dynamics
# ============================================================================

def test_selection_and_transition_are_combined():
    state = PhenotypeState(
        np.array(
            [0.5, 0.5, 0.0, 0.0],
            dtype=float,
        )
    )

    fitness = np.array(
        [2.0, 1.0, 1.0, 1.0],
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 3] = 0.1

    dx = compute_system_derivatives(
        state,
        fitness,
        transition_matrix=K,
    )

    assert dx.shape == (
        STATE_DIMENSION,
    )

    assert np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    )

    assert dx[0] < 0.0 or dx[0] != 0.0
    assert dx[3] > 0.0


# ============================================================================
# Validation
# ============================================================================

def test_invalid_fitness_shape_is_rejected(
    default_state,
):
    fitness = np.array(
        [1.0, 1.0, 1.0],
        dtype=float,
    )

    with pytest.raises(ValueError):
        compute_system_derivatives(
            default_state,
            fitness,
        )


@pytest.mark.parametrize(
    "fitness",
    [
        np.array(
            [1.0, 1.0, 1.0, np.nan],
            dtype=float,
        ),
        np.array(
            [1.0, 1.0, 1.0, np.inf],
            dtype=float,
        ),
        np.array(
            [1.0, 1.0, 1.0, -np.inf],
            dtype=float,
        ),
    ],
)
def test_non_finite_fitness_is_rejected(
    default_state,
    fitness,
):
    with pytest.raises(ValueError):
        compute_system_derivatives(
            default_state,
            fitness,
        )


def test_invalid_transition_matrix_shape_is_rejected(
    default_state,
):
    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K = np.zeros(
        (3, 3),
        dtype=float,
    )

    with pytest.raises(ValueError):
        compute_system_derivatives(
            default_state,
            fitness,
            transition_matrix=K,
        )


def test_negative_transition_rates_are_rejected(
    default_state,
):
    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 1] = -0.1

    with pytest.raises(ValueError):
        compute_system_derivatives(
            default_state,
            fitness,
            transition_matrix=K,
        )


def test_non_finite_transition_rates_are_rejected(
    default_state,
):
    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 1] = np.nan

    with pytest.raises(ValueError):
        compute_system_derivatives(
            default_state,
            fitness,
            transition_matrix=K,
        )


# ============================================================================
# Diagonal Semantics
# ============================================================================

def test_diagonal_transition_rates_are_ignored(
    default_state,
):
    fitness = np.ones(
        STATE_DIMENSION,
        dtype=float,
    )

    K_without_diagonal = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K_with_diagonal = K_without_diagonal.copy()

    K_with_diagonal[0, 0] = 100.0
    K_with_diagonal[1, 1] = 200.0
    K_with_diagonal[2, 2] = 300.0
    K_with_diagonal[3, 3] = 400.0

    dx_a = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K_without_diagonal,
    )

    dx_b = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K_with_diagonal,
    )

    assert np.allclose(
        dx_a,
        dx_b,
    )


# ============================================================================
# Purity / No State Mutation
# ============================================================================

def test_dynamics_does_not_mutate_state(
    default_state,
):
    original = default_state.fractions.copy()

    fitness = np.array(
        [2.0, 1.0, 0.5, 0.2],
        dtype=float,
    )

    K = np.zeros(
        (STATE_DIMENSION, STATE_DIMENSION),
        dtype=float,
    )

    K[0, 1] = 0.1

    compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K,
    )

    assert np.array_equal(
        default_state.fractions,
        original,
    )


# ============================================================================
# Numerical Contract
# ============================================================================

def test_derivative_is_finite(
    default_state,
):
    fitness = np.array(
        [1.0, 0.8, 0.9, 0.7],
        dtype=float,
    )

    K = np.array(
        [
            [0.0, 0.1, 0.0, 0.0],
            [0.0, 0.0, 0.1, 0.0],
            [0.0, 0.0, 0.0, 0.1],
            [0.1, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    dx = compute_system_derivatives(
        default_state,
        fitness,
        transition_matrix=K,
    )

    assert np.all(
        np.isfinite(dx)
    )