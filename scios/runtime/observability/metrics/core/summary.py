"""
SciOS Observability
==================

Summary Metric

Part 1
------

Foundation

Responsibilities
----------------

- Summary metric implementation
- Quantile configuration
- Runtime statistics
- Observation storage

A Summary estimates quantiles over recorded observations.

Unlike Histogram, Summary does not expose bucket boundaries.
"""

from __future__ import annotations

# ==========================================================
# Imports
# ==========================================================

from typing import Any
from typing import Iterable

from .metric import Metric
from .snapshot import MetricSnapshot


__all__ = [
    "Summary",
]


# ==========================================================
# Summary
# ==========================================================


class Summary(Metric):
    """
    Summary metric.

    A Summary records observations and computes:

    - count
    - sum
    - min
    - max
    - mean
    - configurable quantiles

    Examples
    --------
    >>> latency = Summary(
    ...     descriptor=descriptor
    ... )
    >>> latency.observe(12.3)
    >>> latency.observe(18.7)
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        *,
        descriptor,
        quantiles: Iterable[float] | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize Summary.

        Parameters
        ----------
        descriptor
            Metric descriptor.

        quantiles
            Requested quantiles.

        kwargs
            Forwarded to Metric.
        """

        super().__init__(
            descriptor=descriptor,
            **kwargs,
        )

        # --------------------------------------------------
        # Quantiles
        # --------------------------------------------------

        self._quantiles: list[float] = sorted(

            list(
                quantiles
                if quantiles is not None
                else (
                    0.50,
                    0.90,
                    0.95,
                    0.99,
                )
            )

        )

        # --------------------------------------------------
        # Runtime Statistics
        # --------------------------------------------------

        self._values: list[float] = []

        self._count: int = 0

        self._sum: float = 0.0

        self._min: float | None = None

        self._max: float | None = None

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        self.validate()

    # ======================================================
    # Quantiles
    # ======================================================

    @property
    def quantiles(
        self,
    ) -> tuple[float, ...]:
        """
        Configured quantiles.

        Returns
        -------
        tuple[float, ...]
        """

        return tuple(self._quantiles)

    # ======================================================
    # Default Value
    # ======================================================

    def _default_value(
        self,
    ) -> list[float]:
        """
        Default runtime value.

        Returns
        -------
        list[float]
        """

        return []

    # ======================================================
    # Runtime Validation
    # ======================================================

    def _validate_runtime(
        self,
    ) -> None:
        """
        Validate runtime state.

        Raises
        ------
        ValueError
            If runtime state is invalid.
        """

        if self._count < 0:
            raise ValueError(
                "Summary count cannot be negative."
            )

        if self._sum < 0:
            raise ValueError(
                "Summary sum cannot be negative."
            )

        if (
            self._min is not None
            and self._max is not None
            and self._min > self._max
        ):
            raise ValueError(
                "Minimum cannot exceed maximum."
            )

        for q in self._quantiles:

            if not 0.0 <= q <= 1.0:
                raise ValueError(
                    f"Invalid quantile: {q}"
                )
# ======================================================
# Part 2. Summary API
# ======================================================

    def observe(
        self,
        value: float | int,
    ) -> None:
        """
        Record a new observation.

        Parameters
        ----------
        value
            Numeric observation.
        """

        self.validate_value(value)

        with self.lock:

            self._ensure_mutable()

            value = float(value)

            self._previous_value = self._value

            self._values.append(value)

            self._count += 1

            self._sum += value

            if (
                self._min is None
                or value < self._min
            ):
                self._min = value

            if (
                self._max is None
                or value > self._max
            ):
                self._max = value

            self._value = value

            self._update_count += 1

            self._revision += 1

            self._dirty = True

            self._touch()


    def record(
        self,
        value: float | int,
    ) -> None:
        """
        Alias of observe().
        """

        self.observe(value)


    def update(
        self,
        value: float | int,
    ) -> None:
        """
        Alias of observe().

        Summary metrics accumulate values rather than
        replacing them.
        """

        self.observe(value)


    def count(
        self,
    ) -> int:
        """
        Return total number of observations.

        Returns
        -------
        int
        """

        return self._count


    def sum(
        self,
    ) -> float:
        """
        Return accumulated sum.

        Returns
        -------
        float
        """

        return self._sum


    def quantile(
        self,
        q: float,
    ) -> float | None:
        """
        Estimate a quantile.

        Parameters
        ----------
        q
            Quantile in [0,1].

        Returns
        -------
        float | None
        """

        self.validate_quantile(q)

        if not self._values:
            return None

        values = sorted(self._values)

        if len(values) == 1:
            return values[0]

        index = q * (len(values) - 1)

        lower = int(index)

        upper = min(
            lower + 1,
            len(values) - 1,
        )

        if lower == upper:
            return values[lower]

        fraction = index - lower

        return (

            values[lower]

            + (

                values[upper]
                - values[lower]

            ) * fraction

        )


    def reset(
        self,
    ) -> None:
        """
        Reset runtime statistics.
        """

        with self.lock:

            self._ensure_mutable()

            self._previous_value = self._value

            self._values.clear()

            self._count = 0

            self._sum = 0.0

            self._min = None

            self._max = None

            self._value = self._default_value()

            self._update_count += 1

            self._revision += 1

            self._dirty = True

            self._touch()
# ======================================================
# Part 3. Properties
# ======================================================

    @property
    def value(
        self,
    ) -> list[float]:
        """
        Recorded observations.

        Returns
        -------
        list[float]
            Copy of all observed values.
        """

        return list(self._values)


    @property
    def count(
        self,
    ) -> int:
        """
        Number of observations.
        """

        return self._count


    @property
    def sum(
        self,
    ) -> float:
        """
        Sum of observations.
        """

        return self._sum


    @property
    def min(
        self,
    ) -> float | None:
        """
        Minimum observed value.
        """

        return self._min


    @property
    def max(
        self,
    ) -> float | None:
        """
        Maximum observed value.
        """

        return self._max


    @property
    def mean(
        self,
    ) -> float:
        """
        Arithmetic mean.

        Returns
        -------
        float
        """

        if self._count == 0:
            return 0.0

        return self._sum / self._count


    @property
    def quantiles(
        self,
    ) -> dict[float, float | None]:
        """
        Current configured quantiles.

        Returns
        -------
        dict
        """

        return {
            q: self.quantile(q)
            for q in self._quantiles
        }


    @property
    def created_at(
        self,
    ):
        """
        Creation timestamp.
        """

        return self._created_at


    @property
    def updated_at(
        self,
    ):
        """
        Last update timestamp.
        """

        return self._updated_at


    @property
    def revision(
        self,
    ) -> int:
        """
        Runtime revision.
        """

        return self._revision


    @property
    def dirty(
        self,
    ) -> bool:
        """
        Dirty flag.

        Indicates whether runtime state has changed
        since the last snapshot/export.
        """

        return self._dirty
# ======================================================
# Part 4. Snapshot
# ======================================================

    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create an immutable snapshot of the Summary.

        Returns
        -------
        MetricSnapshot
        """

        with self.lock:

            return MetricSnapshot.create(

                name=self.name,

                value={
                    "count": self._count,
                    "sum": self._sum,
                    "min": self._min,
                    "max": self._max,
                    "mean": self.mean,
                    "quantiles": self.quantiles,
                },

                metric_type="summary",

                labels=self.labels.to_dict(),

                attributes=self.attributes.to_dict(),

                metadata=self.metadata.to_dict(),

            )


    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Restore runtime state from a snapshot.

        Parameters
        ----------
        snapshot
            Summary snapshot.
        """

        if snapshot.metric_type != "summary":

            raise TypeError(
                "Snapshot is not a Summary."
            )

        data = snapshot.value

        with self.lock:

            self._ensure_mutable()

            self._previous_value = self._value

            self._count = int(
                data.get("count", 0)
            )

            self._sum = float(
                data.get("sum", 0.0)
            )

            self._min = data.get("min")

            self._max = data.get("max")

            # Summary snapshots do not retain the full
            # observation history. Start with an empty list.
            self._values = []

            self._value = None

            self._update_count += 1

            self._revision += 1

            self._dirty = True

            self._touch()


    def clone(
        self,
    ) -> "Summary":
        """
        Deep clone this Summary.

        Returns
        -------
        Summary
        """

        clone = self.__class__(

            descriptor=self.descriptor.copy(),

            metadata=self.metadata.copy(),

            labels=self.labels.copy(),

            attributes=self.attributes.copy(),

            quantiles=tuple(
                self._quantiles
            ),

        )

        with clone.lock:

            clone._values = list(
                self._values
            )

            clone._count = self._count

            clone._sum = self._sum

            clone._min = self._min

            clone._max = self._max

            clone._value = self._value

            clone._previous_value = (
                self._previous_value
            )

            clone._update_count = (
                self._update_count
            )

            clone._revision = (
                self._revision
            )

            clone._dirty = self._dirty

            clone._updated_at = (
                self._updated_at
            )

        return clone


    def copy(
        self,
    ) -> "Summary":
        """
        Alias of clone().

        Returns
        -------
        Summary
        """

        return self.clone()
# ======================================================
# Part 5. Lifecycle
# ======================================================

    def freeze(
        self,
    ) -> None:
        """
        Freeze the Summary.

        A frozen Summary becomes read-only until
        unfreeze() is called.
        """

        with self.lock:

            if not self._closed:

                self._frozen = True

                self._revision += 1

                self._dirty = True

                self._touch()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze the Summary.
        """

        with self.lock:

            if not self._closed:

                self._frozen = False

                self._revision += 1

                self._dirty = True

                self._touch()


    def enable(
        self,
    ) -> None:
        """
        Enable updates.
        """

        with self.lock:

            if not self._closed:

                self._enabled = True

                self._revision += 1

                self._dirty = True

                self._touch()


    def disable(
        self,
    ) -> None:
        """
        Disable updates.

        Existing values remain available but new
        observations are rejected.
        """

        with self.lock:

            if not self._closed:

                self._enabled = False

                self._revision += 1

                self._dirty = True

                self._touch()


    def close(
        self,
    ) -> None:
        """
        Permanently close the Summary.

        Once closed, no runtime updates are allowed
        until reopen() is invoked.
        """

        with self.lock:

            self._closed = True

            self._enabled = False

            self._frozen = True

            self._revision += 1

            self._dirty = True

            self._touch()


    def reopen(
        self,
    ) -> None:
        """
        Reopen a previously closed Summary.
        """

        with self.lock:

            self._closed = False

            self._enabled = True

            self._frozen = False

            self._revision += 1

            self._dirty = True

            self._touch()
# ======================================================
# Part 6. Validation
# ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the complete Summary state.

        Raises
        ------
        ValueError
            If the runtime state is invalid.
        """

        self._validate_runtime()

        for q in self._quantiles:
            self.validate_quantile(q)

        for value in self._values:
            self.validate_value(value)


    def validate_quantile(
        self,
        quantile: float,
    ) -> None:
        """
        Validate a quantile.

        Parameters
        ----------
        quantile
            Quantile value.

        Raises
        ------
        TypeError
            If quantile is not numeric.

        ValueError
            If quantile is outside [0, 1].
        """

        self.validate_numeric(quantile)

        if not 0.0 <= float(quantile) <= 1.0:

            raise ValueError(
                "Quantile must be between 0.0 and 1.0."
            )


    def validate_value(
        self,
        value: Any,
    ) -> None:
        """
        Validate an observation.

        Parameters
        ----------
        value
            Observation value.

        Raises
        ------
        TypeError
            If the value is not numeric.
        """

        self.validate_numeric(value)


    def validate_numeric(
        self,
        value: Any,
    ) -> None:
        """
        Validate a numeric value.

        Parameters
        ----------
        value
            Candidate numeric value.

        Raises
        ------
        TypeError
            If value is not int or float.

        ValueError
            If value is NaN or infinite.
        """

        if not isinstance(
            value,
            (int, float),
        ):

            raise TypeError(
                "Value must be numeric."
            )

        value = float(value)

        if value != value:

            raise ValueError(
                "NaN is not allowed."
            )

        if value in (
            float("inf"),
            float("-inf"),
        ):

            raise ValueError(
                "Infinite values are not allowed."
            )
# ======================================================
# Part 7. Diagnostics
# ======================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime statistics.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "type": "summary",

            "count": self._count,

            "sum": self._sum,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "quantiles": self.quantiles,

            "updates": self._update_count,

            "revision": self._revision,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

        }


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime health information.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "dirty": self._dirty,

            "healthy": (

                self._enabled

                and not self._closed

            ),

            "observations": self._count,

            "revision": self._revision,

        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump complete runtime state.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "descriptor": self.descriptor.name,

            "statistics": self.statistics(),

            "health": self.health(),

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

        }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed inspection information.

        Intended for debugging and runtime diagnostics.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "class": self.__class__.__name__,

            "metric_type": "summary",

            "value": self.value,

            "count": self._count,

            "sum": self._sum,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "quantiles": self.quantiles,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "dirty": self._dirty,

            "revision": self._revision,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

        }
# ======================================================
# Part 8. Serialization
# ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the Summary to a dictionary.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "metric_type": "summary",

            "name": self.name,

            "count": self._count,

            "sum": self._sum,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "quantiles": list(
                self._quantiles
            ),

            "values": list(
                self._values
            ),

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

            "created_at": self._created_at.isoformat(),

            "updated_at": self._updated_at.isoformat(),

            "revision": self._revision,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        descriptor,
    ) -> "Summary":
        """
        Construct a Summary from a dictionary.

        Parameters
        ----------
        data
            Serialized summary.

        descriptor
            Metric descriptor.

        Returns
        -------
        Summary
        """

        summary = cls(

            descriptor=descriptor,

            quantiles=data.get(
                "quantiles",
            ),

        )

        for value in data.get(
            "values",
            [],
        ):

            summary.observe(value)

        return summary


    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize the Summary to JSON.

        Parameters
        ----------
        kwargs
            Forwarded to json.dumps().

        Returns
        -------
        str
        """

        import json

        kwargs.setdefault(
            "indent",
            2,
        )

        kwargs.setdefault(
            "ensure_ascii",
            False,
        )

        return json.dumps(

            self.to_dict(),

            **kwargs,

        )


    @classmethod
    def from_json(
        cls,
        payload: str,
        *,
        descriptor,
    ) -> "Summary":
        """
        Construct a Summary from JSON.

        Parameters
        ----------
        payload
            JSON string.

        descriptor
            Metric descriptor.

        Returns
        -------
        Summary
        """

        import json

        return cls.from_dict(

            json.loads(payload),

            descriptor=descriptor,

        )
# ======================================================
# Part 9. Export
# ======================================================

    def prometheus(
        self,
    ) -> str:
        """
        Export Summary in Prometheus exposition format.

        Returns
        -------
        str
        """

        labels = ""

        if len(self.labels):

            labels = "{" + ",".join(

                f'{k}="{v}"'

                for k, v in sorted(
                    self.labels.items()
                )

            ) + "}"

        lines: list[str] = []

        # Quantiles
        for q in self._quantiles:

            value = self.quantile(q)

            quantile_labels = (
                f'{{quantile="{q}"}}'
                if not labels
                else labels[:-1] + f',quantile="{q}"' + "}"
            )

            lines.append(
                f"{self.name}{quantile_labels} "
                f"{0.0 if value is None else value}"
            )

        # Count
        lines.append(
            f"{self.name}_count{labels} {self._count}"
        )

        # Sum
        lines.append(
            f"{self.name}_sum{labels} {self._sum}"
        )

        return "\n".join(lines)


    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export Summary in an OpenTelemetry-friendly format.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "name": self.name,

            "type": "summary",

            "count": self._count,

            "sum": self._sum,

            "min": self._min,

            "max": self._max,

            "mean": self.mean,

            "quantiles": self.quantiles,

            "attributes": self.attributes.to_dict(),

            "labels": self.labels.to_dict(),

            "metadata": self.metadata.to_dict(),

            "timestamp": self.updated_at.isoformat(),

        }


    def csv(
        self,
    ) -> str:
        """
        Export Summary as a CSV row.

        Returns
        -------
        str
        """

        quantiles = ";".join(

            f"{q}:{self.quantile(q)}"

            for q in self._quantiles

        )

        return ",".join(

            [

                self.name,

                "summary",

                str(self._count),

                str(self._sum),

                str(self._min),

                str(self._max),

                str(self.mean),

                quantiles,

                self.updated_at.isoformat(),

            ]

        )
# ======================================================
# Part 10. Final Polish
# ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.

        Returns
        -------
        str
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self.name!r}, "

            f"count={self._count}, "

            f"sum={self._sum}, "

            f"mean={self.mean}, "

            f"revision={self._revision})"

        )


    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.

        Returns
        -------
        str
        """

        return (

            f"{self.name}"

            f"(count={self._count}, "

            f"mean={self.mean:.6f}, "

            f"min={self._min}, "

            f"max={self._max})"

        )


    def __len__(
        self,
    ) -> int:
        """
        Number of recorded observations.

        Returns
        -------
        int
        """

        return self._count


    def __bool__(
        self,
    ) -> bool:
        """
        Truthiness.

        Returns
        -------
        bool
            True if at least one observation exists.
        """

        return self._count > 0


    # ==================================================
    # Compatibility
    # ==================================================

    @property
    def total(
        self,
    ) -> float:
        """
        Compatibility alias for sum.

        Returns
        -------
        float
        """

        return self._sum


    @property
    def average(
        self,
    ) -> float:
        """
        Compatibility alias for mean.

        Returns
        -------
        float
        """

        return self.mean


    @property
    def observations(
        self,
    ) -> list[float]:
        """
        Compatibility alias for recorded values.

        Returns
        -------
        list[float]
        """

        return self.value


    def export(
        self,
        format: str = "dict",
    ) -> Any:
        """
        Generic export interface.

        Parameters
        ----------
        format
            One of:
            - dict
            - json
            - prometheus
            - otel
            - csv

        Returns
        -------
        Any
        """

        format = format.lower()

        exporters = {

            "dict": self.to_dict,

            "json": self.to_json,

            "prometheus": self.prometheus,

            "otel": self.otel,

            "csv": self.csv,

        }

        try:

            return exporters[format]()

        except KeyError:

            raise ValueError(
                f"Unsupported export format: {format}"
            ) from None
                                                                                                        