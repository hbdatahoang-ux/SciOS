"""
SciOS Observability
==================

Gauge Metric

Part 1
------

Foundation

Responsibilities
----------------

- Gauge metric implementation
- Runtime construction
- Default value
- Runtime validation

A Gauge represents a numeric value that may
increase or decrease over time.

Examples
--------

CPU Usage
Memory Usage
Temperature
Queue Length
Battery Level
"""

from __future__ import annotations

from numbers import Real
from typing import Any

from .metric import Metric
from .descriptor import MetricDescriptor
from .metadata import MetricMetadata
from .labels import MetricLabels
from .attributes import MetricAttributes

__all__ = [
    "Gauge",
]


# ==========================================================
# Gauge
# ==========================================================


class Gauge(Metric):
    """
    Numeric metric whose value may both increase
    and decrease.

    Unlike Counter, Gauge supports arbitrary
    assignment via set() and update().
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
        initial_value: Real = 0,
    ) -> None:
        """
        Initialize a Gauge.

        Parameters
        ----------
        descriptor:
            Metric descriptor.

        metadata:
            Runtime metadata.

        labels:
            Metric labels.

        attributes:
            Runtime attributes.

        initial_value:
            Initial gauge value.
        """

        super().__init__(
            descriptor=descriptor,
            metadata=metadata,
            labels=labels,
            attributes=attributes,
        )

        self.validate_value(
            initial_value,
        )

        self._value = initial_value

        self._previous_value = None

        self._dirty = False

    # ======================================================
    # Default Value
    # ======================================================

    @staticmethod
    def _default_value() -> int:
        """
        Default Gauge value.
        """

        return 0

    # ======================================================
    # Runtime Validation
    # ======================================================

    @staticmethod
    def validate_value(
        value: Any,
    ) -> None:
        """
        Validate a Gauge value.

        Parameters
        ----------
        value:
            Value to validate.

        Raises
        ------
        TypeError
            If value is not numeric.
        """

        if not isinstance(
            value,
            Real,
        ):
            raise TypeError(
                "Gauge value must be numeric."
            )

    @classmethod
    def validate_runtime(
        cls,
        value: Any,
    ) -> bool:
        """
        Runtime validation helper.

        Returns
        -------
        bool
        """

        try:

            cls.validate_value(
                value,
            )

            return True

        except Exception:

            return False
    # ======================================================
    # Part 2. Gauge API
    # ======================================================

    def get(
        self,
    ) -> Real:
        """
        Return the current Gauge value.

        Returns
        -------
        Real
            Current numeric value.
        """

        return self.value


    def set(
        self,
        value: Real,
    ) -> None:
        """
        Set the Gauge to a new value.

        Parameters
        ----------
        value:
            New numeric value.
        """

        self.validate_value(
            value,
        )

        super().set(
            value,
        )


    def update(
        self,
        value: Real,
    ) -> None:
        """
        Update the Gauge.

        Alias of set().

        Parameters
        ----------
        value:
            New numeric value.
        """

        self.set(
            value,
        )


    def inc(
        self,
        amount: Real = 1,
    ) -> Real:
        """
        Increase the Gauge.

        Parameters
        ----------
        amount:
            Increment amount.

        Returns
        -------
        Real
            Updated value.
        """

        self.validate_value(
            amount,
        )

        new_value = self.value + amount

        self.set(
            new_value,
        )

        return self.value


    def dec(
        self,
        amount: Real = 1,
    ) -> Real:
        """
        Decrease the Gauge.

        Parameters
        ----------
        amount:
            Decrement amount.

        Returns
        -------
        Real
            Updated value.
        """

        self.validate_value(
            amount,
        )

        new_value = self.value - amount

        self.set(
            new_value,
        )

        return self.value


    def reset(
        self,
    ) -> None:
        """
        Reset the Gauge to its default value.
        """

        self.set(
            self._default_value(),
        )
    # ======================================================
    # Part 3. Properties
    # ======================================================

    @property
    def value(
        self,
    ) -> Real:
        """
        Current Gauge value.

        Returns
        -------
        Real
            Current numeric value.
        """

        return self._value


    @property
    def created_at(
        self,
    ):
        """
        Gauge creation timestamp.

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
        Last update timestamp.

        Returns
        -------
        datetime
        """

        return self._updated_at


    @property
    def revision(
        self,
    ) -> int:
        """
        Runtime revision number.

        Increased whenever the Gauge state changes.
        """

        return self._revision


    @property
    def dirty(
        self,
    ) -> bool:
        """
        Whether the Gauge has been modified since
        the last checkpoint or snapshot.
        """

        return self._dirty
    # ======================================================
    # Part 4. Snapshot
    # ======================================================

    def snapshot(
        self,
    ) -> MetricSnapshot:
        """
        Create an immutable snapshot of this Gauge.

        Returns
        -------
        MetricSnapshot
        """

        return MetricSnapshot.create(

            name=self.name,

            value=self.value,

            metric_type="gauge",

            labels=self.labels.to_dict(),

            attributes=self.attributes.to_dict(),

            metadata=self.metadata.to_dict(),

        )


    def restore(
        self,
        snapshot: MetricSnapshot,
    ) -> None:
        """
        Restore Gauge state from a snapshot.

        Parameters
        ----------
        snapshot:
            Source snapshot.
        """

        if snapshot.metric_type != "gauge":
            raise TypeError(
                "Snapshot is not a Gauge snapshot."
            )

        self.set(
            snapshot.value,
        )

        self.labels.clear()
        self.labels.update(
            snapshot.labels.to_dict(),
        )

        self.attributes.clear()
        self.attributes.update(
            snapshot.attributes.to_dict(),
        )

        self.metadata.clear()
        self.metadata.update(
            snapshot.metadata.to_dict(),
        )


    def clone(
        self,
    ) -> "Gauge":
        """
        Deep clone this Gauge.

        Returns
        -------
        Gauge
        """

        clone = self.__class__(

            descriptor=self.descriptor.copy(),

            metadata=self.metadata.copy(),

            labels=self.labels.copy(),

            attributes=self.attributes.copy(),

            initial_value=self.value,

        )

        return clone


    def copy(
        self,
    ) -> "Gauge":
        """
        Alias of clone().

        Returns
        -------
        Gauge
        """

        return self.clone()
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def freeze(
        self,
    ) -> None:
        """
        Freeze this Gauge.

        A frozen Gauge cannot be modified until
        unfreeze() is called.
        """

        super().freeze()


    def unfreeze(
        self,
    ) -> None:
        """
        Unfreeze this Gauge.
        """

        super().unfreeze()


    def enable(
        self,
    ) -> None:
        """
        Enable this Gauge.
        """

        super().enable()


    def disable(
        self,
    ) -> None:
        """
        Disable this Gauge.

        Disabled Gauges reject future updates but
        preserve their runtime state.
        """

        super().disable()


    def close(
        self,
    ) -> None:
        """
        Permanently close this Gauge.

        Closed Gauges become read-only.
        """

        super().close()


    def reopen(
        self,
    ) -> None:
        """
        Reopen a previously closed Gauge.

        Mainly used for runtime recovery.
        """

        super().reopen()
    # ======================================================
    # Part 6. Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate the current Gauge state.

        Raises
        ------
        TypeError
            If the value is invalid.
        """

        self.validate_value(
            self.value,
        )


    @staticmethod
    def validate_value(
        value: Any,
    ) -> None:
        """
        Validate a Gauge value.

        Parameters
        ----------
        value:
            Value to validate.

        Raises
        ------
        TypeError
            If the value is not numeric.
        """

        if not isinstance(
            value,
            Real,
        ):
            raise TypeError(
                "Gauge value must be numeric."
            )


    @staticmethod
    def validate_delta(
        delta: Any,
    ) -> None:
        """
        Validate an increment/decrement amount.

        Parameters
        ----------
        delta:
            Increment or decrement value.

        Raises
        ------
        TypeError
            If delta is not numeric.
        """

        if not isinstance(
            delta,
            Real,
        ):
            raise TypeError(
                "Gauge delta must be numeric."
            )


    @staticmethod
    def validate_numeric(
        value: Any,
    ) -> bool:
        """
        Check whether a value is numeric.

        Parameters
        ----------
        value:
            Value to check.

        Returns
        -------
        bool
        """

        return isinstance(
            value,
            Real,
        )
    # ======================================================
    # Part 7. Diagnostics
    # ======================================================

    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime statistics for this Gauge.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "name": self.name,
            "metric_type": "gauge",
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "revision": self.revision,
            "update_count": self.update_count,
            "dirty": self.dirty,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
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

        issues: list[str] = []

        if self.closed:
            issues.append("closed")

        if not self.enabled:
            issues.append("disabled")

        if self.frozen:
            issues.append("frozen")

        return {
            "healthy": len(issues) == 0,
            "status": (
                "healthy"
                if not issues
                else "degraded"
            ),
            "issues": issues,
        }


    def dump(
        self,
    ) -> dict[str, Any]:
        """
        Return a complete runtime dump.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "metric_type": "gauge",
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "revision": self.revision,
            "update_count": self.update_count,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


    def inspect(
        self,
    ) -> dict[str, Any]:
        """
        Return a production-friendly inspection report.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "descriptor": self.descriptor.name,
            "statistics": self.statistics(),
            "health": self.health(),
            "runtime": {
                "revision": self.revision,
                "dirty": self.dirty,
                "enabled": self.enabled,
                "frozen": self.frozen,
                "closed": self.closed,
            },
        }
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize this Gauge to a dictionary.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "id": str(self.id),
            "type": "gauge",
            "name": self.name,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "revision": self.revision,
            "update_count": self.update_count,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "labels": self.labels.to_dict(),
            "attributes": self.attributes.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Gauge":
        """
        Construct a Gauge from a dictionary.

        Parameters
        ----------
        data
            Serialized Gauge.

        Returns
        -------
        Gauge
        """

        descriptor = MetricDescriptor(
            name=data["name"],
            metric_type="gauge",
            metadata=MetricMetadata.from_dict(
                data.get("metadata", {})
            ),
        )

        gauge = cls(
            descriptor=descriptor,
            labels=MetricLabels.from_dict(
                data.get("labels", {})
            ),
            attributes=MetricAttributes.from_dict(
                data.get("attributes", {})
            ),
        )

        gauge.set(
            data.get("value", 0.0)
        )

        return gauge


    def to_json(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize Gauge to JSON.

        Parameters
        ----------
        indent
            JSON indentation.

        Returns
        -------
        str
        """

        import json

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
    ) -> "Gauge":
        """
        Deserialize Gauge from JSON.

        Parameters
        ----------
        payload
            JSON string.

        Returns
        -------
        Gauge
        """

        import json

        return cls.from_dict(
            json.loads(payload)
        )
    # ======================================================
    # Part 9. Export
    # ======================================================

    def prometheus(
        self,
    ) -> str:
        """
        Export this Gauge in Prometheus exposition format.

        Returns
        -------
        str
        """

        labels = ""

        if len(self.labels):

            labels = (
                "{"
                + ",".join(
                    f'{k}="{v}"'
                    for k, v in sorted(
                        self.labels.items()
                    )
                )
                + "}"
            )

        return (
            f"{self.name}"
            f"{labels} "
            f"{self.value}"
        )


    def otel(
        self,
    ) -> dict[str, Any]:
        """
        Export this Gauge as an OpenTelemetry-compatible
        dictionary.

        Returns
        -------
        dict[str, Any]
        """

        return {
            "name": self.name,
            "description": self.metadata.description,
            "unit": self.metadata.unit,
            "type": "gauge",
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
        Export this Gauge as a CSV row.

        Returns
        -------
        list[Any]
        """

        return [
            self.name,
            "gauge",
            self.value,
            self.updated_at.isoformat(),
            self.revision,
            self.update_count,
            self.metadata.unit,
            self.metadata.description,
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
            f"revision={self.revision}, "
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
        Integer conversion.
        """

        if self.value is None:
            return 0

        return int(self.value)


    def __float__(
        self,
    ) -> float:
        """
        Floating-point conversion.
        """

        if self.value is None:
            return 0.0

        return float(self.value)


    def __bool__(
        self,
    ) -> bool:
        """
        Truthiness.

        Returns False only when the value evaluates
        to False.
        """

        return bool(self.value)


    @property
    def compatibility(
        self,
    ) -> dict[str, bool]:
        """
        Runtime compatibility information.

        Useful for exporters, registries,
        collectors and monitoring pipelines.
        """

        return {
            "metric": True,
            "gauge": True,
            "counter": False,
            "histogram": False,
            "summary": False,
            "timer": False,
            "snapshot": True,
            "serialization": True,
            "prometheus": True,
            "opentelemetry": True,
            "csv": True,
            "thread_safe": True,
            "mutable": (
                self.enabled
                and not self.frozen
                and not self.closed
            ),
        }                                                                            