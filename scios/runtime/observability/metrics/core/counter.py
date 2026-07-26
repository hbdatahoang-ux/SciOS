"""
SciOS Observability
==================

Counter Metric.

Part 1
------

Foundation.

Responsibilities
----------------

- Counter definition
- Constructor
- Default value
- Runtime validation

Notes
-----
A Counter is a monotonic metric.

Its value:

    - starts at zero
    - may only increase
    - cannot become negative

Concrete update APIs are implemented in Part 2.
"""

from __future__ import annotations

from typing import Any

from .descriptor import MetricDescriptor
from .metadata import MetricMetadata
from .labels import MetricLabels
from .attributes import MetricAttributes
from .metric import Metric

__all__ = [
    "Counter",
]


# ==========================================================
# Counter
# ==========================================================


class Counter(Metric):
    """
    Monotonic cumulative metric.

    Counter values are always >= 0.

    Typical examples

    - HTTP requests
    - Errors
    - Transactions
    - Messages
    - Packets
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        *,
        descriptor: MetricDescriptor,
        metadata: MetricMetadata | None = None,
        labels: MetricLabels | None = None,
        attributes: MetricAttributes | None = None,
    ) -> None:
        """
        Initialize a Counter.
        """

        super().__init__(
            descriptor=descriptor,
            metadata=metadata,
            labels=labels,
            attributes=attributes,
        )

        # Counter always starts at zero.
        self._value = self._default_value()

    # ======================================================
    # Default Value
    # ======================================================

    def _default_value(self) -> int:
        """
        Return the default Counter value.

        Returns
        -------
        int
            Always zero.
        """

        return 0

    # ======================================================
    # Runtime Validation
    # ======================================================

    def validate(self) -> None:
        """
        Validate runtime state.

        Raises
        ------
        TypeError
            Invalid value type.

        ValueError
            Invalid counter value.
        """

        value = self._value

        if not isinstance(value, (int, float)):
            raise TypeError(
                "Counter value must be numeric."
            )

        if value < 0:
            raise ValueError(
                "Counter cannot be negative."
            )

        if self._closed:
            raise RuntimeError(
                "Counter is closed."
            )

    # ======================================================
    # Metric Identity
    # ======================================================

    @property
    def metric_type(self) -> str:
        """
        Metric type.
        """

        return "counter"

    @property
    def monotonic(self) -> bool:
        """
        Counter is monotonic.
        """

        return True

    @property
    def cumulative(self) -> bool:
        """
        Counter is cumulative.
        """

        return True
    # ======================================================
    # Part 2. Counter API
    # ======================================================

    def inc(
        self,
        amount: int | float = 1,
    ) -> None:
        """
        Increment the counter.

        Parameters
        ----------
        amount
            Increment amount.

        Raises
        ------
        ValueError
            If amount is negative.
        """

        self.add(amount)


    def add(
        self,
        amount: int | float,
    ) -> None:
        """
        Add a positive amount.

        Parameters
        ----------
        amount
            Amount to add.

        Raises
        ------
        TypeError
            Invalid amount.

        ValueError
            Negative increment.
        """

        self._ensure_mutable()

        if not isinstance(
            amount,
            (int, float),
        ):
            raise TypeError(
                "Counter increment must be numeric."
            )

        if amount < 0:
            raise ValueError(
                "Counter cannot decrease."
            )

        previous = self._value

        self._before_update(
            previous,
            previous + amount,
        )

        self._previous_value = previous

        self._value += amount

        self._update_count += 1

        self._touch()

        self._after_update(
            previous,
            self._value,
        )


    def set(
        self,
        value: Any,
    ) -> None:
        """
        Direct assignment is not supported.

        Counter values must only increase
        through add() / inc().
        """

        raise RuntimeError(
            "Counter.set() is disabled. "
            "Use add() or inc() instead."
        )


    def update(
        self,
        amount: int | float,
    ) -> None:
        """
        Update counter.

        Alias of add().
        """

        self.add(amount)


    def reset(
        self,
    ) -> None:
        """
        Reset counter.

        Intended primarily for testing or
        controlled runtime reinitialization.

        Production monitoring systems
        typically create a new Counter
        instead of resetting an existing one.
        """

        self._ensure_mutable()

        previous = self._value

        self._before_update(
            previous,
            0,
        )

        self._previous_value = previous

        self._value = self._default_value()

        self._update_count += 1

        self._touch()

        self._after_update(
            previous,
            self._value,
        )
    # ======================================================
    # Part 3. Properties
    # ======================================================

    @property
    def value(
        self,
    ) -> int | float:
        """
        Current counter value.

        Returns
        -------
        int | float
            Monotonic counter value.
        """

        return self._value


    @property
    def total(
        self,
    ) -> int | float:
        """
        Alias of value.

        Returns
        -------
        int | float
        """

        return self._value


    @property
    def count(
        self,
    ) -> int:
        """
        Number of successful counter updates.

        Returns
        -------
        int
        """

        return self._update_count


    @property
    def created_at(
        self,
    ):
        """
        Counter creation time.

        Returns
        -------
        datetime
        """

        return self._created_at


    @property
    def updated_at(
        self,
    ):
        """
        Last successful update time.

        Returns
        -------
        datetime
        """

        return self._updated_at
    # ======================================================
    # Part 4. Snapshot
    # ======================================================

    def snapshot(
        self,
    ):
        """
        Create an immutable snapshot of this Counter.

        Returns
        -------
        MetricSnapshot
        """

        self.validate()

        return super().snapshot()


    def restore(
        self,
        snapshot,
    ) -> None:
        """
        Restore Counter state from a snapshot.

        Parameters
        ----------
        snapshot
            MetricSnapshot.
        """

        super().restore(snapshot)

        self.validate()


    def clone(
        self,
    ) -> "Counter":
        """
        Deep clone this Counter.

        Returns
        -------
        Counter
        """

        clone = super().clone()

        clone.validate()

        return clone


    def copy(
        self,
    ) -> "Counter":
        """
        Alias of clone().

        Returns
        -------
        Counter
        """

        return self.clone()
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def freeze(
        self,
    ) -> None:
        """
        Freeze this Counter.

        Frozen counters reject all future updates
        until unfreeze() is called.
        """

        super().freeze()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze this Counter.
        """

        super().unfreeze()


    def enable(
        self,
    ) -> None:
        """
        Enable this Counter.
        """

        super().enable()


    def disable(
        self,
    ) -> None:
        """
        Disable this Counter.

        Disabled counters reject update operations
        but remain readable.
        """

        super().disable()


    def close(
        self,
    ) -> None:
        """
        Permanently close this Counter.

        Closed counters become read-only.
        """

        super().close()


    def reopen(
        self,
    ) -> None:
        """
        Reopen a previously closed Counter.

        Mainly intended for runtime recovery,
        checkpoint restoration,
        or testing.
        """

        super().reopen()
    # ======================================================
    # Part 6. Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the current Counter state.

        This performs Counter-specific validation
        in addition to the generic Metric validation.
        """

        # Generic metric validation
        if hasattr(super(), "validate"):
            super().validate()

        self.validate_value(
            self._value,
        )


    def validate_increment(
        self,
        amount: int | float,
    ) -> None:
        """
        Validate an increment value.

        Parameters
        ----------
        amount
            Increment amount.

        Raises
        ------
        TypeError
            If the increment is not numeric.

        ValueError
            If the increment is negative.
        """

        if not isinstance(
            amount,
            (int, float),
        ):
            raise TypeError(
                "Counter increment must be numeric."
            )

        if amount < 0:
            raise ValueError(
                "Counter increment cannot be negative."
            )


    def validate_value(
        self,
        value: int | float,
    ) -> None:
        """
        Validate the current Counter value.

        Parameters
        ----------
        value
            Counter value.

        Raises
        ------
        TypeError
            If the value is not numeric.

        ValueError
            If the value is negative.
        """

        if not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                "Counter value must be numeric."
            )

        if value < 0:
            raise ValueError(
                "Counter value cannot be negative."
            )
    # ======================================================
    # Part 7. Diagnostics
    # ======================================================

    @property
    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Runtime statistics for this Counter.
        """

        base: dict[str, Any] = {}

        if hasattr(super(), "statistics"):
            base.update(super().statistics)

        base.update(
            {
                "metric_type": "counter",
                "value": self._value,
                "total": self._value,
                "count": self._update_count,
                "created_at": self._created_at,
                "updated_at": self._updated_at,
                "revision": self._revision,
                "dirty": self._dirty,
            }
        )

        return base


    @property
    def health(
        self,
    ) -> dict[str, Any]:
        """
        Health report for this Counter.
        """

        base: dict[str, Any] = {}

        if hasattr(super(), "health"):
            base.update(super().health)

        issues: list[str] = list(
            base.get("issues", [])
        )

        if self._value < 0:
            issues.append(
                "negative_value"
            )

        base.update(
            {
                "healthy": len(issues) == 0,
                "issues": issues,
                "metric_type": "counter",
                "value": self._value,
            }
        )

        return base


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Dump complete runtime state.
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "metric_type": "counter",
            "value": self._value,
            "total": self.total,
            "count": self.count,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "revision": self._revision,
            "dirty": self._dirty,
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Return a comprehensive diagnostic report.
        """

        return {
            "identity": {
                "id": str(self.id),
                "name": self.name,
                "type": "counter",
            },
            "runtime": {
                "value": self._value,
                "total": self.total,
                "count": self.count,
                "revision": self._revision,
                "dirty": self._dirty,
            },
            "lifecycle": {
                "enabled": self._enabled,
                "frozen": self._frozen,
                "closed": self._closed,
            },
            "statistics": self.statistics,
            "health": self.health,
        }
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize this Counter to a dictionary.
        """

        return {
            "id": str(self.id),
            "metric_type": "counter",
            "name": self.name,
            "value": self._value,
            "revision": self._revision,
            "enabled": self._enabled,
            "frozen": self._frozen,
            "closed": self._closed,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Counter":
        """
        Construct a Counter from a dictionary.
        """

        descriptor = MetricDescriptor(
            name=data["name"],
            metric_type="counter",
            metadata=MetricMetadata.from_dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )

        counter = cls(
            descriptor=descriptor,
            labels=MetricLabels.from_dict(
                data.get(
                    "labels",
                    {},
                )
            ),
            attributes=MetricAttributes.from_dict(
                data.get(
                    "attributes",
                    {},
                )
            ),
        )

        counter._value = data.get(
            "value",
            0,
        )

        counter._revision = data.get(
            "revision",
            0,
        )

        counter._enabled = data.get(
            "enabled",
            True,
        )

        counter._frozen = data.get(
            "frozen",
            False,
        )

        counter._closed = data.get(
            "closed",
            False,
        )

        if "created_at" in data:
            counter._created_at = datetime.fromisoformat(
                data["created_at"]
            )

        if "updated_at" in data:
            counter._updated_at = datetime.fromisoformat(
                data["updated_at"]
            )

        return counter


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize this Counter to JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            sort_keys=True,
        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "Counter":
        """
        Construct a Counter from JSON.
        """

        return cls.from_dict(
            json.loads(
                payload,
            )
        )
    # ======================================================
    # Part 9. Export
    # ======================================================

    def prometheus(
        self,
    ) -> str:
        """
        Export this Counter in Prometheus exposition format.

        Returns
        -------
        str
        """

        labels = self.labels.to_dict()

        if labels:

            label_text = ",".join(

                f'{key}="{value}"'

                for key, value in sorted(
                    labels.items()
                )

            )

            return (
                f"{self.name}"
                f"{{{label_text}}} "
                f"{self.value}"
            )

        return (
            f"{self.name} "
            f"{self.value}"
        )


    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export as an OpenTelemetry-compatible record.

        Returns
        -------
        dict[str, Any]
        """

        return {

            "name": self.name,

            "description": self.metadata.description,

            "unit": self.metadata.unit,

            "type": "counter",

            "value": self.value,

            "timestamp": self.updated_at.isoformat(),

            "labels": self.labels.to_dict(),

            "attributes": self.attributes.to_dict(),

            "metadata": self.metadata.to_dict(),

        }


    def csv(
        self,
    ) -> list[Any]:
        """
        Export as a CSV row.

        Returns
        -------
        list[Any]
        """

        return [

            str(self.id),

            self.name,

            "counter",

            self.value,

            self.created_at.isoformat(),

            self.updated_at.isoformat(),

            json.dumps(
                self.labels.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
            ),

            json.dumps(
                self.attributes.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
            ),

            json.dumps(
                self.metadata.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
            ),

        ]
    # ======================================================
    # Part 10. Final Polish
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"value={self.value!r}, "
            f"enabled={self.enabled}, "
            f"frozen={self.frozen}, "
            f"closed={self.closed})"
        )


    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return str(self.value)


    def __int__(
        self,
    ) -> int:
        """
        Convert Counter to integer.
        """

        return int(self.value)


    def __float__(
        self,
    ) -> float:
        """
        Convert Counter to float.
        """

        return float(self.value)


    def __bool__(
        self,
    ) -> bool:
        """
        Truth value of this Counter.
        """

        return self.value > 0


    # ======================================================
    # Compatibility
    # ======================================================

    @property
    def total(
        self,
    ) -> int:
        """
        Compatibility alias for value.
        """

        return self.value


    @property
    def count(
        self,
    ) -> int:
        """
        Compatibility alias for value.
        """

        return self.value


    @property
    def metric_type(
        self,
    ) -> str:
        """
        Metric type.

        Compatibility helper.
        """

        return self.descriptor.metric_type


    @property
    def kind(
        self,
    ) -> str:
        """
        Compatibility alias.
        """

        return self.descriptor.kind


    @property
    def is_counter(
        self,
    ) -> bool:
        """
        Convenience type check.
        """

        return True                                                                            