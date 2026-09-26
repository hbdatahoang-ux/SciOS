"""
SciOS-NG Metrics Core - Exceptions
==================================

Exception hierarchy for the Metrics subsystem.

Design goals
------------
- Single root exception for all metric-related failures.
- Rich contextual information for debugging.
- Stable API for future extensions.
- Production-ready and fully typed.
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "MetricError",
    "MetricValidationError",
    "InvalidMetricName",
    "InvalidMetricValue",
    "InvalidMetricUnit",
    "InvalidMetricLabel",
    "InvalidMetricAttribute",
    "InvalidMetricMetadata",
    "MetricStateError",
    "MetricFrozenError",
    "MetricDisabledError",
    "MetricClosedError",
    "MetricSnapshotError",
    "MetricSerializationError",
    "MetricRegistryError",
    "MetricAlreadyExists",
    "MetricNotFound",
    "MetricCollectorError",
    "MetricExporterError",
]


class MetricError(Exception):
    """
    Base class for all metric exceptions.
    """

    def __init__(
        self,
        message: str = "",
        *,
        metric: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:

        self.metric = metric
        self.context = context or {}

        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0] if self.args else ""

    def __str__(self) -> str:

        text = self.message

        if self.metric:
            text += f" [metric={self.metric}]"

        if self.context:
            text += f" {self.context}"

        return text


# ==========================================================
# Validation
# ==========================================================


class MetricValidationError(MetricError):
    """Base validation error."""


class InvalidMetricName(MetricValidationError):
    """Invalid metric name."""


class InvalidMetricValue(MetricValidationError):
    """Invalid metric value."""


class InvalidMetricUnit(MetricValidationError):
    """Invalid metric unit."""


class InvalidMetricLabel(MetricValidationError):
    """Invalid metric label."""


class InvalidMetricAttribute(MetricValidationError):
    """Invalid metric attribute."""


class InvalidMetricMetadata(MetricValidationError):
    """Invalid metadata."""


# ==========================================================
# Runtime State
# ==========================================================


class MetricStateError(MetricError):
    """Base state error."""


class MetricFrozenError(MetricStateError):
    """Metric is frozen."""


class MetricDisabledError(MetricStateError):
    """Metric is disabled."""


class MetricClosedError(MetricStateError):
    """Metric has been closed."""


# ==========================================================
# Snapshot
# ==========================================================


class MetricSnapshotError(MetricError):
    """Snapshot operation failed."""


class MetricSerializationError(MetricSnapshotError):
    """Serialization or deserialization failed."""


# ==========================================================
# Registry
# ==========================================================


class MetricRegistryError(MetricError):
    """Registry operation failed."""


class MetricAlreadyExists(MetricRegistryError):
    """Metric already exists."""


class MetricNotFound(MetricRegistryError):
    """Metric not found."""


# ==========================================================
# Collector
# ==========================================================


class MetricCollectorError(MetricError):
    """Collector failure."""


# ==========================================================
# Exporter
# ==========================================================


class MetricExporterError(MetricError):
    """Exporter failure."""