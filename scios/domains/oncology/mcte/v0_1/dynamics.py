"""
MCTE v0.1
=========

Evolutionary dynamics module.

Integrates:

1. Darwinian selection / replicator dynamics
       dx_i_sel = x_i (F_i - mean(F))

2. Phenotype state transition dynamics
       dx_i_trans = sum_j(K[j,i] x_j) - x_i sum_j(K[i,j])

The combined derivative is:

       dx_i = dx_i_sel + dx_i_trans

The right-hand side preserves total mass:

       sum_i dx_i = 0

Simplex enforcement (x_i >= 0) is intentionally handled by the
integration layer, not by this module.
"""

from __future__ import annotations

import numpy as np

from scios.domains.oncology.mcte.v0_1.state import (
    STATE_DIMENSION,
    PhenotypeState,
)


__all__ = [
    "compute_system_derivatives",
]


def compute_system_derivatives(
    state: PhenotypeState,
    fitness: np.ndarray,
    transition_matrix: np.ndarray | None = None,
) -> np.ndarray:
    """
    Compute the MCTE phenotype derivative dx/dt.

    Parameters
    ----------
    state:
        Current normalized phenotype state x.

    fitness:
        Fitness vector F with shape (STATE_DIMENSION,).

    transition_matrix:
        Optional transition-rate matrix K.

        K[i, j] represents the rate of transition:

            phenotype i -> phenotype j

        The diagonal is ignored.

    Returns
    -------
    np.ndarray
        Derivative vector dx/dt with shape (STATE_DIMENSION,).

    Notes
    -----
    This function does not clip or normalize the state.

    It only computes the ODE right-hand side.
    """

    x = np.asarray(
        state.fractions,
        dtype=float,
    )

    f = np.asarray(
        fitness,
        dtype=float,
    )

    # ------------------------------------------------------------------
    # Validate fitness
    # ------------------------------------------------------------------

    if f.shape != (STATE_DIMENSION,):
        raise ValueError(
            f"Fitness vector must have shape "
            f"({STATE_DIMENSION},), got {f.shape}"
        )

    if not np.all(np.isfinite(f)):
        raise ValueError(
            "Fitness values must be finite."
        )

    # ------------------------------------------------------------------
    # Replicator selection
    # ------------------------------------------------------------------

    mean_fitness = float(
        np.sum(x * f)
    )

    dot_x_selection = (
        x * (f - mean_fitness)
    )

    # ------------------------------------------------------------------
    # Phenotype transitions
    # ------------------------------------------------------------------

    if transition_matrix is None:

        dot_x_transition = np.zeros(
            STATE_DIMENSION,
            dtype=float,
        )

    else:

        K = np.asarray(
            transition_matrix,
            dtype=float,
        )

        if K.shape != (
            STATE_DIMENSION,
            STATE_DIMENSION,
        ):
            raise ValueError(
                "Transition matrix must have shape "
                f"({STATE_DIMENSION}, {STATE_DIMENSION}), "
                f"got {K.shape}"
            )

        if not np.all(np.isfinite(K)):
            raise ValueError(
                "Transition matrix values must be finite."
            )

        if np.any(K < 0.0):
            raise ValueError(
                "Transition rates must be non-negative."
            )

        # Ignore self-transition terms.
        K_off = K.copy()
        np.fill_diagonal(
            K_off,
            0.0,
        )

        # Incoming flow:
        #
        #   incoming_i = sum_j K[j,i] * x_j
        #
        incoming = K_off.T @ x

        # Outgoing flow:
        #
        #   outgoing_i = x_i * sum_j K[i,j]
        #
        outgoing = x * np.sum(
            K_off,
            axis=1,
        )

        dot_x_transition = (
            incoming - outgoing
        )

    # ------------------------------------------------------------------
    # Combined dynamics
    # ------------------------------------------------------------------

    dx = (
        dot_x_selection
        + dot_x_transition
    )

    # ------------------------------------------------------------------
    # Numerical sanity check:
    # selection and transition dynamics must conserve total mass.
    # ------------------------------------------------------------------

    if not np.isclose(
        np.sum(dx),
        0.0,
        atol=1e-12,
    ):
        raise RuntimeError(
            "Dynamics violated mass conservation: "
            f"sum(dx)={np.sum(dx)}"
        )

    return dx