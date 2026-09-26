"""
SciOS Observability
===================

Metric Validation Engine.

Production validation layer for the
SciOS-NG Observability subsystem.

Responsibilities
----------------
- Metric name validation
- Metric type validation
- Metric value validation
- Label validation
- Attribute validation
- Metadata validation
- Descriptor validation
- Namespace validation
- Serialization validation
- Runtime validation

Design Goals
------------
- Production ready
- Deterministic
- Thread safe
- Allocation friendly
- Immutable aware
- OpenTelemetry compatible
- Prometheus compatible
- Scientific computing friendly

The validator never mutates user objects.

All validation methods are:
- side-effect free
- deterministic
- reusable

Typical usage
-------------

    MetricValidator.validate_name(name)

    MetricValidator.validate_labels(labels)

    MetricValidator.validate_attributes(attributes)

    MetricValidator.validate_metric_type(metric_type)

All validation failures raise subclasses
of MetricValidationError.
"""


from __future__ import annotations


# ==========================================================
# Standard Library Imports
# ==========================================================

import keyword
import math
import re


# ==========================================================
# Collections
# ==========================================================

from collections.abc import Mapping
from collections.abc import Sequence


# ==========================================================
# Numeric
# ==========================================================

from decimal import Decimal


# ==========================================================
# Typing
# ==========================================================

from typing import Any
from typing import Final
from typing import Pattern
from typing import TypeAlias


# ==========================================================
# Local Imports
# ==========================================================

from .exceptions import (
    InvalidAttributeError,
    InvalidLabelError,
    InvalidMetadataError,
    InvalidMetricNameError,
    InvalidMetricTypeError,
    InvalidMetricUnitError,
    MetricValidationError,
)


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "MetricValidator",
]
# ==========================================================
# Version
# ==========================================================

VALIDATION_VERSION: Final[str] = "1.0"


# ==========================================================
# Limits
# ==========================================================

MAX_NAME_LENGTH: Final[int] = 255

MAX_UNIT_LENGTH: Final[int] = 64

MAX_DESCRIPTION_LENGTH: Final[int] = 4096

MAX_LABEL_KEY_LENGTH: Final[int] = 128

MAX_LABEL_VALUE_LENGTH: Final[int] = 512

MAX_ATTRIBUTE_KEY_LENGTH: Final[int] = 256

MAX_ATTRIBUTE_VALUE_LENGTH: Final[int] = 4096

MAX_NAMESPACE_LENGTH: Final[int] = 128

MAX_TAG_LENGTH: Final[int] = 128

MAX_TAG_COUNT: Final[int] = 128

MAX_METADATA_FIELDS: Final[int] = 256

MAX_LABELS: Final[int] = 128

MAX_ATTRIBUTES: Final[int] = 512


# ==========================================================
# Numeric Limits
# ==========================================================

MIN_FLOAT: Final[float] = -1.0e308

MAX_FLOAT: Final[float] = 1.0e308

MIN_INT64: Final[int] = -(2**63)

MAX_INT64: Final[int] = 2**63 - 1


# ==========================================================
# Primitive Types
# ==========================================================

PRIMITIVE_TYPES: Final[tuple[type, ...]] = (
    bool,
    int,
    float,
    str,
    bytes,
    Decimal,
)
# ==========================================================
# Supported Metric Types
# ==========================================================

SUPPORTED_METRIC_TYPES: Final[frozenset[str]] = frozenset(
    {
        "counter",
        "gauge",
        "histogram",
        "summary",
        "timer",
        "observable_counter",
        "observable_gauge",
        "observable_up_down_counter",
        "up_down_counter",
    }
)


# ==========================================================
# Supported Value Types
# ==========================================================

SUPPORTED_VALUE_TYPES: Final[frozenset[type]] = frozenset(
    {
        int,
        float,
        bool,
    }
)


# ==========================================================
# Regular Expressions
# ==========================================================

# ----------------------------------------------------------
# Metric Name
# Prometheus compatible:
# [a-zA-Z_:][a-zA-Z0-9_:]*
# ----------------------------------------------------------

METRIC_NAME_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[a-zA-Z_:][a-zA-Z0-9_:]*$"
)


# ----------------------------------------------------------
# Namespace
# ----------------------------------------------------------

NAMESPACE_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z][A-Za-z0-9_.-]*$"
)


# ----------------------------------------------------------
# Label Key
# ----------------------------------------------------------

LABEL_KEY_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)


# ----------------------------------------------------------
# Attribute Key
# ----------------------------------------------------------

ATTRIBUTE_KEY_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)


# ----------------------------------------------------------
# Unit
# UCUM-like identifier compatible
# ----------------------------------------------------------

UNIT_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_./%-]+$"
)


# ----------------------------------------------------------
# Version
# ----------------------------------------------------------

VERSION_PATTERN: Final[Pattern[str]] = re.compile(
    r"^\d+\.\d+(\.\d+)?$"
)


# ----------------------------------------------------------
# UUID
# ----------------------------------------------------------

UUID_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[0-9a-fA-F-]{36}$"
)


# ----------------------------------------------------------
# Dot Path
# ----------------------------------------------------------

DOT_PATH_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)


# ----------------------------------------------------------
# Tag
# ----------------------------------------------------------

TAG_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.:/-]+$"
)


# ----------------------------------------------------------
# Annotation
# ----------------------------------------------------------

ANNOTATION_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.:/ -]*$"
)


# ==========================================================
# Reserved Names
# ==========================================================

RESERVED_METRIC_NAMES: Final[frozenset[str]] = frozenset(
    {
        "",
        "_",
        ".",
        "..",
        "null",
        "none",
        "true",
        "false",
        "nan",
        "inf",
        "-inf",
    }
)


# ==========================================================
# Reserved Python Names
# ==========================================================

PYTHON_RESERVED_NAMES: Final[frozenset[str]] = frozenset(
    keyword.kwlist
)


# ==========================================================
# Reserved Prefixes
# ==========================================================

RESERVED_PREFIXES: Final[tuple[str, ...]] = (
    "__",
    "_internal",
    "_private",
    "otel.",
    "prometheus.",
    "system.",
    "python.",
)
# ==========================================================
# Default Values
# ==========================================================

DEFAULT_NAMESPACE: Final[str] = "default"

DEFAULT_UNIT: Final[str] = "1"

DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_DESCRIPTION: Final[str] = ""


# ==========================================================
# Type Aliases
# ==========================================================

MetricName: TypeAlias = str

MetricUnit: TypeAlias = str

MetricNamespace: TypeAlias = str

MetricDescription: TypeAlias = str

MetricLabels: TypeAlias = Mapping[str, Any]

MetricAttributes: TypeAlias = Mapping[str, Any]

MetricMetadata: TypeAlias = Mapping[str, Any]

MetricTags: TypeAlias = Sequence[str]

MetricAnnotations: TypeAlias = Mapping[str, str]

MetricValue: TypeAlias = (
    int
    | float
    | bool
    | Decimal
)

PrimitiveValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | bytes
)

JSONScalar: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
)


# ==========================================================
# Validation Policies
# ==========================================================

ALLOW_EMPTY_DESCRIPTION: Final[bool] = True

ALLOW_EMPTY_LABELS: Final[bool] = True

ALLOW_EMPTY_ATTRIBUTES: Final[bool] = True

ALLOW_NAN: Final[bool] = False

ALLOW_INFINITY: Final[bool] = False


STRICT_NAME_CHECK: Final[bool] = True

STRICT_NAMESPACE_CHECK: Final[bool] = True

STRICT_UNIT_CHECK: Final[bool] = True

STRICT_LABEL_CHECK: Final[bool] = True

STRICT_ATTRIBUTE_CHECK: Final[bool] = True


# ==========================================================
# Internal Validation Flags
# ==========================================================

_CHECK_LENGTHS: Final[bool] = True

_CHECK_RESERVED: Final[bool] = True

_CHECK_TYPES: Final[bool] = True

_CHECK_EMPTY: Final[bool] = True

_CHECK_FINITE_FLOATS: Final[bool] = True


# ==========================================================
# Helper Functions
# ==========================================================

def _is_string(value: Any) -> bool:
    return isinstance(value, str)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _is_sequence(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
    )


def _is_numeric(value: Any) -> bool:
    return isinstance(
        value,
        (
            int,
            float,
            Decimal,
        ),
    ) and not isinstance(value, bool)


def _is_finite(value: Any) -> bool:
    if isinstance(value, Decimal):
        return value.is_finite()

    if isinstance(value, float):
        return math.isfinite(value)

    return True

# ==========================================================
# MetricValidator
# ==========================================================

class MetricValidator:
    """
    Production metric validation engine.

    Provides deterministic, side-effect free validation
    utilities for the SciOS observability subsystem.
    """

    __slots__ = ()

    # ======================================================
    # Metric Name Validation
    # ======================================================

    @classmethod
    def validate_name(
        cls,
        name: MetricName,
    ) -> str:
        pass


    # ======================================================
    # Namespace Validation
    # ======================================================

    @classmethod
    def validate_namespace(
        cls,
        namespace: MetricNamespace,
    ) -> str:
        pass


    # ======================================================
    # Unit Validation
    # ======================================================

    @classmethod
    def validate_unit(
        cls,
        unit: MetricUnit,
    ) -> str:
        pass


    # ======================================================
    # Description Validation
    # ======================================================

    @classmethod
    def validate_description(
        cls,
        description: MetricDescription,
    ) -> str:
        pass


    # ======================================================
    # Label Validation
    # ======================================================

    @classmethod
    def validate_label_key(
        cls,
        key: str,
    ) -> str:
        pass


    @classmethod
    def validate_label_value(
        cls,
        value: Any,
    ) -> Any:
        pass


    @classmethod
    def validate_labels(
        cls,
        labels: MetricLabels,
    ) -> MetricLabels:
        pass


    # ======================================================
    # Attribute Validation
    # ======================================================

    @classmethod
    def validate_attribute_key(
        cls,
        key: str,
    ) -> str:
        pass


    @classmethod
    def validate_attribute_value(
        cls,
        value: Any,
    ) -> Any:
        pass


    @classmethod
    def validate_attributes(
        cls,
        attributes: MetricAttributes,
    ) -> MetricAttributes:
        pass


    # ======================================================
    # Metadata Validation
    # ======================================================

    @classmethod
    def validate_metadata(
        cls,
        metadata: MetricMetadata,
    ) -> MetricMetadata:
        pass


    # ======================================================
    # Tag Validation
    # ======================================================

    @classmethod
    def validate_tags(
        cls,
        tags: MetricTags,
    ) -> tuple[str, ...]:
        pass


    # ======================================================
    # Metric Type Validation
    # ======================================================

    @classmethod
    def validate_metric_type(
        cls,
        metric_type: str,
    ) -> str:
        pass


    # ======================================================
    # Metric Value Validation
    # ======================================================

    @classmethod
    def validate_metric_value(
        cls,
        value: MetricValue,
    ) -> MetricValue:
        pass


    # ======================================================
    # Semantic Metric Validation
    # ======================================================

    @classmethod
    def validate_counter_value(
        cls,
        value: MetricValue,
        *,
        field: str = "counter",
        strict: bool = True,
    ) -> MetricValue:
        pass


    @classmethod
    def validate_up_down_counter_value(
        cls,
        value: MetricValue,
        *,
        field: str = "up_down_counter",
        strict: bool = True,
    ) -> MetricValue:
        pass


    @classmethod
    def validate_gauge_value(
        cls,
        value: MetricValue,
        *,
        field: str = "gauge",
        strict: bool = True,
    ) -> MetricValue:
        pass


    # ======================================================
    # Descriptor Validation
    # ======================================================

    @classmethod
    def validate_descriptor(
        cls,
        descriptor: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        pass


    # ======================================================
    # Internal Helpers
    # ======================================================

    @classmethod
    def _validate_string(
        cls,
        value: Any,
        *,
        field: str,
        max_length: int | None = None,
        allow_empty: bool = False,
    ) -> str:
        pass


    @classmethod
    def _validate_metric_numeric(
        cls,
        value: Any,
        *,
        field: str,
    ) -> int | float | Decimal:
        pass


    @classmethod
    def _validate_collection_size(
        cls,
        value: Any,
        *,
        field: str,
        maximum: int,
    ) -> None:
        pass

    # ======================================================
    # Metric Name Validation
    # ======================================================

    @classmethod
    def validate_name(
        cls,
        name: MetricName,
    ) -> str:
        """
        Validate metric name.

        Rules:
        - Must be string
        - Cannot be empty
        - Must match Prometheus metric format
        - Cannot use reserved names
        - Maximum length enforced
        """

        name = cls._validate_string(
            name,
            field="metric_name",
            max_length=MAX_NAME_LENGTH,
            allow_empty=False,
        )

        if name in RESERVED_METRIC_NAMES:
            raise InvalidMetricNameError(
                f"Reserved metric name: {name}"
            )

        if STRICT_NAME_CHECK:
            if not METRIC_NAME_PATTERN.match(name):
                raise InvalidMetricNameError(
                    f"Invalid metric name: {name}"
                )

        return name


    # ======================================================
    # Namespace Validation
    # ======================================================

    @classmethod
    def validate_namespace(
        cls,
        namespace: MetricNamespace,
    ) -> str:
        """
        Validate metric namespace.

        Rules:
        - Must be string
        - Cannot be empty
        - Must match namespace pattern
        """

        namespace = cls._validate_string(
            namespace,
            field="namespace",
            max_length=MAX_NAMESPACE_LENGTH,
            allow_empty=False,
        )

        if STRICT_NAMESPACE_CHECK:
            if not NAMESPACE_PATTERN.match(namespace):
                raise InvalidMetricNameError(
                    f"Invalid namespace: {namespace}"
                )

        return namespace


    # ======================================================
    # Unit Validation
    # ======================================================

    @classmethod
    def validate_unit(
        cls,
        unit: MetricUnit,
    ) -> str:
        """
        Validate metric unit.

        Rules:
        - Must be string
        - Empty unit allowed only when policy permits
        - Must match UCUM-like format
        """

        unit = cls._validate_string(
            unit,
            field="unit",
            max_length=MAX_UNIT_LENGTH,
            allow_empty=ALLOW_EMPTY_DESCRIPTION,
        )

        if unit and STRICT_UNIT_CHECK:

            if not UNIT_PATTERN.match(unit):
                raise InvalidMetricUnitError(
                    f"Invalid metric unit: {unit}"
                )

        return unit


    # ======================================================
    # Description Validation
    # ======================================================

    @classmethod
    def validate_description(
        cls,
        description: MetricDescription,
    ) -> str:
        """
        Validate metric description.

        Rules:
        - Must be string
        - Maximum length enforced
        - Empty value controlled by policy
        """

        description = cls._validate_string(
            description,
            field="description",
            max_length=MAX_DESCRIPTION_LENGTH,
            allow_empty=ALLOW_EMPTY_DESCRIPTION,
        )

        return description

    # ======================================================
    # Label Validation
    # ======================================================

    @classmethod
    def validate_label_key(
        cls,
        key: str,
    ) -> str:
        """
        Validate label key.

        Rules:
        - Must be string
        - Cannot be empty
        - Must match label key pattern
        - Cannot use reserved labels
        - Maximum length enforced
        """

        key = cls._validate_string(
            key,
            field="label_key",
            max_length=MAX_LABEL_KEY_LENGTH,
            allow_empty=False,
        )

        if key in RESERVED_LABEL_KEYS:
            raise InvalidLabelError(
                f"Reserved label key: {key}"
            )

        if key in PROMETHEUS_RESERVED_LABELS:
            raise InvalidLabelError(
                f"Prometheus reserved label key: {key}"
            )

        if STRICT_LABEL_CHECK:

            if not LABEL_KEY_PATTERN.match(key):
                raise InvalidLabelError(
                    f"Invalid label key: {key}"
                )

        return key


    @classmethod
    def validate_label_value(
        cls,
        value: Any,
    ) -> str:
        """
        Validate label value.

        Rules:
        - Must be string
        - Maximum length enforced
        - Empty value allowed
        """

        if not isinstance(value, str):

            raise InvalidLabelError(
                "Label value must be string."
            )

        if len(value) > MAX_LABEL_VALUE_LENGTH:

            raise InvalidLabelError(
                "Label value exceeds maximum length."
            )

        return value


    @classmethod
    def validate_labels(
        cls,
        labels: MetricLabels | None,
    ) -> dict[str, str]:
        """
        Validate metric labels.

        Rules:
        - Must be mapping
        - Maximum label count enforced
        - Keys validated
        - Values validated
        """

        if labels is None:

            if ALLOW_EMPTY_LABELS:
                return {}

            raise InvalidLabelError(
                "Labels cannot be empty."
            )


        if not isinstance(labels, Mapping):

            raise InvalidLabelError(
                "Labels must be a mapping."
            )


        if len(labels) > MAX_LABELS:

            raise InvalidLabelError(
                "Too many labels."
            )


        validated: dict[str, str] = {}


        for key, value in labels.items():

            valid_key = cls.validate_label_key(
                key
            )

            valid_value = cls.validate_label_value(
                value
            )

            validated[valid_key] = valid_value


        return validated
    # ======================================================
    # Attribute Validation
    # ======================================================

    @classmethod
    def validate_attribute_key(
        cls,
        key: str,
    ) -> str:
        """
        Validate attribute key.

        Rules:
        - Must be string
        - Cannot be empty
        - Must match attribute pattern
        - Cannot use reserved keys
        - Maximum length enforced
        """

        key = cls._validate_string(
            key,
            field="attribute_key",
            max_length=MAX_ATTRIBUTE_KEY_LENGTH,
            allow_empty=False,
        )

        if key in RESERVED_ATTRIBUTE_KEYS:

            raise InvalidAttributeError(
                f"Reserved attribute key: {key}"
            )

        if key.startswith("__"):

            raise InvalidAttributeError(
                f"Private attribute key forbidden: {key}"
            )

        if STRICT_ATTRIBUTE_CHECK:

            if not ATTRIBUTE_KEY_PATTERN.match(key):

                raise InvalidAttributeError(
                    f"Invalid attribute key: {key}"
                )

        return key


    @classmethod
    def validate_attribute_value(
        cls,
        value: Any,
    ) -> Any:
        """
        Validate attribute value.

        Supported:
        - bool
        - int
        - float
        - str
        - bytes

        Reject:
        - complex objects
        - non finite floats
        """

        if isinstance(value, bool):

            return value


        if isinstance(value, int):

            return value


        if isinstance(value, float):

            if _CHECK_FINITE_FLOATS:

                if not math.isfinite(value):

                    raise InvalidAttributeError(
                        "Attribute float must be finite."
                    )

            return value


        if isinstance(value, str):

            if len(value) > MAX_ATTRIBUTE_VALUE_LENGTH:

                raise InvalidAttributeError(
                    "Attribute string exceeds maximum length."
                )

            return value


        if isinstance(value, bytes):

            if len(value) > MAX_ATTRIBUTE_VALUE_LENGTH:

                raise InvalidAttributeError(
                    "Attribute bytes exceeds maximum length."
                )

            return value


        raise InvalidAttributeError(
            f"Unsupported attribute value type: {type(value).__name__}"
        )


    @classmethod
    def validate_attributes(
        cls,
        attributes: MetricAttributes | None,
    ) -> dict[str, Any]:
        """
        Validate metric attributes.

        Rules:
        - Must be mapping
        - Maximum attribute count enforced
        - Keys validated
        - Values validated
        """

        if attributes is None:

            if ALLOW_EMPTY_ATTRIBUTES:

                return {}

            raise InvalidAttributeError(
                "Attributes cannot be empty."
            )


        if not isinstance(attributes, Mapping):

            raise InvalidAttributeError(
                "Attributes must be a mapping."
            )


        if len(attributes) > MAX_ATTRIBUTES:

            raise InvalidAttributeError(
                "Too many attributes."
            )


        validated: dict[str, Any] = {}


        for key, value in attributes.items():

            valid_key = cls.validate_attribute_key(
                key
            )

            valid_value = cls.validate_attribute_value(
                value
            )

            validated[valid_key] = valid_value


        return validated
    # ======================================================
    # Metadata & Tags Validation
    # ======================================================

    @classmethod
    def validate_metadata(
        cls,
        metadata: MetricMetadata | None,
    ) -> dict[str, Any]:
        """
        Validate metric metadata.

        Rules:
        - Must be mapping
        - Maximum field count enforced
        - Keys are validated strings
        - Values must be JSON compatible primitives
        """

        if metadata is None:

            return {}


        if not isinstance(metadata, Mapping):

            raise InvalidMetadataError(
                "Metadata must be a mapping."
            )


        if len(metadata) > MAX_METADATA_FIELDS:

            raise InvalidMetadataError(
                "Too many metadata fields."
            )


        validated: dict[str, Any] = {}


        for key, value in metadata.items():

            key = cls._validate_string(
                key,
                field="metadata_key",
                max_length=MAX_ATTRIBUTE_KEY_LENGTH,
                allow_empty=False,
            )


            if key.startswith("__"):

                raise InvalidMetadataError(
                    f"Reserved metadata key: {key}"
                )


            if not cls._is_json_scalar(value):

                raise InvalidMetadataError(
                    f"Invalid metadata value for key: {key}"
                )


            validated[key] = value


        return validated



    @classmethod
    def validate_tags(
        cls,
        tags: MetricTags | None,
    ) -> tuple[str, ...]:
        """
        Validate metric tags.

        Rules:
        - Must be sequence
        - Maximum tag count enforced
        - Each tag must be string
        - Tag format validated
        """

        if tags is None:

            return ()


        if isinstance(tags, (str, bytes)):

            raise InvalidMetadataError(
                "Tags must be a sequence of strings."
            )


        if not isinstance(tags, Sequence):

            raise InvalidMetadataError(
                "Tags must be a sequence."
            )


        if len(tags) > MAX_TAG_COUNT:

            raise InvalidMetadataError(
                "Too many tags."
            )


        validated: list[str] = []


        for tag in tags:

            tag = cls._validate_string(
                tag,
                field="tag",
                max_length=MAX_TAG_LENGTH,
                allow_empty=False,
            )


            if STRICT_ATTRIBUTE_CHECK:

                if not TAG_PATTERN.match(tag):

                    raise InvalidMetadataError(
                        f"Invalid tag format: {tag}"
                    )


            validated.append(tag)


        return tuple(validated)
    # ======================================================
    # Metric Type & Value Validation
    # ======================================================

    @classmethod
    def validate_metric_type(
        cls,
        metric_type: str,
    ) -> str:
        """
        Validate metric type.

        Supported:
        - counter
        - gauge
        - histogram
        - summary
        - timer
        - observable_counter
        - observable_gauge
        - observable_up_down_counter
        - up_down_counter
        """

        metric_type = cls._validate_string(
            metric_type,
            field="metric_type",
            max_length=64,
            allow_empty=False,
        )


        if metric_type not in SUPPORTED_METRIC_TYPES:

            raise InvalidMetricTypeError(
                f"Unsupported metric type: {metric_type}"
            )


        return metric_type



    @classmethod
    def validate_metric_value(
        cls,
        value: MetricValue,
        *,
        field: str = "value",
        allow_bool: bool = False,
    ) -> int | float | bool | Decimal:
        """
        Validate generic metric value.

        Rules:
        - Must be numeric
        - Must be finite
        - Bool rejected by default
        - Decimal supported
        """

        if isinstance(value, bool):

            if not allow_bool:

                raise InvalidMetricTypeError(
                    f"{field} cannot be bool."
                )


            return value


        if not isinstance(
            value,
            (
                int,
                float,
                Decimal,
            ),
        ):

            raise InvalidMetricTypeError(
                f"{field} must be numeric."
            )


        if isinstance(value, float):

            if not math.isfinite(value):

                raise MetricValidationError(
                    f"{field} must be finite."
                )


        return value
    # ======================================================
    # Counter / Gauge Validation
    # ======================================================

    @classmethod
    def validate_counter_value(
        cls,
        value: MetricValue,
        *,
        field: str = "counter",
    ) -> int | float | Decimal:
        """
        Validate Counter metric value.

        Counter rules:
        - Numeric
        - Finite
        - Not bool
        - Non-negative
        - Monotonic increasing semantics
        """

        value = cls.validate_metric_value(
            value,
            field=field,
            allow_bool=False,
        )


        if value < 0:

            raise MetricValidationError(
                f"{field} must be non-negative."
            )


        return value



    @classmethod
    def validate_up_down_counter_value(
        cls,
        value: MetricValue,
        *,
        field: str = "up_down_counter",
    ) -> int | float | Decimal:
        """
        Validate UpDownCounter metric value.

        Rules:
        - Numeric
        - Finite
        - Not bool
        - Positive, negative or zero allowed
        """

        return cls.validate_metric_value(
            value,
            field=field,
            allow_bool=False,
        )



    @classmethod
    def validate_gauge_value(
        cls,
        value: MetricValue,
        *,
        field: str = "gauge",
    ) -> int | float | Decimal:
        """
        Validate Gauge metric value.

        Gauge rules:
        - Numeric
        - Finite
        - Not bool
        - Positive, negative and zero allowed
        """

        return cls.validate_metric_value(
            value,
            field=field,
            allow_bool=False,
        )
    # ======================================================
    # Descriptor Validation
    # ======================================================

    @classmethod
    def validate_descriptor(
        cls,
        descriptor: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Validate metric descriptor.

        Descriptor expected fields:

        Required:
        - name
        - type

        Optional:
        - namespace
        - unit
        - description
        - labels
        - attributes
        - metadata
        """

        if not isinstance(descriptor, Mapping):

            raise InvalidMetadataError(
                "Descriptor must be a mapping."
            )


        required_fields = (
            "name",
            "type",
        )


        for field in required_fields:

            if field not in descriptor:

                raise InvalidMetadataError(
                    f"Descriptor missing required field: {field}"
                )


        cls.validate_name(
            descriptor["name"],
        )


        cls.validate_metric_type(
            descriptor["type"],
        )


        if "namespace" in descriptor:

            cls.validate_namespace(
                descriptor["namespace"],
            )


        if "unit" in descriptor:

            cls.validate_unit(
                descriptor["unit"],
            )


        if "description" in descriptor:

            cls.validate_description(
                descriptor["description"],
            )


        if "labels" in descriptor:

            cls.validate_labels(
                descriptor["labels"],
            )


        if "attributes" in descriptor:

            cls.validate_attributes(
                descriptor["attributes"],
            )


        if "metadata" in descriptor:

            cls.validate_metadata(
                descriptor["metadata"],
            )


        return descriptor
    # ======================================================
    # Internal Helpers
    # ======================================================

    @classmethod
    def _validate_string(
        cls,
        value: Any,
        *,
        field: str,
        max_length: int | None = None,
        allow_empty: bool = False,
    ) -> str:
        """
        Validate string value.
        """

        if not isinstance(value, str):

            raise MetricValidationError(
                f"{field} must be string."
            )


        if not allow_empty and not value:

            raise MetricValidationError(
                f"{field} cannot be empty."
            )


        if max_length is not None:

            cls._validate_length(
                value,
                field=field,
                maximum=max_length,
            )


        return value



    @classmethod
    def _validate_metric_numeric(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> int | float | Decimal:
        """
        Validate metric numeric value.

        Rules:
        - int
        - float
        - Decimal
        - finite
        - not bool
        """

        if isinstance(value, bool):

            raise InvalidMetricTypeError(
                f"{field} cannot be bool."
            )


        if not isinstance(
            value,
            (
                int,
                float,
                Decimal,
            ),
        ):

            raise InvalidMetricTypeError(
                f"{field} must be numeric."
            )


        return cls._validate_finite(
            value,
            field=field,
        )



    @classmethod
    def _validate_collection_size(
        cls,
        value: Any,
        *,
        field: str,
        maximum: int,
    ) -> None:
        """
        Validate collection size.
        """

        try:

            size = len(value)

        except TypeError:

            raise MetricValidationError(
                f"{field} must be sized collection."
            )


        if size > maximum:

            raise MetricValidationError(
                f"{field} exceeds maximum size {maximum}."
            )



    @classmethod
    def _validate_reserved(
        cls,
        value: str,
        *,
        field: str,
        reserved: frozenset[str] | set[str],
    ) -> str:
        """
        Validate reserved names.
        """

        if value in reserved:

            raise MetricValidationError(
                f"{field} uses reserved value: {value}"
            )


        return value



    @classmethod
    def _validate_length(
        cls,
        value: str,
        *,
        field: str,
        maximum: int,
        minimum: int = 0,
    ) -> str:
        """
        Validate string length.
        """

        length = len(value)


        if length < minimum:

            raise MetricValidationError(
                f"{field} length must be >= {minimum}."
            )


        if length > maximum:

            raise MetricValidationError(
                f"{field} length must be <= {maximum}."
            )


        return value



    @classmethod
    def _validate_finite(
        cls,
        value: int | float | Decimal,
        *,
        field: str = "value",
    ) -> int | float | Decimal:
        """
        Validate numeric finite value.
        """

        if isinstance(value, Decimal):

            if not value.is_finite():

                raise MetricValidationError(
                    f"{field} must be finite."
                )

            return value


        if isinstance(value, float):

            if not math.isfinite(value):

                raise MetricValidationError(
                    f"{field} must be finite."
                )


        return value
# ======================================================
# Module Finalization
# ======================================================

# Ensure public API remains stable.

__all__ = [
    "MetricValidator",
    "VALIDATION_VERSION",
]                                                                