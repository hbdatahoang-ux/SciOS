"""
SciOS-NG Runtime Observability

Metric Schema

metric_schema.py

Part 1
Foundation

Provides

    • imports
    • constants
    • enums
    • type aliases
    • utilities

This module defines the canonical Metric schema used
throughout the SciOS runtime observability stack.

MetricSchema is shared by

    • Runtime
    • Metrics Engine
    • Dashboard
    • CLI
    • Exporters
    • Prometheus
    • OpenTelemetry
"""

from __future__ import annotations

import json
import math
import statistics
import time
import uuid

from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeAlias,
    Union,
)

# ==========================================================
# Package Metadata
# ==========================================================

__all__ = [

    # Enums

    "MetricType",
    "MetricUnit",
    "MetricStatus",

    # Type Aliases

    "MetricID",
    "MetricValue",
    "MetricDict",
    "MetricList",
    "MetricTags",
    "MetricAttributes",

    # Constants

    "METRIC_VERSION",

    # Utilities

    "generate_metric_id",
    "utc_now",
    "timestamp",
    "ensure_path",
    "pretty_json",
    "enum_value",
    "dataclass_to_dict",
    "runtime_info",
]

__version__ = "0.1.0"

__author__ = "SciOS-NG"

__description__ = (
    "Runtime Metric Schema"
)

# ==========================================================
# Constants
# ==========================================================

METRIC_VERSION = "1.0"

DEFAULT_METRIC_NAME = "metric"

DEFAULT_NAMESPACE = "runtime"

DEFAULT_SERVICE_NAME = "SciOS"

DEFAULT_UNIT = "count"

DEFAULT_DESCRIPTION = ""

DEFAULT_ENCODING = "utf-8"

DEFAULT_TIMEOUT = 30.0

# ==========================================================
# Enums
# ==========================================================


class MetricStatus(str, Enum):
    """
    Runtime metric status.
    """

    CREATED = "created"

    ACTIVE = "active"

    INACTIVE = "inactive"

    DISABLED = "disabled"

    CLOSED = "closed"


class MetricType(str, Enum):
    """
    Metric categories.
    """

    COUNTER = "counter"

    GAUGE = "gauge"

    HISTOGRAM = "histogram"

    SUMMARY = "summary"

    TIMER = "timer"

    RATE = "rate"

    CUSTOM = "custom"


class MetricUnit(str, Enum):
    """
    Common metric units.
    """

    COUNT = "count"

    SECONDS = "seconds"

    MILLISECONDS = "milliseconds"

    MICROSECONDS = "microseconds"

    BYTES = "bytes"

    PERCENT = "percent"

    CELSIUS = "celsius"

    VOLTS = "volts"

    WATTS = "watts"

    NONE = "none"


# ==========================================================
# Type Aliases
# ==========================================================

MetricID: TypeAlias = str

MetricValue: TypeAlias = Union[
    int,
    float,
]

MetricDict: TypeAlias = Dict[
    str,
    Any,
]

MetricList: TypeAlias = List[
    MetricDict,
]

MetricTags: TypeAlias = Dict[
    str,
    Any,
]

MetricAttributes: TypeAlias = Dict[
    str,
    Any,
]

MetricFilter: TypeAlias = Callable[
    [MetricDict],
    bool,
]

# ==========================================================
# Utilities
# ==========================================================


def generate_metric_id() -> MetricID:
    """
    Generate a metric identifier.
    """

    return uuid.uuid4().hex


def timestamp() -> float:
    """
    Current UNIX timestamp.
    """

    return time.time()


def utc_now() -> str:
    """
    Current UTC ISO-8601 timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def ensure_path(
    path: str | Path,
) -> Path:
    """
    Normalize a filesystem path.
    """

    return Path(
        path
    ).expanduser().resolve()


def pretty_json(
    obj: Any,
) -> str:
    """
    Pretty JSON serialization.
    """

    return json.dumps(

        obj,

        indent=4,

        ensure_ascii=False,

        default=str,

    )


def enum_value(
    value: Any,
) -> Any:
    """
    Convert Enum into primitive value.
    """

    if isinstance(
        value,
        Enum,
    ):

        return value.value

    return value


def dataclass_to_dict(
    obj: Any,
) -> Dict[str, Any]:
    """
    Convert dataclass into dictionary.
    """

    try:

        return asdict(obj)

    except Exception:

        if hasattr(
            obj,
            "__dict__",
        ):

            return dict(
                obj.__dict__
            )

        return {

            "value": obj,

        }


def runtime_info() -> MetricDict:
    """
    Runtime information for this module.
    """

    return {

        "module":

            __name__,

        "version":

            __version__,

        "description":

            __description__,

        "metric_version":

            METRIC_VERSION,

        "default_namespace":

            DEFAULT_NAMESPACE,

        "default_service":

            DEFAULT_SERVICE_NAME,

        "supported_types":

            [

                item.value

                for item

                in MetricType

            ],

        "supported_units":

            [

                item.value

                for item

                in MetricUnit

            ],

        "supported_status":

            [

                item.value

                for item

                in MetricStatus

            ],

    }
# ==========================================================
# Part 2
# Dataclasses
#
# Provides
#     • MetricSchema
#     • MetricContext
#     • MetricMetadata
#
# Notes
# -----
# These dataclasses define the canonical runtime metric
# model used throughout the SciOS observability stack.
#
# MetricSchema is the fundamental metric object shared by
# Runtime, Dashboard, CLI and Exporters.
# ==========================================================

from dataclasses import dataclass, field


# ==========================================================
# Part 2.1
# Metric Context
# ==========================================================

@dataclass(slots=True)
class MetricContext:
    """
    Runtime metric context.

    Carries correlation and ownership information for a
    metric instance.
    """

    metric_id: MetricID = field(
        default_factory=generate_metric_id
    )

    trace_id: Optional[str] = None

    span_id: Optional[str] = None

    parent_metric_id: Optional[MetricID] = None

    service_name: str = DEFAULT_SERVICE_NAME

    namespace: str = DEFAULT_NAMESPACE

    metric_type: MetricType = MetricType.GAUGE

    unit: MetricUnit = MetricUnit.COUNT

    source: str = "runtime"

    labels: Dict[str, str] = field(
        default_factory=dict
    )

    baggage: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# Part 2.2
# Metric Metadata
# ==========================================================

@dataclass(slots=True)
class MetricMetadata:
    """
    Descriptive metadata for a metric.
    """

    name: str = DEFAULT_METRIC_NAME

    description: str = DEFAULT_DESCRIPTION

    version: str = METRIC_VERSION

    owner: str = "SciOS"

    category: str = "runtime"

    subsystem: str = "observability"

    environment: str = "production"

    host: Optional[str] = None

    process_id: Optional[int] = None

    thread_id: Optional[int] = None

    runtime: str = "SciOS"

    runtime_version: str = __version__

    language: str = "Python"

    tags: MetricTags = field(
        default_factory=dict
    )

    attributes: MetricAttributes = field(
        default_factory=dict
    )

    extras: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# Part 2.3
# Metric Schema
# ==========================================================

@dataclass(slots=True)
class MetricSchema:
    """
    Canonical runtime metric schema.

    Shared by

        • Runtime
        • Metrics Engine
        • Dashboard
        • CLI
        • Prometheus Exporter
        • OpenTelemetry Exporter
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: MetricID = field(
        default_factory=generate_metric_id
    )

    name: str = DEFAULT_METRIC_NAME

    type: MetricType = MetricType.GAUGE

    status: MetricStatus = MetricStatus.CREATED

    # ------------------------------------------------------
    # Core Models
    # ------------------------------------------------------

    context: MetricContext = field(
        default_factory=MetricContext
    )

    metadata: MetricMetadata = field(
        default_factory=MetricMetadata
    )

    # ------------------------------------------------------
    # Metric Value
    # ------------------------------------------------------

    value: MetricValue = 0.0

    previous_value: MetricValue = 0.0

    samples: List[MetricValue] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # Runtime Dictionaries
    # ------------------------------------------------------

    tags: MetricTags = field(
        default_factory=dict
    )

    attributes: MetricAttributes = field(
        default_factory=dict
    )

    diagnostics: Dict[str, Any] = field(
        default_factory=dict
    )

    extras: Dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------

    enabled: bool = True

    sampled: bool = True

    exported: bool = False

    # ------------------------------------------------------
    # Timing
    # ------------------------------------------------------

    created_at: float = field(
        default_factory=timestamp
    )

    updated_at: float = field(
        default_factory=timestamp
    )

    collected_at: Optional[float] = None

    # ------------------------------------------------------
    # Runtime Statistics
    # ------------------------------------------------------

    update_count: int = 0

    export_count: int = 0

    error_count: int = 0
# ==========================================================
# Part 3
# Constructor
#
# Provides
#     • __post_init__()
#     • validation
#     • normalization
#
# Notes
# -----
# Responsible for validating and normalizing MetricSchema
# immediately after construction.
# ==========================================================

    # ------------------------------------------------------
    # Part 3.1
    # Dataclass Initialization
    # ------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Finalize MetricSchema initialization.
        """

        self._normalize()

        self._validate()

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 3.2
    # Validation
    # ------------------------------------------------------

    def _validate(self) -> None:
        """
        Validate the internal state.

        Raises
        ------
        TypeError
            Invalid object type.

        ValueError
            Invalid value.
        """

        #
        # Identity
        #

        if not isinstance(self.id, str):

            raise TypeError(
                "Metric id must be a string."
            )

        self.id = self.id.strip()

        if not self.id:

            raise ValueError(
                "Metric id cannot be empty."
            )

        if not isinstance(self.name, str):

            raise TypeError(
                "Metric name must be a string."
            )

        self.name = self.name.strip()

        if not self.name:

            raise ValueError(
                "Metric name cannot be empty."
            )

        #
        # Enums
        #

        if not isinstance(
            self.type,
            MetricType,
        ):

            raise TypeError(
                "type must be MetricType."
            )

        if not isinstance(
            self.status,
            MetricStatus,
        ):

            raise TypeError(
                "status must be MetricStatus."
            )

        #
        # Context
        #

        if not isinstance(
            self.context,
            MetricContext,
        ):

            raise TypeError(
                "context must be MetricContext."
            )

        #
        # Metadata
        #

        if not isinstance(
            self.metadata,
            MetricMetadata,
        ):

            raise TypeError(
                "metadata must be MetricMetadata."
            )

        #
        # Numeric values
        #

        if not isinstance(
            self.value,
            (int, float),
        ):

            raise TypeError(
                "value must be numeric."
            )

        if not isinstance(
            self.previous_value,
            (int, float),
        ):

            raise TypeError(
                "previous_value must be numeric."
            )

        #
        # Samples
        #

        if not isinstance(
            self.samples,
            list,
        ):

            raise TypeError(
                "samples must be a list."
            )

        for sample in self.samples:

            if not isinstance(
                sample,
                (int, float),
            ):

                raise TypeError(
                    "Every sample must be numeric."
                )

        #
        # Dictionaries
        #

        for name in (

            "tags",
            "attributes",
            "diagnostics",
            "extras",

        ):

            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                dict,
            ):

                raise TypeError(
                    f"{name} must be a dictionary."
                )

        #
        # Counters
        #

        for name in (

            "update_count",
            "export_count",
            "error_count",

        ):

            value = getattr(
                self,
                name,
            )

            if value < 0:

                raise ValueError(
                    f"{name} cannot be negative."
                )

    # ------------------------------------------------------
    # Part 3.3
    # Normalization
    # ------------------------------------------------------

    def _normalize(self) -> None:
        """
        Normalize runtime values.
        """

        #
        # Identity
        #

        self.id = str(
            self.id
        ).strip()

        self.name = (
            str(self.name).strip()
            or DEFAULT_METRIC_NAME
        )

        #
        # Synchronize Context
        #

        self.context.metric_id = self.id

        self.context.metric_type = self.type

        #
        # Synchronize Metadata
        #

        self.metadata.name = self.name

        #
        # Merge tags
        #

        if self.metadata.tags:

            self.tags.update(
                self.metadata.tags
            )

        self.metadata.tags = self.tags

        #
        # Merge attributes
        #

        if self.metadata.attributes:

            self.attributes.update(
                self.metadata.attributes
            )

        self.metadata.attributes = (
            self.attributes
        )

        #
        # Normalize numeric values
        #

        self.value = float(
            self.value
        )

        self.previous_value = float(
            self.previous_value
        )

        self.samples = [

            float(v)

            for v

            in self.samples

        ]

        #
        # Runtime timestamps
        #

        if self.created_at <= 0:

            self.created_at = timestamp()

        if self.updated_at <= 0:

            self.updated_at = self.created_at
# ==========================================================
# Part 4
# Properties
#
# Provides
#     • value
#     • sample_count
#     • tag_count
#     • attribute_count
#     • enabled
#     • empty
#
# Notes
# -----
# Read-only computed properties describing the current
# runtime state of MetricSchema.
# ==========================================================

    # ------------------------------------------------------
    # Part 4.1
    # Value
    # ------------------------------------------------------

    @property
    def value(self) -> float:
        """
        Current metric value.

        Returns
        -------
        float
        """

        return self._value

    @value.setter
    def value(
        self,
        value: MetricValue,
    ) -> None:
        """
        Update metric value.

        Previous value is preserved and update statistics
        are maintained automatically.
        """

        if not isinstance(
            value,
            (int, float),
        ):

            raise TypeError(
                "Metric value must be numeric."
            )

        previous = getattr(
            self,
            "_value",
            0.0,
        )

        self.previous_value = float(
            previous
        )

        self._value = float(
            value
        )

        self.update_count += 1

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 4.2
    # Sample Count
    # ------------------------------------------------------

    @property
    def sample_count(self) -> int:
        """
        Number of collected samples.
        """

        return len(
            self.samples
        )

    # ------------------------------------------------------
    # Part 4.3
    # Tag Count
    # ------------------------------------------------------

    @property
    def tag_count(self) -> int:
        """
        Number of metric tags.
        """

        return len(
            self.tags
        )

    # ------------------------------------------------------
    # Part 4.4
    # Attribute Count
    # ------------------------------------------------------

    @property
    def attribute_count(self) -> int:
        """
        Number of metric attributes.
        """

        return len(
            self.attributes
        )

    # ------------------------------------------------------
    # Part 4.5
    # Enabled
    # ------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """
        Whether this metric is enabled.
        """

        return self._enabled

    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable the metric.
        """

        self._enabled = bool(
            value
        )

        self.updated_at = timestamp()

    # ------------------------------------------------------
    # Part 4.6
    # Empty
    # ------------------------------------------------------

    @property
    def empty(self) -> bool:
        """
        True if the metric contains no runtime data.

        Returns
        -------
        bool
        """

        return (

            self.sample_count == 0

            and

            self.tag_count == 0

            and

            self.attribute_count == 0

            and

            self.value == 0.0

        )
# ==========================================================
# Part 5
# Metric Operations
#
# Provides
#     • set_value()
#     • increment()
#     • decrement()
#     • reset()
#     • clear()
#
# Notes
# -----
# Core runtime operations for MetricSchema.
#
# All operations automatically maintain:
#
#     • previous_value
#     • update_count
#     • updated_at
#
# The property setter of "value" is intentionally reused to
# keep state changes centralized.
# ==========================================================

    # ------------------------------------------------------
    # Part 5.1
    # Set Value
    # ------------------------------------------------------

    def set_value(
        self,
        value: MetricValue,
    ) -> "MetricSchema":
        """
        Set the metric value.

        Parameters
        ----------
        value
            New metric value.

        Returns
        -------
        MetricSchema
            Self.
        """

        self.value = value

        return self

    # ------------------------------------------------------
    # Part 5.2
    # Increment
    # ------------------------------------------------------

    def increment(
        self,
        amount: MetricValue = 1.0,
    ) -> "MetricSchema":
        """
        Increase the metric value.

        Parameters
        ----------
        amount
            Increment amount.

        Returns
        -------
        MetricSchema
            Self.
        """

        if not isinstance(
            amount,
            (int, float),
        ):

            raise TypeError(
                "Increment amount must be numeric."
            )

        self.value = self.value + float(
            amount
        )

        return self

    # ------------------------------------------------------
    # Part 5.3
    # Decrement
    # ------------------------------------------------------

    def decrement(
        self,
        amount: MetricValue = 1.0,
    ) -> "MetricSchema":
        """
        Decrease the metric value.

        Parameters
        ----------
        amount
            Decrement amount.

        Returns
        -------
        MetricSchema
            Self.
        """

        if not isinstance(
            amount,
            (int, float),
        ):

            raise TypeError(
                "Decrement amount must be numeric."
            )

        self.value = self.value - float(
            amount
        )

        return self

    # ------------------------------------------------------
    # Part 5.4
    # Reset
    # ------------------------------------------------------

    def reset(self) -> "MetricSchema":
        """
        Reset the metric value.

        Runtime metadata and samples are preserved.

        Returns
        -------
        MetricSchema
            Self.
        """

        self.previous_value = self.value

        self.value = 0.0

        self.error_count = 0

        self.export_count = 0

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 5.5
    # Clear
    # ------------------------------------------------------

    def clear(self) -> "MetricSchema":
        """
        Clear all runtime metric data.

        The metric identity, context and metadata are
        preserved.

        Returns
        -------
        MetricSchema
            Self.
        """

        self.previous_value = 0.0

        self.value = 0.0

        self.samples.clear()

        self.tags.clear()

        self.attributes.clear()

        self.diagnostics.clear()

        self.extras.clear()

        #
        # Keep metadata synchronized.
        #

        self.metadata.tags.clear()

        self.metadata.attributes.clear()

        self.metadata.extras.clear()

        self.update_count = 0

        self.export_count = 0

        self.error_count = 0

        self.exported = False

        self.collected_at = None

        self.updated_at = timestamp()

        return self
# ==========================================================
# Part 6
# Sample Management
#
# Provides
#     • add_sample()
#     • remove_sample()
#     • get_sample()
#     • clear_samples()
#
# Notes
# -----
# Samples represent individual observations collected for
# this metric.
#
# They are used for:
#
#     • average()
#     • minimum()
#     • maximum()
#     • histogram()
#     • summary()
#
# All operations automatically update runtime timestamps.
# ==========================================================

    # ------------------------------------------------------
    # Part 6.1
    # Add Sample
    # ------------------------------------------------------

    def add_sample(
        self,
        value: MetricValue,
    ) -> "MetricSchema":
        """
        Add a metric sample.

        Parameters
        ----------
        value
            Numeric sample.

        Returns
        -------
        MetricSchema
            Self.
        """

        if not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                "Sample must be numeric."
            )

        sample = float(value)

        self.samples.append(sample)

        #
        # Latest observation becomes
        # the current metric value.
        #

        self.value = sample

        self.collected_at = timestamp()

        self.updated_at = self.collected_at

        return self

    # ------------------------------------------------------
    # Part 6.2
    # Remove Sample
    # ------------------------------------------------------

    def remove_sample(
        self,
        index: int = -1,
    ) -> float:
        """
        Remove a sample by index.

        Parameters
        ----------
        index
            Sample index.

        Returns
        -------
        float
            Removed sample.
        """

        if not self.samples:

            raise IndexError(
                "No samples available."
            )

        sample = self.samples.pop(
            index
        )

        #
        # Restore latest sample as value.
        #

        if self.samples:

            self.value = self.samples[-1]

        else:

            self.value = 0.0

        self.updated_at = timestamp()

        return sample

    # ------------------------------------------------------
    # Part 6.3
    # Get Sample
    # ------------------------------------------------------

    def get_sample(
        self,
        index: int = -1,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a sample.

        Parameters
        ----------
        index
            Sample index.

        default
            Returned if index is invalid.

        Returns
        -------
        Any
        """

        try:

            return self.samples[
                index
            ]

        except IndexError:

            return default

    # ------------------------------------------------------
    # Part 6.4
    # Clear Samples
    # ------------------------------------------------------

    def clear_samples(
        self,
    ) -> int:
        """
        Remove all collected samples.

        Returns
        -------
        int
            Number of removed samples.
        """

        count = len(
            self.samples
        )

        self.samples.clear()

        self.previous_value = self.value

        self.value = 0.0

        self.collected_at = None

        self.updated_at = timestamp()

        return count
# ==========================================================
# Part 7
# Tags & Attributes
#
# Provides
#     • set_tag()
#     • get_tag()
#     • remove_tag()
#     • update_metadata()
#
# Notes
# -----
# Tags are lightweight labels used for filtering,
# grouping and querying metrics.
#
# Metadata stores descriptive information about the metric.
#
# Runtime dictionaries and MetricMetadata are kept
# synchronized automatically.
# ==========================================================

    # ------------------------------------------------------
    # Part 7.1
    # Set Tag
    # ------------------------------------------------------

    def set_tag(
        self,
        key: str,
        value: Any,
    ) -> "MetricSchema":
        """
        Set or update a metric tag.

        Parameters
        ----------
        key
            Tag name.

        value
            Tag value.

        Returns
        -------
        MetricSchema
        """

        key = str(key).strip()

        if not key:

            raise ValueError(
                "Tag key cannot be empty."
            )

        self.tags[key] = value

        #
        # Synchronize metadata.
        #

        self.metadata.tags[key] = value

        self.updated_at = timestamp()

        return self

    # ------------------------------------------------------
    # Part 7.2
    # Get Tag
    # ------------------------------------------------------

    def get_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a metric tag.

        Returns
        -------
        Any
        """

        return self.tags.get(
            key,
            default,
        )

    # ------------------------------------------------------
    # Part 7.3
    # Remove Tag
    # ------------------------------------------------------

    def remove_tag(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Remove a metric tag.

        Returns
        -------
        Any
            Removed value or default.
        """

        value = self.tags.pop(
            key,
            default,
        )

        self.metadata.tags.pop(
            key,
            None,
        )

        self.updated_at = timestamp()

        return value

    # ------------------------------------------------------
    # Part 7.4
    # Update Metadata
    # ------------------------------------------------------

    def update_metadata(
        self,
        **metadata: Any,
    ) -> "MetricSchema":
        """
        Update MetricMetadata.

        Existing fields are updated directly.
        Unknown fields are stored inside
        metadata.extras.

        Returns
        -------
        MetricSchema
        """

        for key, value in metadata.items():

            if hasattr(
                self.metadata,
                key,
            ):

                setattr(
                    self.metadata,
                    key,
                    value,
                )

            else:

                self.metadata.extras[
                    key
                ] = value

        #
        # Synchronize shared dictionaries.
        #

        if hasattr(
            self.metadata,
            "tags",
        ):

            self.tags.update(
                self.metadata.tags
            )

        if hasattr(
            self.metadata,
            "attributes",
        ):

            self.attributes.update(
                self.metadata.attributes
            )

        self.updated_at = timestamp()

        return self
# ==========================================================
# Part 8
# Aggregation
#
# Provides
#     • minimum()
#     • maximum()
#     • average()
#     • sum()
#     • statistics()
#
# Notes
# -----
# Aggregation APIs operate on collected samples.
#
# If no samples are available, the current metric value is
# used as the aggregation source.
#
# These operations are read-only.
# ==========================================================

    # ------------------------------------------------------
    # Internal Helper
    # ------------------------------------------------------

    def _aggregation_values(self) -> list[float]:
        """
        Return the values used for aggregation.
        """

        if self.samples:

            return list(self.samples)

        return [float(self.value)]

    # ------------------------------------------------------
    # Part 8.1
    # Minimum
    # ------------------------------------------------------

    def minimum(self) -> float:
        """
        Return the minimum observed value.
        """

        values = self._aggregation_values()

        return min(values)

    # ------------------------------------------------------
    # Part 8.2
    # Maximum
    # ------------------------------------------------------

    def maximum(self) -> float:
        """
        Return the maximum observed value.
        """

        values = self._aggregation_values()

        return max(values)

    # ------------------------------------------------------
    # Part 8.3
    # Average
    # ------------------------------------------------------

    def average(self) -> float:
        """
        Return the arithmetic mean.
        """

        values = self._aggregation_values()

        return statistics.fmean(values)

    # ------------------------------------------------------
    # Part 8.4
    # Sum
    # ------------------------------------------------------

    def sum(self) -> float:
        """
        Return the accumulated value.
        """

        values = self._aggregation_values()

        return float(

            math.fsum(values)

        )

    # ------------------------------------------------------
    # Part 8.5
    # Statistics
    # ------------------------------------------------------

    def statistics(self) -> MetricDict:
        """
        Return aggregation statistics.

        Returns
        -------
        MetricDict
        """

        values = self._aggregation_values()

        count = len(values)

        total = float(

            math.fsum(values)

        )

        mean = statistics.fmean(values)

        minimum = min(values)

        maximum = max(values)

        if count > 1:

            variance = statistics.pvariance(
                values
            )

            stdev = statistics.pstdev(
                values
            )

        else:

            variance = 0.0

            stdev = 0.0

        return {

            # Identity

            "id":
                self.id,

            "name":
                self.name,

            "type":
                self.type.value,

            "unit":
                self.context.unit.value,

            # Sample information

            "count":
                count,

            "sample_count":
                self.sample_count,

            # Aggregation

            "minimum":
                minimum,

            "maximum":
                maximum,

            "average":
                mean,

            "sum":
                total,

            "variance":
                variance,

            "stddev":
                stdev,

            # Current runtime

            "current":
                self.value,

            "previous":
                self.previous_value,

            "updates":
                self.update_count,

            "exports":
                self.export_count,

            "errors":
                self.error_count,

            # Metadata

            "tag_count":
                self.tag_count,

            "attribute_count":
                self.attribute_count,

            "enabled":
                self.enabled,

            "status":
                self.status.value,

            "updated_at":
                self.updated_at,

        }
# ==========================================================
# Part 9
# Serialization
#
# Provides
#     • to_dict()
#     • to_json()
#     • from_dict()
#     • from_json()
#
# Notes
# -----
# Serialization APIs for MetricSchema.
#
# These methods provide lossless conversion between
# MetricSchema and JSON-compatible representations.
#
# Compatible with dataclasses(slots=True).
# ==========================================================

    # ------------------------------------------------------
    # Part 9.1
    # To Dictionary
    # ------------------------------------------------------

    def to_dict(self) -> MetricDict:
        """
        Convert this metric into a dictionary.

        Returns
        -------
        MetricDict
        """

        return {

            # Identity

            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,

            # Core

            "context": dataclass_to_dict(
                self.context
            ),

            "metadata": dataclass_to_dict(
                self.metadata
            ),

            # Metric

            "value": self.value,
            "previous_value": self.previous_value,
            "samples": list(self.samples),

            # Runtime

            "tags": dict(self.tags),
            "attributes": dict(self.attributes),
            "diagnostics": dict(self.diagnostics),
            "extras": dict(self.extras),

            # State

            "enabled": self.enabled,
            "sampled": self.sampled,
            "exported": self.exported,

            # Time

            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "collected_at": self.collected_at,

            # Counters

            "update_count": self.update_count,
            "export_count": self.export_count,
            "error_count": self.error_count,

        }

    # ------------------------------------------------------
    # Part 9.2
    # To JSON
    # ------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize metric into JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=ensure_ascii,

            default=str,

        )

    # ------------------------------------------------------
    # Part 9.3
    # From Dictionary
    # ------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricSchema":
        """
        Construct MetricSchema from dictionary.
        """

        context = MetricContext(

            **data.get(
                "context",
                {},
            )

        )

        #
        # Restore enums.
        #

        if isinstance(
            context.metric_type,
            str,
        ):

            context.metric_type = MetricType(

                context.metric_type

            )

        if isinstance(
            context.unit,
            str,
        ):

            context.unit = MetricUnit(

                context.unit

            )

        metadata = MetricMetadata(

            **data.get(
                "metadata",
                {},
            )

        )

        metric_type = data.get(

            "type",

            MetricType.GAUGE,

        )

        if isinstance(
            metric_type,
            str,
        ):

            metric_type = MetricType(

                metric_type

            )

        metric_status = data.get(

            "status",

            MetricStatus.CREATED,

        )

        if isinstance(
            metric_status,
            str,
        ):

            metric_status = MetricStatus(

                metric_status

            )

        return cls(

            id=data.get(
                "id",
                generate_metric_id(),
            ),

            name=data.get(
                "name",
                DEFAULT_METRIC_NAME,
            ),

            type=metric_type,

            status=metric_status,

            context=context,

            metadata=metadata,

            value=data.get(
                "value",
                0.0,
            ),

            previous_value=data.get(
                "previous_value",
                0.0,
            ),

            samples=list(

                data.get(
                    "samples",
                    [],
                )

            ),

            tags=dict(

                data.get(
                    "tags",
                    {},
                )

            ),

            attributes=dict(

                data.get(
                    "attributes",
                    {},
                )

            ),

            diagnostics=dict(

                data.get(
                    "diagnostics",
                    {},
                )

            ),

            extras=dict(

                data.get(
                    "extras",
                    {},
                )

            ),

            enabled=data.get(
                "enabled",
                True,
            ),

            sampled=data.get(
                "sampled",
                True,
            ),

            exported=data.get(
                "exported",
                False,
            ),

            created_at=data.get(
                "created_at",
                timestamp(),
            ),

            updated_at=data.get(
                "updated_at",
                timestamp(),
            ),

            collected_at=data.get(
                "collected_at",
            ),

            update_count=data.get(
                "update_count",
                0,
            ),

            export_count=data.get(
                "export_count",
                0,
            ),

            error_count=data.get(
                "error_count",
                0,
            ),

        )

    # ------------------------------------------------------
    # Part 9.4
    # From JSON
    # ------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricSchema":
        """
        Construct MetricSchema from JSON.
        """

        return cls.from_dict(

            json.loads(

                payload

            )

        )
# ==========================================================
# Part 10
# Snapshot
#
# Provides
#     • snapshot()
#     • restore()
#     • clone()
#     • copy()
#
# Notes
# -----
# Snapshot APIs provide lightweight state persistence for
# MetricSchema.
#
# They are intended for:
#
#     • Runtime checkpoints
#     • Rollback
#     • Debugging
#     • Export pipelines
#     • Safe cloning
#
# Snapshot objects are plain dictionaries and therefore
# JSON serializable.
# ==========================================================

    # ------------------------------------------------------
    # Part 10.1
    # Snapshot
    # ------------------------------------------------------

    def snapshot(self) -> MetricDict:
        """
        Create a runtime snapshot.

        Returns
        -------
        MetricDict
        """

        snapshot = self.to_dict()

        snapshot["snapshot_time"] = timestamp()

        snapshot["snapshot_version"] = METRIC_VERSION

        return snapshot

    # ------------------------------------------------------
    # Part 10.2
    # Restore
    # ------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "MetricSchema":
        """
        Restore this metric from a snapshot.

        Parameters
        ----------
        snapshot
            Snapshot dictionary.

        Returns
        -------
        MetricSchema
        """

        restored = self.from_dict(snapshot)

        #
        # Identity
        #

        self.id = restored.id

        self.name = restored.name

        self.type = restored.type

        self.status = restored.status

        #
        # Core Models
        #

        self.context = restored.context

        self.metadata = restored.metadata

        #
        # Metric Data
        #

        self.value = restored.value

        self.previous_value = restored.previous_value

        self.samples = list(
            restored.samples
        )

        #
        # Runtime Dictionaries
        #

        self.tags = dict(
            restored.tags
        )

        self.attributes = dict(
            restored.attributes
        )

        self.diagnostics = dict(
            restored.diagnostics
        )

        self.extras = dict(
            restored.extras
        )

        #
        # Runtime State
        #

        self.enabled = restored.enabled

        self.sampled = restored.sampled

        self.exported = restored.exported

        #
        # Timing
        #

        self.created_at = restored.created_at

        self.updated_at = timestamp()

        self.collected_at = restored.collected_at

        #
        # Counters
        #

        self.update_count = restored.update_count

        self.export_count = restored.export_count

        self.error_count = restored.error_count

        return self

    # ------------------------------------------------------
    # Part 10.3
    # Clone
    # ------------------------------------------------------

    def clone(self) -> "MetricSchema":
        """
        Create a deep clone.

        Returns
        -------
        MetricSchema
        """

        return self.from_dict(

            self.snapshot()

        )

    # ------------------------------------------------------
    # Part 10.4
    # Copy
    # ------------------------------------------------------

    def copy(self) -> "MetricSchema":
        """
        Alias for clone().

        Returns
        -------
        MetricSchema
        """

        return self.clone()
# ==========================================================
# Part 11
# Validation
#
# Provides
#     • validate()
#     • validate_context()
#     • validate_samples()
#     • validate_tags()
#
# Notes
# -----
# Public validation APIs.
#
# These methods are intended for Runtime, Dashboard,
# CLI, Exporters and user applications.
#
# They complement the internal _validate() constructor
# validation by allowing validation at any runtime point.
# ==========================================================

    # ------------------------------------------------------
    # Part 11.1
    # Validate
    # ------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate the entire metric.

        Returns
        -------
        bool
        """

        self.validate_context()

        self.validate_samples()

        self.validate_tags()

        #
        # Identity
        #

        if not self.id:

            raise ValueError(
                "Metric id cannot be empty."
            )

        if not self.name:

            raise ValueError(
                "Metric name cannot be empty."
            )

        #
        # Enum validation
        #

        if not isinstance(
            self.type,
            MetricType,
        ):

            raise TypeError(
                "Invalid MetricType."
            )

        if not isinstance(
            self.status,
            MetricStatus,
        ):

            raise TypeError(
                "Invalid MetricStatus."
            )

        #
        # Numeric validation
        #

        if not isinstance(
            self.value,
            (int, float),
        ):

            raise TypeError(
                "Metric value must be numeric."
            )

        if not isinstance(
            self.previous_value,
            (int, float),
        ):

            raise TypeError(
                "previous_value must be numeric."
            )

        return True

    # ------------------------------------------------------
    # Part 11.2
    # Validate Context
    # ------------------------------------------------------

    def validate_context(self) -> bool:
        """
        Validate MetricContext.

        Returns
        -------
        bool
        """

        if not isinstance(
            self.context,
            MetricContext,
        ):

            raise TypeError(
                "context must be MetricContext."
            )

        if not self.context.metric_id:

            raise ValueError(
                "MetricContext.metric_id is required."
            )

        if not self.context.namespace:

            raise ValueError(
                "Metric namespace is required."
            )

        if not self.context.service_name:

            raise ValueError(
                "Service name is required."
            )

        if not isinstance(
            self.context.metric_type,
            MetricType,
        ):

            raise TypeError(
                "Invalid MetricType."
            )

        if not isinstance(
            self.context.unit,
            MetricUnit,
        ):

            raise TypeError(
                "Invalid MetricUnit."
            )

        return True

    # ------------------------------------------------------
    # Part 11.3
    # Validate Samples
    # ------------------------------------------------------

    def validate_samples(self) -> bool:
        """
        Validate collected samples.

        Returns
        -------
        bool
        """

        if not isinstance(
            self.samples,
            list,
        ):

            raise TypeError(
                "samples must be a list."
            )

        for sample in self.samples:

            if not isinstance(
                sample,
                (int, float),
            ):

                raise TypeError(
                    "All samples must be numeric."
                )

            if math.isnan(sample):

                raise ValueError(
                    "NaN sample detected."
                )

            if math.isinf(sample):

                raise ValueError(
                    "Infinite sample detected."
                )

        return True

    # ------------------------------------------------------
    # Part 11.4
    # Validate Tags
    # ------------------------------------------------------

    def validate_tags(self) -> bool:
        """
        Validate metric tags.

        Returns
        -------
        bool
        """

        if not isinstance(
            self.tags,
            dict,
        ):

            raise TypeError(
                "tags must be a dictionary."
            )

        for key, value in self.tags.items():

            if not isinstance(
                key,
                str,
            ):

                raise TypeError(
                    "Tag keys must be strings."
                )

            if not key.strip():

                raise ValueError(
                    "Empty tag key detected."
                )

            #
            # Ensure values are JSON serializable.
            #

            try:

                json.dumps(
                    value,
                    default=str,
                )

            except Exception as exc:

                raise TypeError(

                    f"Tag '{key}' is not serializable."

                ) from exc

        return True
# ==========================================================
# Part 12
# Statistics
#
# Provides
#     • diagnostics()
#     • summary()
#     • runtime_statistics()
#
# Notes
# -----
# High-level reporting APIs for MetricSchema.
#
# These methods are intended for:
#
#     • Runtime
#     • Dashboard
#     • CLI
#     • Exporters
#     • Monitoring
# ==========================================================

    # ------------------------------------------------------
    # Part 12.1
    # Diagnostics
    # ------------------------------------------------------

    def diagnostics(self) -> MetricDict:
        """
        Return diagnostic information.

        Returns
        -------
        MetricDict
        """

        return {

            #
            # Identity
            #

            "id":
                self.id,

            "name":
                self.name,

            "type":
                self.type.value,

            "status":
                self.status.value,

            #
            # Runtime
            #

            "enabled":
                self.enabled,

            "sampled":
                self.sampled,

            "exported":
                self.exported,

            #
            # Validation
            #

            "valid":
                self.validate(),

            #
            # Counters
            #

            "update_count":
                self.update_count,

            "export_count":
                self.export_count,

            "error_count":
                self.error_count,

            #
            # Collections
            #

            "sample_count":
                self.sample_count,

            "tag_count":
                self.tag_count,

            "attribute_count":
                self.attribute_count,

            #
            # Time
            #

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "collected_at":
                self.collected_at,

        }

    # ------------------------------------------------------
    # Part 12.2
    # Summary
    # ------------------------------------------------------

    def summary(self) -> MetricDict:
        """
        Return a concise metric summary.

        Returns
        -------
        MetricDict
        """

        statistics = self.statistics()

        return {

            "id":
                self.id,

            "name":
                self.name,

            "type":
                self.type.value,

            "unit":
                self.context.unit.value,

            "value":
                self.value,

            "minimum":
                statistics["minimum"],

            "maximum":
                statistics["maximum"],

            "average":
                statistics["average"],

            "sum":
                statistics["sum"],

            "samples":
                self.sample_count,

            "status":
                self.status.value,

        }

    # ------------------------------------------------------
    # Part 12.3
    # Runtime Statistics
    # ------------------------------------------------------

    def runtime_statistics(self) -> MetricDict:
        """
        Return runtime execution statistics.

        Returns
        -------
        MetricDict
        """

        uptime = max(

            0.0,

            timestamp() - self.created_at,

        )

        export_rate = (

            self.export_count / uptime

            if uptime > 0

            else 0.0

        )

        update_rate = (

            self.update_count / uptime

            if uptime > 0

            else 0.0

        )

        error_rate = (

            self.error_count / self.update_count

            if self.update_count > 0

            else 0.0

        )

        return {

            #
            # Runtime
            #

            "uptime_seconds":
                uptime,

            "enabled":
                self.enabled,

            "sampled":
                self.sampled,

            "exported":
                self.exported,

            #
            # Activity
            #

            "updates":
                self.update_count,

            "exports":
                self.export_count,

            "errors":
                self.error_count,

            #
            # Rates
            #

            "update_rate":
                update_rate,

            "export_rate":
                export_rate,

            "error_rate":
                error_rate,

            #
            # Resource Usage
            #

            "samples":
                self.sample_count,

            "tags":
                self.tag_count,

            "attributes":
                self.attribute_count,

            #
            # Current Value
            #

            "current_value":
                self.value,

            "previous_value":
                self.previous_value,

        }
# ==========================================================
# Part 13
# Python Protocols
#
# Provides
#     • __repr__()
#     • __str__()
#     • __len__()
#     • __iter__()
#     • __contains__()
#     • __getitem__()
#     • __setitem__()
#     • __copy__()
#     • __deepcopy__()
#
# Notes
# -----
# Standard Python protocol implementations.
#
# These protocols make MetricSchema behave naturally as a
# Python object while remaining convenient for Runtime,
# Dashboard, CLI and Exporters.
# ==========================================================

    # ------------------------------------------------------
    # Part 13.1
    # repr()
    # ------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"id={self.id!r}, "

            f"name={self.name!r}, "

            f"type={self.type.value!r}, "

            f"value={self.value!r}, "

            f"status={self.status.value!r}"

            ")"

        )

    # ------------------------------------------------------
    # Part 13.2
    # str()
    # ------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        unit = self.context.unit.value

        return (

            f"{self.name}: "

            f"{self.value} "

            f"{unit}"

        )

    # ------------------------------------------------------
    # Part 13.3
    # len()
    # ------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of collected samples.
        """

        return self.sample_count

    # ------------------------------------------------------
    # Part 13.4
    # iter()
    # ------------------------------------------------------

    def __iter__(self) -> Iterator[float]:
        """
        Iterate over samples.
        """

        return iter(

            self.samples

        )

    # ------------------------------------------------------
    # Part 13.5
    # contains()
    # ------------------------------------------------------

    def __contains__(
        self,
        item: Any,
    ) -> bool:
        """
        Membership test.

        Checks

            • sample value
            • tag key
            • attribute key
        """

        return (

            item in self.samples

            or

            item in self.tags

            or

            item in self.attributes

        )

    # ------------------------------------------------------
    # Part 13.6
    # getitem()
    # ------------------------------------------------------

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style lookup.

        Search order

            1. tags
            2. attributes
            3. dataclass fields
        """

        if key in self.tags:

            return self.tags[key]

        if key in self.attributes:

            return self.attributes[key]

        if hasattr(

            self,

            key,

        ):

            return getattr(

                self,

                key,

            )

        raise KeyError(

            key

        )

    # ------------------------------------------------------
    # Part 13.7
    # setitem()
    # ------------------------------------------------------

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style assignment.

        Existing attributes are updated directly.
        Unknown keys become tags.
        """

        if hasattr(

            self,

            key,

        ):

            setattr(

                self,

                key,

                value,

            )

        else:

            self.set_tag(

                key,

                value,

            )

    # ------------------------------------------------------
    # Part 13.8
    # copy()
    # ------------------------------------------------------

    def __copy__(
        self,
    ) -> "MetricSchema":
        """
        Shallow copy.

        Implemented using clone() to avoid shared mutable
        state.
        """

        return self.clone()

    # ------------------------------------------------------
    # Part 13.9
    # deepcopy()
    # ------------------------------------------------------

    def __deepcopy__(
        self,
        memo: dict,
    ) -> "MetricSchema":
        """
        Deep copy.

        Parameters
        ----------
        memo
            Copy memo.

        Returns
        -------
        MetricSchema
        """

        cloned = self.clone()

        memo[id(self)] = cloned

        return cloned                                                                                            