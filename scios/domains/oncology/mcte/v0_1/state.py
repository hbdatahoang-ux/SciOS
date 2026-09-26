"""
MCTE v0.1
=========

Phenotype state semantics.

Defines the immutable phenotype composition vector:

    x(t) = [S, R, I, D]

where:
    S = Drug-sensitive
    R = Drug-resistant
    I = Invasive
    D = Differentiated / less malignant

Core invariants:
    - state dimension is fixed at 4
    - every fraction is finite
    - every fraction is non-negative
    - sum(x) == 1 within numerical tolerance
    - underlying NumPy array is immutable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np


__all__ = [
    "PHENOTYPES",
    "STATE_DIMENSION",
    "PhenotypeState",
]


# =============================================================================
# Phenotype semantics
# =============================================================================

PHENOTYPES: tuple[str, ...] = ("S", "R", "I", "D")

STATE_DIMENSION: int = len(PHENOTYPES)

_NORMALIZATION_ATOL = 1e-8


# =============================================================================
# Phenotype state
# =============================================================================


@dataclass(frozen=True)
class PhenotypeState:
    """
    Immutable container for phenotype fractions x(t).

    Parameters
    ----------
    fractions:
        One-dimensional NumPy array with shape ``(4,)``.

    Invariants
    ----------
    ``x_i >= 0`` for every phenotype.

    ``sum(x_i) == 1`` within numerical tolerance.

    The underlying NumPy array is read-only after construction.
    """

    fractions: np.ndarray = field(
        default_factory=lambda: np.array(
            [0.7, 0.1, 0.1, 0.1],
            dtype=float,
        )
    )

    def __post_init__(self) -> None:
        # ---------------------------------------------------------------------
        # Normalize input representation to a NumPy array.
        # ---------------------------------------------------------------------
        arr = np.asarray(self.fractions, dtype=float)

        # ---------------------------------------------------------------------
        # Shape invariant.
        # ---------------------------------------------------------------------
        if arr.shape != (STATE_DIMENSION,):
            raise ValueError(
                f"Phenotype state vector must have shape "
                f"({STATE_DIMENSION},), got {arr.shape}"
            )

        # ---------------------------------------------------------------------
        # Finite-value invariant.
        # ---------------------------------------------------------------------
        if not np.all(np.isfinite(arr)):
            raise ValueError(
                "Phenotype fractions must contain only finite values."
            )

        # ---------------------------------------------------------------------
        # Non-negativity invariant.
        # ---------------------------------------------------------------------
        if np.any(arr < 0.0):
            raise ValueError(
                "All phenotype fractions must be greater than or equal to 0."
            )

        # ---------------------------------------------------------------------
        # Simplex normalization invariant.
        # ---------------------------------------------------------------------
        total = float(np.sum(arr))

        if not np.isclose(
            total,
            1.0,
            atol=_NORMALIZATION_ATOL,
            rtol=0.0,
        ):
            raise ValueError(
                f"Phenotype fractions must sum to 1.0, got {total}"
            )

        # ---------------------------------------------------------------------
        # Store an independent immutable array.
        #
        # Copying prevents the caller from mutating the original array after
        # construction and thereby violating the frozen-state contract.
        # ---------------------------------------------------------------------
        arr = np.array(arr, dtype=float, copy=True)
        arr.setflags(write=False)

        object.__setattr__(self, "fractions", arr)

    # =========================================================================
    # Constructors
    # =========================================================================

    @classmethod
    def default(cls) -> "PhenotypeState":
        """
        Return the canonical MCTE v0.1 default phenotype state.

        Returns
        -------
        PhenotypeState
            ``[S, R, I, D] = [0.7, 0.1, 0.1, 0.1]``.
        """
        return cls(
            fractions=np.array(
                [0.7, 0.1, 0.1, 0.1],
                dtype=float,
            )
        )

    @classmethod
    def from_dict(
        cls,
        values: Mapping[str, float],
    ) -> "PhenotypeState":
        """
        Construct a state from phenotype-labelled values.

        This constructor is strict with respect to normalization:
        values must represent an already normalized phenotype state.

        Missing phenotype keys are interpreted as zero.

        Parameters
        ----------
        values:
            Mapping using phenotype names ``S``, ``R``, ``I``, ``D``.

        Raises
        ------
        ValueError
            If unknown keys are supplied, values are invalid, or the resulting
            vector is not normalized.
        """
        if not isinstance(values, Mapping):
            raise TypeError("values must be a mapping.")

        unknown = set(values) - set(PHENOTYPES)
        if unknown:
            raise ValueError(
                f"Unknown phenotype keys: {sorted(unknown)}"
            )

        try:
            arr = np.array(
                [values.get(phenotype, 0.0) for phenotype in PHENOTYPES],
                dtype=float,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Phenotype values must be numeric."
            ) from exc

        return cls(fractions=arr)

    @classmethod
    def from_raw(
        cls,
        values: Mapping[str, float] | np.ndarray,
    ) -> "PhenotypeState":
        """
        Construct a normalized state from raw non-negative phenotype values.

        Unlike ``from_dict``, this constructor explicitly performs
        normalization.

        Examples
        --------
        Raw values::

            [7, 1, 1, 1]

        become::

            [0.7, 0.1, 0.1, 0.1]

        Zero-total input is rejected because it cannot define a composition.
        """
        if isinstance(values, Mapping):
            unknown = set(values) - set(PHENOTYPES)
            if unknown:
                raise ValueError(
                    f"Unknown phenotype keys: {sorted(unknown)}"
                )

            try:
                arr = np.array(
                    [values.get(phenotype, 0.0) for phenotype in PHENOTYPES],
                    dtype=float,
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Phenotype values must be numeric."
                ) from exc
        else:
            arr = np.asarray(values, dtype=float)

        if arr.shape != (STATE_DIMENSION,):
            raise ValueError(
                f"Raw phenotype vector must have shape "
                f"({STATE_DIMENSION},), got {arr.shape}"
            )

        if not np.all(np.isfinite(arr)):
            raise ValueError(
                "Raw phenotype values must be finite."
            )

        if np.any(arr < 0.0):
            raise ValueError(
                "Raw phenotype values must be non-negative."
            )

        total = float(np.sum(arr))

        if total <= 0.0:
            raise ValueError(
                "Raw phenotype values must have a positive total."
            )

        normalized = arr / total

        return cls(fractions=normalized)

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, float]:
        """
        Convert the phenotype state to a plain dictionary.
        """
        return {
            phenotype: float(self.fractions[index])
            for index, phenotype in enumerate(PHENOTYPES)
        }

    def to_array(self) -> np.ndarray:
        """
        Return a read-only copy of the phenotype vector.

        The returned array cannot be used to mutate this state.
        """
        arr = self.fractions.copy()
        arr.setflags(write=False)
        return arr

    # =========================================================================
    # Phenotype accessors
    # =========================================================================

    @property
    def sensitive(self) -> float:
        """Fraction of drug-sensitive phenotype S."""
        return float(self.fractions[0])

    @property
    def resistant(self) -> float:
        """Fraction of drug-resistant phenotype R."""
        return float(self.fractions[1])

    @property
    def invasive(self) -> float:
        """Fraction of invasive phenotype I."""
        return float(self.fractions[2])

    @property
    def differentiated(self) -> float:
        """Fraction of differentiated phenotype D."""
        return float(self.fractions[3])