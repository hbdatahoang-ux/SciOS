"""
Tests for MCTE v0.1 environment.py.
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)


# =============================================================================
# EnvironmentState
# =============================================================================


def test_default_environment() -> None:
    env = EnvironmentState.default()

    assert env.drug_pressure == 0.0
    assert env.acidity_stress == 0.1
    assert env.host_support == 0.9


def test_environment_values_are_python_floats() -> None:
    env = EnvironmentState(
        drug_pressure=np.float64(1.0),
        acidity_stress=np.float64(0.2),
        host_support=np.float64(0.8),
    )

    assert type(env.drug_pressure) is float
    assert type(env.acidity_stress) is float
    assert type(env.host_support) is float


def test_environment_to_array() -> None:
    env = EnvironmentState(
        drug_pressure=1.0,
        acidity_stress=0.2,
        host_support=0.8,
    )

    arr = env.to_array()

    assert isinstance(arr, np.ndarray)
    assert arr.shape == (3,)
    assert arr.dtype == float
    assert np.allclose(
        arr,
        [1.0, 0.2, 0.8],
    )


def test_environment_to_array_returns_copy() -> None:
    env = EnvironmentState.default()

    arr = env.to_array()
    arr[0] = 999.0

    assert env.drug_pressure == 0.0


def test_invalid_environment_negative_drug() -> None:
    with pytest.raises(ValueError):
        EnvironmentState(
            drug_pressure=-1.0,
            acidity_stress=0.1,
            host_support=0.9,
        )


def test_invalid_environment_negative_stress() -> None:
    with pytest.raises(ValueError):
        EnvironmentState(
            drug_pressure=0.0,
            acidity_stress=-0.1,
            host_support=0.9,
        )


@pytest.mark.parametrize(
    "host_support",
    [-0.01, 1.01, 2.0],
)
def test_invalid_environment_host_support(
    host_support: float,
) -> None:
    with pytest.raises(ValueError):
        EnvironmentState(
            drug_pressure=0.0,
            acidity_stress=0.1,
            host_support=host_support,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("drug_pressure", np.nan),
        ("drug_pressure", np.inf),
        ("drug_pressure", -np.inf),
        ("acidity_stress", np.nan),
        ("acidity_stress", np.inf),
        ("acidity_stress", -np.inf),
        ("host_support", np.nan),
        ("host_support", np.inf),
        ("host_support", -np.inf),
    ],
)
def test_environment_rejects_non_finite_values(
    field: str,
    value: float,
) -> None:
    kwargs = {
        "drug_pressure": 0.0,
        "acidity_stress": 0.1,
        "host_support": 0.9,
    }

    kwargs[field] = value

    with pytest.raises(ValueError):
        EnvironmentState(**kwargs)


def test_environment_is_immutable() -> None:
    env = EnvironmentState.default()

    with pytest.raises(FrozenInstanceError):
        env.drug_pressure = 1.0  # type: ignore[misc]


# =============================================================================
# HostState
# =============================================================================


def test_default_host() -> None:
    host = HostState.default()

    assert host.inflammation == 0.1
    assert host.immune_competence == 0.8


def test_host_values_are_python_floats() -> None:
    host = HostState(
        inflammation=np.float64(0.2),
        immune_competence=np.float64(0.7),
    )

    assert type(host.inflammation) is float
    assert type(host.immune_competence) is float


def test_host_to_array() -> None:
    host = HostState(
        inflammation=0.2,
        immune_competence=0.7,
    )

    arr = host.to_array()

    assert isinstance(arr, np.ndarray)
    assert arr.shape == (2,)
    assert arr.dtype == float
    assert np.allclose(
        arr,
        [0.2, 0.7],
    )


def test_host_to_array_returns_copy() -> None:
    host = HostState.default()

    arr = host.to_array()
    arr[0] = 999.0

    assert host.inflammation == 0.1


@pytest.mark.parametrize(
    "inflammation",
    [-0.01, 1.01, 2.0],
)
def test_invalid_host_inflammation(
    inflammation: float,
) -> None:
    with pytest.raises(ValueError):
        HostState(
            inflammation=inflammation,
            immune_competence=0.8,
        )


@pytest.mark.parametrize(
    "immune_competence",
    [-0.01, 1.01, 2.0],
)
def test_invalid_host_immune_competence(
    immune_competence: float,
) -> None:
    with pytest.raises(ValueError):
        HostState(
            inflammation=0.1,
            immune_competence=immune_competence,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("inflammation", np.nan),
        ("inflammation", np.inf),
        ("inflammation", -np.inf),
        ("immune_competence", np.nan),
        ("immune_competence", np.inf),
        ("immune_competence", -np.inf),
    ],
)
def test_host_rejects_non_finite_values(
    field: str,
    value: float,
) -> None:
    kwargs = {
        "inflammation": 0.1,
        "immune_competence": 0.8,
    }

    kwargs[field] = value

    with pytest.raises(ValueError):
        HostState(**kwargs)


def test_host_is_immutable() -> None:
    host = HostState.default()

    with pytest.raises(FrozenInstanceError):
        host.inflammation = 0.5  # type: ignore[misc]


# =============================================================================
# Cross-state contract
# =============================================================================


def test_environment_and_host_are_independent_states() -> None:
    env = EnvironmentState.default()
    host = HostState.default()

    assert env is not host
    assert env.host_support != host.immune_competence