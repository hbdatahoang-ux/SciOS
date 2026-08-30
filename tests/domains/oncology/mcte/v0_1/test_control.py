"""
Tests for MCTE v0.1 control.py.

Control contract:

1. Intervention is immutable.
2. Intervention values are finite and non-negative.
3. ControlPolicy exposes the required interface.
4. ConstantControlPolicy returns a fixed target.
5. MetronomicControlPolicy follows its periodic schedule.
6. Policies do not mutate state or environment.
7. Invalid policy parameters are rejected.
8. Non-finite time is rejected.
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from scios.domains.oncology.mcte.v0_1.control import (
    BaseControlPolicy,
    ConstantControlPolicy,
    ControlPolicy,
    Intervention,
    MetronomicControlPolicy,
)
from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
    HostState,
)
from scios.domains.oncology.mcte.v0_1.state import (
    PhenotypeState,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def state() -> PhenotypeState:
    return PhenotypeState.default()


@pytest.fixture
def env() -> EnvironmentState:
    return EnvironmentState.default()


@pytest.fixture
def host() -> HostState:
    return HostState.default()


# ============================================================================
# Intervention
# ============================================================================


def test_intervention_creation():
    intervention = Intervention(
        target_drug_pressure=0.5,
        target_acidity_stress=0.2,
    )

    assert intervention.target_drug_pressure == 0.5
    assert intervention.target_acidity_stress == 0.2


def test_intervention_normalizes_scalar_types():
    intervention = Intervention(
        target_drug_pressure=np.float64(0.5),
        target_acidity_stress=np.float64(0.2),
    )

    assert isinstance(
        intervention.target_drug_pressure,
        float,
    )

    assert isinstance(
        intervention.target_acidity_stress,
        float,
    )


def test_intervention_is_immutable():
    intervention = Intervention(
        target_drug_pressure=0.5,
        target_acidity_stress=0.2,
    )

    with pytest.raises(FrozenInstanceError):
        intervention.target_drug_pressure = 1.0


@pytest.mark.parametrize(
    "drug_pressure",
    [
        -1.0,
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_invalid_intervention_drug_pressure_is_rejected(
    drug_pressure,
):
    with pytest.raises(ValueError):
        Intervention(
            target_drug_pressure=drug_pressure,
            target_acidity_stress=0.2,
        )


@pytest.mark.parametrize(
    "acidity_stress",
    [
        -1.0,
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_invalid_intervention_acidity_stress_is_rejected(
    acidity_stress,
):
    with pytest.raises(ValueError):
        Intervention(
            target_drug_pressure=0.5,
            target_acidity_stress=acidity_stress,
        )


# ============================================================================
# ConstantControlPolicy
# ============================================================================


def test_constant_policy_is_base_policy():
    policy = ConstantControlPolicy()

    assert isinstance(
        policy,
        BaseControlPolicy,
    )


def test_constant_policy_implements_protocol():
    policy = ConstantControlPolicy()

    assert isinstance(
        policy,
        ControlPolicy,
    )


def test_constant_policy_returns_configured_target(
    state,
    env,
    host,
):
    policy = ConstantControlPolicy(
        drug_pressure=1.2,
        acidity_stress=0.3,
    )

    action = policy.compute_action(
        state,
        env,
        host,
        time=5.0,
    )

    assert isinstance(
        action,
        Intervention,
    )

    assert action.target_drug_pressure == 1.2
    assert action.target_acidity_stress == 0.3


def test_constant_policy_is_deterministic(
    state,
    env,
    host,
):
    policy = ConstantControlPolicy(
        drug_pressure=1.2,
        acidity_stress=0.3,
    )

    action_a = policy.compute_action(
        state,
        env,
        host,
        time=0.0,
    )

    action_b = policy.compute_action(
        state,
        env,
        host,
        time=100.0,
    )

    assert action_a == action_b


def test_constant_policy_reuses_immutable_intervention(
    state,
    env,
    host,
):
    policy = ConstantControlPolicy(
        drug_pressure=1.0,
        acidity_stress=0.2,
    )

    action_a = policy.compute_action(
        state,
        env,
        host,
        time=0.0,
    )

    action_b = policy.compute_action(
        state,
        env,
        host,
        time=1.0,
    )

    assert action_a is action_b


# ============================================================================
# MetronomicControlPolicy
# ============================================================================


def test_metronomic_policy_is_base_policy():
    policy = MetronomicControlPolicy()

    assert isinstance(
        policy,
        BaseControlPolicy,
    )


def test_metronomic_policy_implements_protocol():
    policy = MetronomicControlPolicy()

    assert isinstance(
        policy,
        ControlPolicy,
    )


def test_metronomic_policy_active_phase(
    state,
    env,
    host,
):
    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    action = policy.compute_action(
        state,
        env,
        host,
        time=2.0,
    )

    assert action.target_drug_pressure == 2.0


def test_metronomic_policy_resting_phase(
    state,
    env,
    host,
):
    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    action = policy.compute_action(
        state,
        env,
        host,
        time=7.0,
    )

    assert action.target_drug_pressure == 0.0


def test_metronomic_policy_boundary_is_off(
    state,
    env,
    host,
):
    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    action = policy.compute_action(
        state,
        env,
        host,
        time=5.0,
    )

    assert action.target_drug_pressure == 0.0


def test_metronomic_policy_repeats_periodically(
    state,
    env,
    host,
):
    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    action_a = policy.compute_action(
        state,
        env,
        host,
        time=2.0,
    )

    action_b = policy.compute_action(
        state,
        env,
        host,
        time=12.0,
    )

    assert action_a == action_b


def test_metronomic_policy_preserves_environment_stress(
    state,
    host,
):
    env = EnvironmentState(
        drug_pressure=0.7,
        acidity_stress=0.35,
        host_support=0.9,
    )

    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    action = policy.compute_action(
        state,
        env,
        host,
        time=2.0,
    )

    assert action.target_acidity_stress == 0.35


# ============================================================================
# Parameter validation
# ============================================================================


def test_constant_policy_rejects_negative_drug():
    with pytest.raises(ValueError):
        ConstantControlPolicy(
            drug_pressure=-1.0,
            acidity_stress=0.1,
        )


def test_constant_policy_rejects_negative_stress():
    with pytest.raises(ValueError):
        ConstantControlPolicy(
            drug_pressure=1.0,
            acidity_stress=-0.1,
        )


def test_metronomic_policy_rejects_negative_peak():
    with pytest.raises(ValueError):
        MetronomicControlPolicy(
            peak_drug_pressure=-1.0,
        )


def test_metronomic_policy_rejects_zero_period():
    with pytest.raises(ValueError):
        MetronomicControlPolicy(
            period=0.0,
        )


def test_metronomic_policy_rejects_negative_period():
    with pytest.raises(ValueError):
        MetronomicControlPolicy(
            period=-1.0,
        )


@pytest.mark.parametrize(
    "duty_cycle",
    [
        -0.1,
        1.1,
    ],
)
def test_metronomic_policy_rejects_invalid_duty_cycle(
    duty_cycle,
):
    with pytest.raises(ValueError):
        MetronomicControlPolicy(
            duty_cycle=duty_cycle,
        )


# ============================================================================
# Time validation
# ============================================================================


@pytest.mark.parametrize(
    "invalid_time",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_constant_policy_rejects_non_finite_time(
    state,
    env,
    host,
    invalid_time,
):
    policy = ConstantControlPolicy()

    with pytest.raises(ValueError):
        policy.compute_action(
            state,
            env,
            host,
            time=invalid_time,
        )


@pytest.mark.parametrize(
    "invalid_time",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_metronomic_policy_rejects_non_finite_time(
    state,
    env,
    host,
    invalid_time,
):
    policy = MetronomicControlPolicy()

    with pytest.raises(ValueError):
        policy.compute_action(
            state,
            env,
            host,
            time=invalid_time,
        )


# ============================================================================
# Observer-only / purity contract
# ============================================================================


def test_constant_policy_does_not_mutate_inputs(
    state,
    env,
    host,
):
    original_state = state.fractions.copy()

    original_drug = env.drug_pressure
    original_stress = env.acidity_stress
    original_support = env.host_support

    policy = ConstantControlPolicy(
        drug_pressure=1.5,
        acidity_stress=0.2,
    )

    policy.compute_action(
        state,
        env,
        host,
        time=5.0,
    )

    assert np.array_equal(
        state.fractions,
        original_state,
    )

    assert env.drug_pressure == original_drug
    assert env.acidity_stress == original_stress
    assert env.host_support == original_support


def test_metronomic_policy_does_not_mutate_inputs(
    state,
    env,
    host,
):
    original_state = state.fractions.copy()

    original_drug = env.drug_pressure
    original_stress = env.acidity_stress
    original_support = env.host_support

    policy = MetronomicControlPolicy(
        peak_drug_pressure=2.0,
        period=10.0,
        duty_cycle=0.5,
    )

    policy.compute_action(
        state,
        env,
        host,
        time=2.0,
    )

    assert np.array_equal(
        state.fractions,
        original_state,
    )

    assert env.drug_pressure == original_drug
    assert env.acidity_stress == original_stress
    assert env.host_support == original_support