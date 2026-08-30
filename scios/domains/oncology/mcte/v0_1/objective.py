from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from scios.domains.oncology.mcte.v0_1.environment import EnvironmentState
from scios.domains.oncology.mcte.v0_1.state import PhenotypeState


__all__ = [
    "EvaluationMetrics",
    "compute_step_metrics",
]


@dataclass(frozen=True)
class EvaluationMetrics:
    """
    Immutable instantaneous evaluation metrics.
    """

    malignancy_score: float
    treatment_toxicity: float
    net_utility: float

    def __post_init__(self) -> None:
        malignancy = float(self.malignancy_score)
        toxicity = float(self.treatment_toxicity)
        utility = float(self.net_utility)

        if not np.isfinite(
            [malignancy, toxicity, utility]
        ).all():
            raise ValueError(
                "Evaluation metric values must be finite."
            )

        object.__setattr__(
            self,
            "malignancy_score",
            malignancy,
        )
        object.__setattr__(
            self,
            "treatment_toxicity",
            toxicity,
        )
        object.__setattr__(
            self,
            "net_utility",
            utility,
        )


def compute_step_metrics(
    state: PhenotypeState,
    env: EnvironmentState,
    *,
    weight_resistant: float = 1.0,
    weight_invasive: float = 2.0,
    toxicity_coefficient: float = 0.5,
) -> EvaluationMetrics:
    """
    Compute instantaneous evaluation metrics.

    This function is observation-only and must not mutate
    the phenotype state or environment state.
    """

    weight_r = float(weight_resistant)
    weight_i = float(weight_invasive)
    toxicity_coeff = float(toxicity_coefficient)

    if not np.isfinite(
        [weight_r, weight_i, toxicity_coeff]
    ).all():
        raise ValueError(
            "Metric weights and coefficients must be finite."
        )

    if weight_r < 0.0:
        raise ValueError(
            "weight_resistant must be >= 0."
        )

    if weight_i < 0.0:
        raise ValueError(
            "weight_invasive must be >= 0."
        )

    if toxicity_coeff < 0.0:
        raise ValueError(
            "toxicity_coefficient must be >= 0."
        )

    fractions = state.fractions

    x_r = float(fractions[1])
    x_i = float(fractions[2])

    malignancy = (
        weight_r * x_r
        + weight_i * x_i
    )

    toxicity = (
        toxicity_coeff
        * env.drug_pressure
    )

    net_utility = -(malignancy + toxicity)

    return EvaluationMetrics(
        malignancy_score=malignancy,
        treatment_toxicity=toxicity,
        net_utility=net_utility,
    )