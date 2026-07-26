"""
SciOS-NG Metrics Core
=====================

Core building blocks for the Metrics subsystem.

Exports
-------
- Metric
- MetricState
- MetricSnapshot
- MetricHooks
- MetricDescriptor
- MetricMetadata
- MetricLabels
- MetricAttributes
- MetricValidator
- Metric exceptions
"""

from __future__ import annotations

# ---------------------------------------------------------------------
# Core Objects
# ---------------------------------------------------------------------

from .metric import Metric
from .metric_state import MetricState
from .metric_snapshot import MetricSnapshot
from .metric_hooks import MetricHooks

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
    MetricException,
    InvalidMetricName,
    InvalidUnit,
    InvalidLabel,
    InvalidAttribute,
    InvalidState,
    SnapshotError,
    RegistryError,
    CollectorError,
    ExporterError,
)

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    # Core
    "Metric",
    "MetricState",
    "MetricSnapshot",
    "MetricHooks",

    # Descriptor
    "MetricDescriptor",
    "MetricMetadata",

    # Labels
    "MetricLabels",
    "MetricAttributes",

    # Validation
    "MetricValidator",

    # Exceptions
    "MetricException",
    "InvalidMetricName",
    "InvalidUnit",
    "InvalidLabel",
    "InvalidAttribute",
    "InvalidState",
    "SnapshotError",
    "RegistryError",
    "CollectorError",
    "ExporterError",
]

# ---------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------

__version__ = "0.1.0"