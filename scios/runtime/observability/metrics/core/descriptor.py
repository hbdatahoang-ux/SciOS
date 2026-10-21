# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import json

from enum import Enum
from typing import Final
from typing import Literal
from typing import TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DESCRIPTOR_VERSION: Final[str] = "1.0.0"

DESCRIPTOR_API_VERSION: Final[str] = "1.0"

DEFAULT_DESCRIPTION: Final[str] = ""

DEFAULT_UNIT: Final[str] = "count"

DEFAULT_MONOTONIC: Final[bool] = False

DEFAULT_ENABLED: Final[bool] = True

MAX_NAME_LENGTH: Final[int] = 255

MAX_DESCRIPTION_LENGTH: Final[int] = 4096


# ==============================================================================
# Part 3. Enums
# ==============================================================================


class MetricType(str, Enum):
    """
    Supported metric kinds.
    """

    COUNTER = "counter"

    GAUGE = "gauge"

    HISTOGRAM = "histogram"

    SUMMARY = "summary"

    TIMER = "timer"

    CUSTOM = "custom"


class MetricUnit(str, Enum):
    """
    Common metric units.
    """

    COUNT = "count"

    BYTES = "bytes"

    SECONDS = "seconds"

    MILLISECONDS = "milliseconds"

    MICROSECONDS = "microseconds"

    NANOSECONDS = "nanoseconds"

    PERCENT = "percent"

    CELSIUS = "celsius"

    VOLTS = "volts"

    AMPERES = "amperes"

    WATTS = "watts"

    HERTZ = "hertz"

    METERS = "meters"

    NONE = "none"

    CUSTOM = "custom"


# ==============================================================================
# Part 4. Exceptions
# ==============================================================================


class MetricDescriptorError(Exception):
    """
    Base descriptor exception.
    """


class InvalidMetricNameError(MetricDescriptorError):
    """
    Raised when a metric name is invalid.
    """


class InvalidMetricTypeError(MetricDescriptorError):
    """
    Raised when metric type is invalid.
    """


class InvalidMetricUnitError(MetricDescriptorError):
    """
    Raised when metric unit is invalid.
    """


class DescriptorValidationError(MetricDescriptorError):
    """
    Raised when descriptor validation fails.
    """


# ==============================================================================
# Part 5. Type Aliases
# ==============================================================================

MetricName: TypeAlias = str

MetricDescription: TypeAlias = str

MetricVersion: TypeAlias = str

MetricEnabled: TypeAlias = bool

MetricMonotonic: TypeAlias = bool

MetricJSON: TypeAlias = str

MetricDict: TypeAlias = dict[str, object]

MetricUnitLike: TypeAlias = MetricUnit | str

MetricTypeLike: TypeAlias = MetricType | str

MetricKind: TypeAlias = Literal[
    "counter",
    "gauge",
    "histogram",
    "summary",
    "timer",
    "custom",
]

# ==============================================================================
# Part 6. Dataclass
# ==============================================================================

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class MetricDescriptor:
    """
    Immutable description of a metric.

    A MetricDescriptor contains metadata describing a metric but does not
    contain any runtime value.
    """

    name: MetricName

    metric_type: MetricTypeLike

    description: MetricDescription = DEFAULT_DESCRIPTION

    unit: MetricUnitLike = DEFAULT_UNIT

    monotonic: MetricMonotonic = DEFAULT_MONOTONIC

    enabled: MetricEnabled = DEFAULT_ENABLED

    version: MetricVersion = DESCRIPTOR_VERSION

    api_version: MetricVersion = DESCRIPTOR_API_VERSION

    _validated: bool = field(
        init=False,
        default=False,
        repr=False,
        compare=False,
    )


# ==============================================================================
# Part 7. Constructor Validation
# ==============================================================================

    def __post_init__(self) -> None:

        self._validate_name()

        self._validate_metric_type()

        self._validate_unit()

        self.validate()

        self._validated = True


# ==============================================================================
# Part 8. Properties
# ==============================================================================

    @property
    def is_counter(self) -> bool:

        return self.metric_type == MetricType.COUNTER


    @property
    def is_gauge(self) -> bool:

        return self.metric_type == MetricType.GAUGE


    @property
    def is_histogram(self) -> bool:

        return self.metric_type == MetricType.HISTOGRAM


    @property
    def is_summary(self) -> bool:

        return self.metric_type == MetricType.SUMMARY


    @property
    def is_timer(self) -> bool:

        return self.metric_type == MetricType.TIMER


    @property
    def is_custom(self) -> bool:

        return self.metric_type == MetricType.CUSTOM


    @property
    def is_enabled(self) -> bool:

        return self.enabled


    @property
    def is_monotonic(self) -> bool:

        return self.monotonic


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def _validate_name(self) -> None:

        if not isinstance(self.name, str):
            raise InvalidMetricNameError(
                "Metric name must be a string."
            )

        self.name = self.name.strip()

        if not self.name:
            raise InvalidMetricNameError(
                "Metric name cannot be empty."
            )

        if len(self.name) > MAX_NAME_LENGTH:
            raise InvalidMetricNameError(
                f"Metric name exceeds {MAX_NAME_LENGTH} characters."
            )


    def _validate_metric_type(self) -> None:

        if isinstance(self.metric_type, MetricType):
            return

        try:
            self.metric_type = MetricType(self.metric_type)
        except Exception as exc:
            raise InvalidMetricTypeError(
                f"Unsupported metric type: {self.metric_type}"
            ) from exc


    def _validate_unit(self) -> None:

        if isinstance(self.unit, MetricUnit):
            return

        try:
            self.unit = MetricUnit(self.unit)
        except Exception:
            self.unit = MetricUnit.CUSTOM


    def validate(self) -> None:

        if len(self.description) > MAX_DESCRIPTION_LENGTH:
            raise DescriptorValidationError(
                "Description exceeds maximum length."
            )

        if not isinstance(self.enabled, bool):
            raise DescriptorValidationError(
                "enabled must be bool."
            )

        if not isinstance(self.monotonic, bool):
            raise DescriptorValidationError(
                "monotonic must be bool."
            )


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> MetricDict:

        return {
            "name": self.name,
            "metric_type": self.metric_type.value,
            "description": self.description,
            "unit": self.unit.value,
            "monotonic": self.monotonic,
            "enabled": self.enabled,
            "version": self.version,
            "api_version": self.api_version,
        }


    @classmethod
    def from_dict(
        cls,
        data: MetricDict,
    ) -> "MetricDescriptor":

        return cls(
            name=data["name"],
            metric_type=data["metric_type"],
            description=data.get(
                "description",
                DEFAULT_DESCRIPTION,
            ),
            unit=data.get(
                "unit",
                DEFAULT_UNIT,
            ),
            monotonic=data.get(
                "monotonic",
                DEFAULT_MONOTONIC,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            version=data.get(
                "version",
                DESCRIPTOR_VERSION,
            ),
            api_version=data.get(
                "api_version",
                DESCRIPTOR_API_VERSION,
            ),
        )


    def to_json(self) -> MetricJSON:

        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
        )


    @classmethod
    def from_json(
        cls,
        text: MetricJSON,
    ) -> "MetricDescriptor":

        return cls.from_dict(
            json.loads(text)
        )

# ==============================================================================
# Part 11. Copy
# ==============================================================================

    def copy(self) -> "MetricDescriptor":
        """
        Return a shallow copy.
        """
        return MetricDescriptor.from_dict(
            self.to_dict()
        )

    def clone(self) -> "MetricDescriptor":
        """
        Return a deep semantic copy.

        Currently equivalent to copy() because every field is immutable.
        """
        return MetricDescriptor.from_dict(
            self.to_dict()
        )


# ==============================================================================
# Part 12. Equality
# ==============================================================================

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricDescriptor):
            return NotImplemented

        return self.to_dict() == other.to_dict()


    def __hash__(self) -> int:

        return hash(
            (
                self.name,
                self.metric_type,
                self.description,
                self.unit,
                self.monotonic,
                self.enabled,
                self.version,
                self.api_version,
            )
        )


# ==============================================================================
# Part 13. Representation
# ==============================================================================

    def __repr__(self) -> str:

        return (
            "MetricDescriptor("
            f"name={self.name!r}, "
            f"type={self.metric_type.value!r}, "
            f"unit={self.unit.value!r}, "
            f"monotonic={self.monotonic!r}, "
            f"enabled={self.enabled!r}"
            ")"
        )


    def __str__(self) -> str:

        return (
            f"{self.name}"
            f"[{self.metric_type.value}]"
        )


# ==============================================================================
# Part 14. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DESCRIPTOR_VERSION",
    "DESCRIPTOR_API_VERSION",
    "DEFAULT_DESCRIPTION",
    "DEFAULT_UNIT",
    "DEFAULT_MONOTONIC",
    "DEFAULT_ENABLED",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "MetricType",
    "MetricUnit",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "MetricDescriptorError",
    "InvalidMetricNameError",
    "InvalidMetricTypeError",
    "InvalidMetricUnitError",
    "DescriptorValidationError",

    # ------------------------------------------------------------------
    # Type aliases
    # ------------------------------------------------------------------

    "MetricName",
    "MetricDescription",
    "MetricVersion",
    "MetricEnabled",
    "MetricMonotonic",
    "MetricJSON",
    "MetricDict",
    "MetricUnitLike",
    "MetricTypeLike",
    "MetricKind",

    # ------------------------------------------------------------------
    # Main class
    # ------------------------------------------------------------------

    "MetricDescriptor",
]        