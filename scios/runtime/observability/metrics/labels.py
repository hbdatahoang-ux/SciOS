"""
SciOS Runtime Metrics Labels
============================

Metric label model.

Responsibilities
-----------------
- Store metric dimensions.
- Validate label keys.
- Normalize label values.
- Provide controlled label operations.
- Support metric metadata and descriptors.
- Support serialization and exporters.

Examples
--------
    labels = MetricLabels(
        service="runtime",
        component="scheduler",
    )

Python 3.11+
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any


__all__ = [
    "MetricLabels",
]


# ==============================================================================
# Validation
# ==============================================================================


def _normalize_key(key: str) -> str:
    """
    Normalize and validate a metric label key.

    Parameters
    ----------
    key:
        Label key.

    Returns
    -------
    str
        Normalized label key.

    Raises
    ------
    TypeError
        If key is not a string.
    ValueError
        If key is empty after normalization.
    """

    if not isinstance(key, str):
        raise TypeError(
            "label key must be a string"
        )

    normalized = key.strip()

    if not normalized:
        raise ValueError(
            "label key cannot be empty"
        )

    return normalized


def _normalize_value(value: Any) -> str:
    """
    Normalize a metric label value.

    Metric label values are represented as strings so that the
    resulting representation is suitable for exporters such as
    Prometheus and OpenTelemetry.
    """

    return str(value)


# ==============================================================================
# MetricLabels
# ==============================================================================


@dataclass(slots=True)
class MetricLabels:
    """
    Container for metric labels.

    Labels represent dimensions associated with a metric.

    Examples
    --------
    >>> labels = MetricLabels(
    ...     service="runtime",
    ...     component="scheduler",
    ... )

    >>> labels["service"]
    'runtime'

    >>> labels.set("worker", 1)

    >>> labels.to_dict()
    {'service': 'runtime', 'component': 'scheduler', 'worker': '1'}
    """

    _values: dict[str, str] = field(
        default_factory=dict,
        repr=False,
    )

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def __init__(
        self,
        **labels: Any,
    ) -> None:
        """
        Create a MetricLabels instance.

        All keys and values pass through normalization.
        """

        self._values = {}

        self.update(labels)

    # ==========================================================================
    # Core mutation
    # ==========================================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set or replace a label.

        Parameters
        ----------
        key:
            Label key.
        value:
            Label value.
        """

        normalized_key = _normalize_key(key)
        normalized_value = _normalize_value(value)

        self._values[normalized_key] = normalized_value

    def update(
        self,
        labels: Mapping[str, Any],
    ) -> None:
        """
        Add or replace multiple labels.
        """

        if not isinstance(labels, Mapping):
            raise TypeError(
                "labels must be a mapping"
            )

        for key, value in labels.items():
            self.set(key, value)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a label.

        Missing labels are ignored.
        """

        normalized_key = _normalize_key(key)

        self._values.pop(
            normalized_key,
            None,
        )

    def clear(self) -> None:
        """
        Remove all labels.
        """

        self._values.clear()

    # ==========================================================================
    # Access
    # ==========================================================================

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Get a label value.
        """

        normalized_key = _normalize_key(key)

        return self._values.get(
            normalized_key,
            default,
        )

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Return True if the label exists.
        """

        normalized_key = _normalize_key(key)

        return normalized_key in self._values

    def keys(self):
        """
        Return label keys.
        """

        return self._values.keys()

    def items(self):
        """
        Return label key/value pairs.
        """

        return self._values.items()

    def values(self):
        """
        Return label values.
        """

        return self._values.values()

    # ==========================================================================
    # Merge
    # ==========================================================================

    def merge(
        self,
        other: MetricLabels | Mapping[str, Any],
    ) -> MetricLabels:
        """
        Return a new label set containing both label collections.

        Labels from ``other`` take precedence when keys collide.

        The current instance is not modified.
        """

        if isinstance(other, MetricLabels):
            other_values = other._values

        elif isinstance(other, Mapping):
            other_values = other

        else:
            raise TypeError(
                "other must be MetricLabels or a mapping"
            )

        result = self.copy()

        result.update(other_values)

        return result

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, str]:
        """
        Return a detached dictionary representation.

        The returned dictionary can be safely modified without
        changing this MetricLabels instance.
        """

        return dict(self._values)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> MetricLabels:
        """
        Construct labels from a mapping.
        """

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping"
            )

        return cls(**dict(data))

    # ==========================================================================
    # Copy
    # ==========================================================================

    def copy(self) -> MetricLabels:
        """
        Return an independent copy.
        """

        result = MetricLabels()

        result._values = dict(
            self._values
        )

        return result

    # ==========================================================================
    # Protocols
    # ==========================================================================

    def __getitem__(
        self,
        key: str,
    ) -> str:
        """
        Get a label using mapping syntax.
        """

        normalized_key = _normalize_key(key)

        return self._values[normalized_key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a label using mapping syntax.
        """

        self.set(
            key,
            value,
        )

    def __delitem__(
        self,
        key: str,
    ) -> None:
        """
        Delete a label using mapping syntax.
        """

        normalized_key = _normalize_key(key)

        del self._values[normalized_key]

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Support ``key in labels``.
        """

        if not isinstance(key, str):
            return False

        return key.strip() in self._values

    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate over label keys.
        """

        return iter(self._values)

    def __len__(
        self,
    ) -> int:
        """
        Return the number of labels.
        """

        return len(self._values)

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return deterministic debug representation.
        """

        return (
            "MetricLabels("
            f"{self._values!r}"
            ")"
        )