"""
SciOS-NG Metrics Core - Descriptor
=================================

Metric descriptor defining the immutable identity of a metric.

A descriptor contains all static information describing a metric.
Runtime values are stored separately in MetricState.

Design goals
------------
- Immutable
- Hashable
- Serializable
- Validation-aware
- Thread-safe
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .metadata import MetricMetadata

__all__ = [
    "MetricDescriptor",
]


@dataclass(slots=True, frozen=True)
class MetricDescriptor:
    """
    Immutable descriptor for a Metric.

    Parameters
    ----------
    metadata:
        Metric metadata.

    metric_type:
        counter, gauge, histogram, summary...

    value_type:
        Python type of the runtime value.

    enabled:
        Whether this descriptor is active.
    """

    metadata: MetricMetadata

    metric_type: str = "gauge"

    value_type: type = float

    enabled: bool = True

    extras: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def unit(self) -> str:
        return self.metadata.unit

    @property
    def description(self) -> str:
        return self.metadata.description

    @property
    def namespace(self) -> str:
        return self.metadata.namespace

    @property
    def category(self) -> str:
        return self.metadata.category

    @property
    def owner(self) -> str:
        return self.metadata.owner

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def tags(self) -> tuple[str, ...]:
        return self.metadata.tags

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "metadata": self.metadata.to_dict(),
            "metric_type": self.metric_type,
            "value_type": self.value_type.__name__,
            "enabled": self.enabled,
            "extras": dict(self.extras),
        }

    # ---------------------------------------------------------
    # Copy
    # ---------------------------------------------------------

    def copy(
        self,
        **updates: Any,
    ) -> "MetricDescriptor":

        data = {
            "metadata": self.metadata,
            "metric_type": self.metric_type,
            "value_type": self.value_type,
            "enabled": self.enabled,
            "extras": dict(self.extras),
        }

        data.update(updates)

        return MetricDescriptor(**data)

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"type={self.metric_type!r}, "
            f"value_type={self.value_type.__name__})"
        )