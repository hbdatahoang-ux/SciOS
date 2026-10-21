"""
SciOS-NG Metrics Core
=====================

Low-level building blocks for the Metrics subsystem.

This package intentionally exposes only immutable/core components.

Runtime objects (Metric, MetricState, MetricSnapshot, MetricHooks)
are exported by the parent metrics package.
"""

from __future__ import annotations

# ---------------------------------------------------------------------
# Descriptor & Metadata
# ---------------------------------------------------------------------

from .descriptor import MetricDescriptor
from .metadata import MetricMetadata

# ---------------------------------------------------------------------
# Labels & Attributes
# ---------------------------------------------------------------------

from .labels import MetricLabels
from .attributes import MetricAttributes

# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

from .validation import MetricValidator

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

from .exceptions import (
    MetricError,
    MetricValidationError,

    InvalidMetricName,
    InvalidMetricValue,
    InvalidMetricUnit,
    InvalidMetricLabel,
    InvalidMetricAttribute,
    InvalidMetricMetadata,

    MetricStateError,
    MetricFrozenError,
    MetricDisabledError,
    MetricClosedError,

    MetricSnapshotError,
    MetricSerializationError,

    MetricRegistryError,
    MetricAlreadyExists,
    MetricNotFound,

    MetricCollectorError,
    MetricExporterError,
)

__all__ = [

    "MetricDescriptor",
    "MetricMetadata",
    "MetricLabels",
    "MetricAttributes",
    "MetricValidator",

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

__version__ = "0.1.0"