"""
SciOS Runtime Observability
===========================

Summary Metric
==============

A thread-safe statistical summary metric.

The Summary stores observations and exposes:

- count
- sum
- average
- minimum
- maximum
- arbitrary quantiles
- p50 / p90 / p95 / p99
- reset
- snapshot / restore
- labels / metadata through Metric
- deterministic serialization helpers

Python 3.11+
"""

from __future__ import annotations

from copy import deepcopy
from math import isnan
from threading import RLock
from typing import Any, Iterable


try:
    from .metric import Metric
except ImportError:
    from .core.metric import Metric


__all__ = [
    "Summary",
]


# ============================================================================
# Part 1. Summary
# ============================================================================


class Summary(Metric):
    """
    Thread-safe statistical summary.

    Parameters
    ----------
    name:
        Metric name.

    description:
        Human-readable metric description.

    unit:
        Measurement unit.

    labels:
        Optional metric labels.

    value:
        Optional initial observation.

        ``value`` is retained for compatibility with the public Summary API.
        It is recorded as an observation when supplied.

    Notes
    -----
    Summary deliberately keeps the raw observations.

    This provides exact quantiles for the runtime observability test/API layer
    and keeps snapshot/restore lossless.
    """

    # ----------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------

    def __init__(
        self,
        name: str,
        value: int | float = 0,
        **kwargs: Any,
    ) -> None:
        """
        Create an empty Summary.

        ``value`` is accepted for API compatibility.  The default value of
        zero does NOT create an observation, so a newly created Summary
        remains empty.
        """

        # The current SciOS Metric implementation does not accept ``value``
        # in its constructor.  Do not pass it through.
        super().__init__(
            name=name,
            **kwargs,
        )

        self._summary_lock = RLock()
        self._observations: list[float] = []

        # Preserve the semantic expected by the public test/API layer:
        # Summary("name") starts empty.
        #
        # A non-default explicit value is treated as an initial observation.
        if value != 0:
            self.observe(value)

    # =========================================================================
    # Part 2. Internal helpers
    # =========================================================================

    @staticmethod
    def _validate_observation(value: int | float) -> float:
        """
        Validate and normalize an observation.
        """

        if isinstance(value, bool):
            raise TypeError(
                "Summary observation must be numeric."
            )

        if not isinstance(value, (int, float)):
            raise TypeError(
                "Summary observation must be numeric."
            )

        numeric = float(value)

        if isnan(numeric):
            raise ValueError(
                "Summary observation cannot be NaN."
            )

        return numeric

    # =========================================================================
    # Part 3. Observation API
    # =========================================================================

    def observe(
        self,
        value: int | float,
    ) -> "Summary":
        """
        Record one observation.

        Negative values are valid.
        """

        numeric = self._validate_observation(value)

        with self._summary_lock:
            self._observations.append(numeric)

        return self

    # Compatibility alias used by some metric callers.
    record = observe

    # =========================================================================
    # Part 4. Statistical properties
    # =========================================================================

    @property
    def count(self) -> int:
        """
        Number of observations.
        """

        with self._summary_lock:
            return len(self._observations)

    @property
    def sum(self) -> float:
        """
        Sum of all observations.

        Returns zero for an empty Summary.
        """

        with self._summary_lock:
            return float(sum(self._observations))

    @property
    def average(self) -> float:
        """
        Arithmetic mean.

        Returns zero for an empty Summary.
        """

        with self._summary_lock:
            if not self._observations:
                return 0.0

            return float(
                sum(self._observations)
                / len(self._observations)
            )

    @property
    def minimum(self) -> float:
        """
        Minimum observation.

        Returns zero for an empty Summary.
        """

        with self._summary_lock:
            if not self._observations:
                return 0.0

            return min(self._observations)

    @property
    def maximum(self) -> float:
        """
        Maximum observation.

        Returns zero for an empty Summary.
        """

        with self._summary_lock:
            if not self._observations:
                return 0.0

            return max(self._observations)

    # =========================================================================
    # Part 5. Quantiles
    # =========================================================================

    def quantile(
        self,
        q: float,
    ) -> float:
        """
        Return the exact empirical quantile.

        Parameters
        ----------
        q:
            Quantile in the inclusive range [0, 1].

        Notes
        -----
        Linear interpolation is used, matching the conventional percentile
        definition used by NumPy's default linear method.

        Empty summaries return zero.
        """

        if isinstance(q, bool) or not isinstance(q, (int, float)):
            raise TypeError(
                "Quantile must be numeric."
            )

        q = float(q)

        if q < 0.0 or q > 1.0:
            raise ValueError(
                "Quantile must be between 0 and 1."
            )

        with self._summary_lock:
            if not self._observations:
                return 0.0

            values = sorted(self._observations)

        if len(values) == 1:
            return values[0]

        position = q * (len(values) - 1)

        lower_index = int(position)
        upper_index = min(
            lower_index + 1,
            len(values) - 1,
        )

        fraction = position - lower_index

        lower = values[lower_index]
        upper = values[upper_index]

        return float(
            lower + fraction * (upper - lower)
        )

    @property
    def p50(self) -> float:
        """50th percentile."""

        return self.quantile(0.50)

    @property
    def p90(self) -> float:
        """90th percentile."""

        return self.quantile(0.90)

    @property
    def p95(self) -> float:
        """95th percentile."""

        return self.quantile(0.95)

    @property
    def p99(self) -> float:
        """99th percentile."""

        return self.quantile(0.99)

    # =========================================================================
    # Part 6. Observation access
    # =========================================================================

    @property
    def observations(self) -> tuple[float, ...]:
        """
        Return an immutable copy of the observations.
        """

        with self._summary_lock:
            return tuple(self._observations)

    # =========================================================================
    # Part 7. Reset
    # =========================================================================

    def reset(self) -> "Summary":
        """
        Remove all observations.
        """

        with self._summary_lock:
            self._observations.clear()

        return self

    # =========================================================================
    # Part 8. Snapshot
    # =========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a lossless Summary snapshot.

        The snapshot is intentionally a plain dictionary so that it remains
        compatible with the existing runtime metric tests and serialization
        layer.
        """

        with self._summary_lock:
            observations = list(self._observations)

        snapshot: dict[str, Any] = {
            "name": self.name,
            "description": getattr(
                self,
                "description",
                None,
            ),
            "unit": getattr(
                self,
                "unit",
                None,
            ),
            "labels": deepcopy(
                getattr(
                    self,
                    "labels",
                    None,
                )
            ),
            "observations": observations,
            "count": len(observations),
            "sum": float(sum(observations)),
        }

        return snapshot

    # =========================================================================
    # Part 9. Restore
    # =========================================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Summary":
        """
        Restore Summary observations from a snapshot.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "Summary snapshot must be a dictionary."
            )

        raw_observations = snapshot.get(
            "observations",
            [],
        )

        if not isinstance(
            raw_observations,
            Iterable,
        ) or isinstance(
            raw_observations,
            (str, bytes, dict),
        ):
            raise TypeError(
                "Summary observations must be iterable."
            )

        restored: list[float] = []

        for value in raw_observations:
            restored.append(
                self._validate_observation(value)
            )

        with self._summary_lock:
            self._observations = restored

        # Restore labels when the underlying Metric exposes a mutable
        # labels API.  Keep this deliberately defensive because different
        # SciOS Metric generations expose labels differently.
        if "labels" in snapshot:
            labels = snapshot["labels"]

            try:
                if labels is not None and hasattr(
                    self,
                    "update_labels",
                ):
                    if isinstance(labels, dict):
                        self.update_labels(labels)
            except Exception:
                # Statistical state restoration must not fail merely because
                # an optional metadata representation is incompatible.
                pass

        return self

    # =========================================================================
    # Part 10. Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the Summary into a plain dictionary.
        """

        return self.snapshot()

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> "Summary":
        """
        Construct a Summary from a dictionary snapshot.
        """

        if not isinstance(payload, dict):
            raise TypeError(
                "Summary payload must be a dictionary."
            )

        summary = cls(
            payload.get(
                "name",
                "summary",
            ),
            description=payload.get(
                "description"
            ),
            unit=payload.get(
                "unit"
            ),
        )

        summary.restore(payload)

        return summary

    # =========================================================================
    # Part 11. Copy / clone
    # =========================================================================

    def copy(self) -> "Summary":
        """
        Return an independent copy.
        """

        return type(self).from_dict(
            self.snapshot()
        )

    def clone(self) -> "Summary":
        """
        Alias for copy().
        """

        return self.copy()

    # =========================================================================
    # Part 12. Representation
    # =========================================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"count={self.count}, "
            f"sum={self.sum!r})"
        )