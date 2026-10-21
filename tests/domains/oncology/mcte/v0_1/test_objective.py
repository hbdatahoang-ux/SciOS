import numpy as np
import pytest

from dataclasses import FrozenInstanceError

from scios.domains.oncology.mcte.v0_1.environment import (
    EnvironmentState,
)

from scios.domains.oncology.mcte.v0_1.objective import (
    EvaluationMetrics,
    compute_step_metrics,
)

from scios.domains.oncology.mcte.v0_1.state import (
    PhenotypeState,
)


def test_compute_step_metrics_default():
    state = PhenotypeState.default()

    env = EnvironmentState(
        drug_pressure=1.0,
        acidity_stress=0.1,
        host_support=0.9,
    )

    metrics = compute_step_metrics(
        state,
        env,
    )

    assert isinstance(
        metrics,
        EvaluationMetrics,
    )

    assert np.isclose(
        metrics.malignancy_score,
        0.3,
    )

    assert np.isclose(
        metrics.treatment_toxicity,
        0.5,
    )

    assert np.isclose(
        metrics.net_utility,
        -0.8,
    )


def test_metrics_are_finite():
    state = PhenotypeState.default()
    env = EnvironmentState.default()

    metrics = compute_step_metrics(
        state,
        env,
    )

    assert np.isfinite(
        metrics.malignancy_score
    )

    assert np.isfinite(
        metrics.treatment_toxicity
    )

    assert np.isfinite(
        metrics.net_utility
    )


def test_metrics_immutability():
    metrics = EvaluationMetrics(
        malignancy_score=0.1,
        treatment_toxicity=0.2,
        net_utility=-0.3,
    )

    with pytest.raises(FrozenInstanceError):
        metrics.malignancy_score = 0.5


def test_invalid_metric_weights():
    state = PhenotypeState.default()
    env = EnvironmentState.default()

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            weight_resistant=-1.0,
        )

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            weight_invasive=-1.0,
        )

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            toxicity_coefficient=-1.0,
        )


@pytest.mark.parametrize(
    "parameter",
    [
        "weight_resistant",
        "weight_invasive",
        "toxicity_coefficient",
    ],
)
def test_non_finite_metric_parameters_are_rejected(
    parameter,
):
    state = PhenotypeState.default()
    env = EnvironmentState.default()

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            **{parameter: np.nan},
        )

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            **{parameter: np.inf},
        )

    with pytest.raises(ValueError):
        compute_step_metrics(
            state,
            env,
            **{parameter: -np.inf},
        )


def test_malignancy_depends_only_on_r_and_i():
    env = EnvironmentState.default()

    state_a = PhenotypeState(
        np.array(
            [0.7, 0.1, 0.1, 0.1],
            dtype=float,
        )
    )

    state_b = PhenotypeState(
        np.array(
            [0.5, 0.1, 0.1, 0.3],
            dtype=float,
        )
    )

    metrics_a = compute_step_metrics(
        state_a,
        env,
    )

    metrics_b = compute_step_metrics(
        state_b,
        env,
    )

    assert np.isclose(
        metrics_a.malignancy_score,
        metrics_b.malignancy_score,
    )


def test_toxicity_depends_on_drug_pressure():
    state = PhenotypeState.default()

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

    metrics_low = compute_step_metrics(
        state,
        env_low,
    )

    metrics_high = compute_step_metrics(
        state,
        env_high,
    )

    assert (
        metrics_high.treatment_toxicity
        > metrics_low.treatment_toxicity
    )


def test_custom_weights():
    state = PhenotypeState.default()

    env = EnvironmentState(
        drug_pressure=1.0,
        acidity_stress=0.1,
        host_support=0.9,
    )

    metrics = compute_step_metrics(
        state,
        env,
        weight_resistant=2.0,
        weight_invasive=3.0,
        toxicity_coefficient=1.0,
    )

    expected_malignancy = (
        2.0 * 0.1
        + 3.0 * 0.1
    )

    expected_toxicity = 1.0

    expected_utility = -(
        expected_malignancy
        + expected_toxicity
    )

    assert np.isclose(
        metrics.malignancy_score,
        expected_malignancy,
    )

    assert np.isclose(
        metrics.treatment_toxicity,
        expected_toxicity,
    )

    assert np.isclose(
        metrics.net_utility,
        expected_utility,
    )


def test_compute_step_metrics_is_observation_only():
    state = PhenotypeState.default()

    env = EnvironmentState(
        drug_pressure=1.0,
        acidity_stress=0.1,
        host_support=0.9,
    )

    state_before = state.fractions.copy()
    env_before = env.to_array().copy()

    compute_step_metrics(
        state,
        env,
    )

    assert np.array_equal(
        state.fractions,
        state_before,
    )

    assert np.array_equal(
        env.to_array(),
        env_before,
    )


def test_zero_weights_produce_zero_penalties():
    state = PhenotypeState.default()

    env = EnvironmentState(
        drug_pressure=2.0,
        acidity_stress=0.5,
        host_support=0.9,
    )

    metrics = compute_step_metrics(
        state,
        env,
        weight_resistant=0.0,
        weight_invasive=0.0,
        toxicity_coefficient=0.0,
    )

    assert metrics.malignancy_score == 0.0
    assert metrics.treatment_toxicity == 0.0
    assert metrics.net_utility == 0.0