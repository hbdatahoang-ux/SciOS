"""
Tests for MCTE v0.1 phenotype state semantics.
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from scios.domains.oncology.mcte.v0_1.state import (
    PHENOTYPES,
    STATE_DIMENSION,
    PhenotypeState,
)


# =============================================================================
# Defaults and basic invariants
# =============================================================================


def test_default_state():
    state = PhenotypeState.default()

    assert isinstance(state, PhenotypeState)
    assert STATE_DIMENSION == 4
    assert PHENOTYPES == ("S", "R", "I", "D")

    assert state.fractions.shape == (4,)
    assert np.all(state.fractions >= 0.0)
    assert np.isclose(np.sum(state.fractions), 1.0)

    assert np.allclose(
        state.fractions,
        np.array([0.7, 0.1, 0.1, 0.1]),
    )


def test_state_dimension_is_fixed():
    with pytest.raises(ValueError):
        PhenotypeState(np.array([0.5, 0.5]))

    with pytest.raises(ValueError):
        PhenotypeState(np.array([0.25, 0.25, 0.25, 0.15, 0.10]))


def test_non_negative_invariant():
    with pytest.raises(ValueError):
        PhenotypeState(
            np.array([0.7, -0.1, 0.2, 0.2])
        )


def test_sum_to_one_invariant():
    with pytest.raises(ValueError):
        PhenotypeState(
            np.array([0.7, 0.1, 0.1, 0.2])
        )


def test_finite_values_required():
    with pytest.raises(ValueError):
        PhenotypeState(
            np.array([np.nan, 0.1, 0.2, 0.7])
        )

    with pytest.raises(ValueError):
        PhenotypeState(
            np.array([np.inf, 0.1, 0.2, 0.7])
        )


# =============================================================================
# Immutability
# =============================================================================


def test_dataclass_is_frozen():
    state = PhenotypeState.default()

    with pytest.raises(FrozenInstanceError):
        state.fractions = np.array([0.25, 0.25, 0.25, 0.25])


def test_underlying_numpy_array_is_read_only():
    state = PhenotypeState.default()

    assert state.fractions.flags.writeable is False

    with pytest.raises(ValueError):
        state.fractions[0] = 0.5


def test_input_array_cannot_mutate_state():
    source = np.array([0.7, 0.1, 0.1, 0.1])

    state = PhenotypeState(source)

    source[0] = 0.1
    source[1] = 0.7

    assert np.allclose(
        state.fractions,
        np.array([0.7, 0.1, 0.1, 0.1]),
    )


def test_to_array_returns_read_only_copy():
    state = PhenotypeState.default()

    arr = state.to_array()

    assert np.allclose(arr, state.fractions)
    assert arr.flags.writeable is False

    with pytest.raises(ValueError):
        arr[0] = 0.5


# =============================================================================
# from_dict
# =============================================================================


def test_from_dict():
    state = PhenotypeState.from_dict(
        {
            "S": 0.6,
            "R": 0.2,
            "I": 0.1,
            "D": 0.1,
        }
    )

    assert np.allclose(
        state.fractions,
        np.array([0.6, 0.2, 0.1, 0.1]),
    )


def test_from_dict_missing_keys_are_zero():
    state = PhenotypeState.from_dict(
        {
            "S": 0.7,
            "R": 0.2,
            "I": 0.1,
        }
    )

    assert np.allclose(
        state.fractions,
        np.array([0.7, 0.2, 0.1, 0.0]),
    )


def test_from_dict_is_strict_about_normalization():
    with pytest.raises(ValueError):
        PhenotypeState.from_dict(
            {
                "S": 7.0,
                "R": 1.0,
                "I": 1.0,
                "D": 1.0,
            }
        )


def test_from_dict_rejects_unknown_phenotypes():
    with pytest.raises(ValueError):
        PhenotypeState.from_dict(
            {
                "S": 0.7,
                "R": 0.1,
                "I": 0.1,
                "D": 0.0,
                "X": 0.1,
            }
        )


# =============================================================================
# from_raw
# =============================================================================


def test_from_raw_normalizes_vector():
    state = PhenotypeState.from_raw(
        np.array([7.0, 1.0, 1.0, 1.0])
    )

    assert np.allclose(
        state.fractions,
        np.array([0.7, 0.1, 0.1, 0.1]),
    )


def test_from_raw_normalizes_mapping():
    state = PhenotypeState.from_raw(
        {
            "S": 7.0,
            "R": 1.0,
            "I": 1.0,
            "D": 1.0,
        }
    )

    assert np.allclose(
        state.fractions,
        np.array([0.7, 0.1, 0.1, 0.1]),
    )


def test_from_raw_rejects_negative_values():
    with pytest.raises(ValueError):
        PhenotypeState.from_raw(
            np.array([7.0, -1.0, 1.0, 1.0])
        )


def test_from_raw_rejects_zero_total():
    with pytest.raises(ValueError):
        PhenotypeState.from_raw(
            np.zeros(STATE_DIMENSION)
        )


def test_from_raw_rejects_wrong_shape():
    with pytest.raises(ValueError):
        PhenotypeState.from_raw(
            np.array([1.0, 1.0, 1.0])
        )


# =============================================================================
# Accessors
# =============================================================================


def test_phenotype_properties():
    state = PhenotypeState.default()

    assert state.sensitive == pytest.approx(0.7)
    assert state.resistant == pytest.approx(0.1)
    assert state.invasive == pytest.approx(0.1)
    assert state.differentiated == pytest.approx(0.1)


# =============================================================================
# Serialization
# =============================================================================


def test_to_dict():
    state = PhenotypeState.default()

    result = state.to_dict()

    assert result == {
        "S": 0.7,
        "R": 0.1,
        "I": 0.1,
        "D": 0.1,
    }


def test_dict_round_trip():
    original = PhenotypeState.default()

    restored = PhenotypeState.from_dict(
        original.to_dict()
    )

    assert np.allclose(
        restored.fractions,
        original.fractions,
    )


# =============================================================================
# Numerical tolerance
# =============================================================================


def test_sum_within_tolerance_is_accepted():
    state = PhenotypeState(
        np.array(
            [
                0.700000001,
                0.099999999,
                0.1,
                0.1,
            ]
        )
    )

    assert np.isclose(
        np.sum(state.fractions),
        1.0,
        atol=1e-8,
    )