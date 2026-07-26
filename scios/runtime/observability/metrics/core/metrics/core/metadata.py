"""
SciOS-NG Metrics Core - Metadata
================================

Metadata container for Metric objects.

Design goals
------------
- Type-safe
- Validation-aware
- Snapshot-friendly
- Serializable
- Immutable-friendly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .validation import MetricValidator

__all__ = [
    "MetricMetadata",
]


@dataclass(slots=True)
class MetricMetadata:
    """
    Immutable-style metadata describing a Metric.
    """

    name: str

    description: str = ""

    unit: str = ""

    namespace: str = ""

    category: str = ""

    owner: str = ""

    version: str = "1.0"

    tags: tuple[str, ...] = ()

    extras: dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def __post_init__(self) -> None:

        self.name = MetricValidator.validate_name(self.name)

        self.unit = MetricValidator.validate_unit(self.unit)

        self.description = str(self.description)

        self.namespace = str(self.namespace)

        self.category = str(self.category)

        self.owner = str(self.owner)

        self.version = str(self.version)

        self.tags = tuple(map(str, self.tags))

        self.extras = MetricValidator.validate_metadata(
            self.extras
        )

    # ---------------------------------------------------------
    # Copy
    # ---------------------------------------------------------

    def copy(
        self,
        **updates: Any,
    ) -> "MetricMetadata":
        """
        Return a modified copy.
        """

        data = self.to_dict()

        data.update(updates)

        return MetricMetadata(**data)

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "namespace": self.namespace,
            "category": self.category,
            "owner": self.owner,
            "version": self.version,
            "tags": list(self.tags),
            "extras": dict(self.extras),
        }

    # ---------------------------------------------------------
    # Rich API
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"MetricMetadata("
            f"name={self.name!r}, "
            f"unit={self.unit!r})"
        )

    def __str__(self) -> str:

        return self.name