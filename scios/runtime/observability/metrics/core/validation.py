"""
SciOS Observability
==================

Metric Validation Engine.

This module implements the production validation layer for the
SciOS-NG Observability subsystem.

Responsibilities
----------------
- Metric validation
- Descriptor validation
- Label validation
- Attribute validation
- Metadata validation
- Runtime validation
- Registry validation
- Serialization validation
- Snapshot validation
- Type validation
- Namespace validation

Design Goals
------------
- Production ready
- Thread safe
- Deterministic
- Fast
- Allocation friendly
- Immutable aware
- OpenTelemetry compatible
- Prometheus compatible
- Scientific computing friendly

The validator never mutates user objects.
All validation methods are side-effect free.

Typical usage
-------------

    MetricValidator.validate_name(name)

    MetricValidator.validate_labels(labels)

    MetricValidator.validate_attributes(attrs)

    MetricValidator.validate_descriptor(descriptor)

All validation errors raise subclasses of MetricValidationError.
"""

from __future__ import annotations

import keyword
import math
import re
import uuid

from collections.abc import Mapping
from collections.abc import Sequence
from collections.abc import Set

from decimal import Decimal

from typing import Any
from typing import Final
from typing import Pattern
from typing import TypeAlias

from .exceptions import (
    InvalidAttributeError,
    InvalidLabelError,
    InvalidMetadataError,
    InvalidMetricNameError,
    InvalidMetricTypeError,
    InvalidMetricUnitError,
    MetricValidationError,
)

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
# Supported Primitive Types
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
# Allowed Attribute Types
# ==========================================================

ATTRIBUTE_TYPES: Final[tuple[type, ...]] = (
    bool,
    int,
    float,
    str,
    bytes,
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
# Empty Constants
# ==========================================================

EMPTY_DICT: Final[dict[str, Any]] = {}

EMPTY_TUPLE: Final[tuple[Any, ...]] = ()

EMPTY_SET: Final[frozenset[Any]] = frozenset()

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
# Reserved Label Keys
# ==========================================================

RESERVED_LABEL_KEYS: Final[frozenset[str]] = frozenset(
    {
        "__name__",
        "__value__",
        "__type__",
        "__metric__",
        "__bucket__",
        "__sum__",
        "__count__",
    }
)

# ==========================================================
# Reserved Attribute Keys
# ==========================================================

RESERVED_ATTRIBUTE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "__class__",
        "__dict__",
        "__slots__",
        "__weakref__",
    }
)
# ==========================================================
# Regular Expressions
# ==========================================================

#
# Metric name
# Prometheus compatible:
#   [a-zA-Z_:][a-zA-Z0-9_:]*
#

METRIC_NAME_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[a-zA-Z_:][a-zA-Z0-9_:]*$"
)

#
# Namespace
#

NAMESPACE_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z][A-Za-z0-9_.-]*$"
)

#
# Label key
#

LABEL_KEY_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)

#
# Attribute key
#

ATTRIBUTE_KEY_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)

#
# Unit
#
# Compatible with UCUM-like identifiers
#

UNIT_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_./%-]+$"
)

#
# Version
#

VERSION_PATTERN: Final[Pattern[str]] = re.compile(
    r"^\d+\.\d+(\.\d+)?$"
)

#
# UUID
#

UUID_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[0-9a-fA-F-]{36}$"
)

#
# Dot path
#

DOT_PATH_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.-]*$"
)

#
# Tag
#

TAG_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.:/-]+$"
)

#
# Annotation
#

ANNOTATION_PATTERN: Final[Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.:/ -]*$"
)

# ==========================================================
# Reserved Metric Names
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
# Reserved Python Keywords
# ==========================================================

PYTHON_RESERVED_NAMES: Final[frozenset[str]] = frozenset(
    keyword.kwlist
)

# ==========================================================
# Reserved OpenTelemetry Fields
# ==========================================================

OTEL_RESERVED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "service.name",
        "service.version",
        "service.instance.id",
        "telemetry.sdk.name",
        "telemetry.sdk.language",
        "telemetry.sdk.version",
        "host.name",
        "host.id",
        "os.type",
        "os.version",
        "process.pid",
        "process.command",
        "thread.id",
        "thread.name",
    }
)

# ==========================================================
# Reserved Prometheus Labels
# ==========================================================

PROMETHEUS_RESERVED_LABELS: Final[frozenset[str]] = frozenset(
    {
        "__name__",
        "__address__",
        "__scheme__",
        "__metrics_path__",
        "__param_target",
        "__scrape_interval__",
        "__scrape_timeout__",
    }
)

# ==========================================================
# Reserved SciOS Labels
# ==========================================================

SCIOS_RESERVED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "runtime",
        "scheduler",
        "kernel",
        "executor",
        "agent",
        "memory",
        "trace",
        "span",
        "context",
        "snapshot",
        "descriptor",
        "metadata",
    }
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
# Cached Empty Collections
# ==========================================================

_EMPTY_MAPPING: Final[Mapping[str, Any]] = {}

_EMPTY_SEQUENCE: Final[tuple[Any, ...]] = ()

_EMPTY_FROZENSET: Final[frozenset[Any]] = frozenset()
# ==========================================================
# Foundation Helper Functions
# ==========================================================


def _is_str(
    value: Any,
) -> bool:
    """
    Return True if value is a string.
    """

    return isinstance(
        value,
        str,
    )


def _is_mapping(
    value: Any,
) -> bool:
    """
    Return True if value implements Mapping.
    """

    return isinstance(
        value,
        Mapping,
    )


def _is_sequence(
    value: Any,
) -> bool:
    """
    Return (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    )


def _is_identifier(
    value: str,
) -> bool:
    """
    Python identifier check.
    """

    return value.isidentifier()


def _is_keyword(
    value: str,
) -> bool:
    """
    Python keyword.
    """

    return keyword.iskeyword(
        value,
    )


def _is_reserved_name(
    value: str,
) -> bool:
    """
    Reserved metric name.
    """

    return (
        value in RESERVED_METRIC_NAMES
        or value in PYTHON_RESERVED_NAMES
    )


def _matches(
    pattern: Pattern[str],
    value: str,
) -> bool:
    """
    Regex helper.
    """

    return (
        pattern.fullmatch(
            value,
        )
        is not None
    )


def _is_uuid(
    value: str,
) -> bool:
    """
    UUID validator.
    """

    try:

        uuid.UUID(
            value,
        )

        return True

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):

        return False


def _is_finite_number(
    value: Any,
) -> bool:
    """
    Finite numeric value.
    """

    if isinstance(
        value,
        bool,
    ):
        return True

    if isinstance(
        value,
        int,
    ):
        return True

    if isinstance(
        value,
        Decimal,
    ):
        return value.is_finite()

    if isinstance(
        value,
        float,
    ):
        return math.isfinite(
            value,
        )

    return False


def _is_supported_value(
    value: Any,
) -> bool:
    """
    Primitive metric value.
    """

    return isinstance(
        value,
        PRIMITIVE_TYPES,
    )


def _is_supported_attribute(
    value: Any,
) -> bool:
    """
    Supported attribute type.
    """

    return isinstance(
        value,
        ATTRIBUTE_TYPES,
    )


def _normalize_string(
    value: str,
) -> str:
    """
    Trim surrounding whitespace.
    """

    return value.strip()


def _safe_len(
    value: Any,
) -> int:
    """
    Length helper.

    Never raises.
    """

    try:

        return len(
            value,
        )

    except Exception:

        return 0
# ==========================================================
# Internal Validation Helpers
# ==========================================================


def _require_str(
    value: Any,
    field: str,
) -> str:
    """
    Ensure value is a string.
    """

    if not isinstance(value, str):

        raise MetricValidationError(
            f"{field} must be a string."
        )

    return value


def _require_mapping(
    value: Any,
    field: str,
) -> Mapping[str, Any]:
    """
    Ensure value implements Mapping.
    """

    if not isinstance(
        value,
        Mapping,
    ):

        raise MetricValidationError(
            f"{field} must be a mapping."
        )

    return value


def _require_sequence(
    value: Any,
    field: str,
) -> Sequence[Any]:
    """
    Ensure value is a non-string sequence.
    """

    if (
        not isinstance(
            value,
            Sequence,
        )
        or isinstance(
            value,
            (
                str,
                bytes,
                bytearray,
            ),
        )
    ):

        raise MetricValidationError(
            f"{field} must be a sequence."
        )

    return value


# ==========================================================
# Length Helpers
# ==========================================================


def _check_length(
    value: str,
    *,
    maximum: int,
    field: str,
) -> None:
    """
    Validate maximum string length.
    """

    if (
        _CHECK_LENGTHS
        and len(value) > maximum
    ):

        raise MetricValidationError(
            f"{field} exceeds "
            f"{maximum} characters."
        )


def _check_not_empty(
    value: str,
    field: str,
) -> None:
    """
    Reject empty strings.
    """

    if value == "":

        raise MetricValidationError(
            f"{field} cannot be empty."
        )


# ==========================================================
# Regex Helpers
# ==========================================================


def _check_pattern(
    value: str,
    *,
    pattern: Pattern[str],
    field: str,
) -> None:
    """
    Regex validation.
    """

    if not _matches(
        pattern,
        value,
    ):

        raise MetricValidationError(
            f"Invalid {field}: "
            f"{value!r}"
        )


# ==========================================================
# Reserved Helpers
# ==========================================================


def _check_reserved(
    value: str,
    *,
    reserved: Set[str],
    field: str,
) -> None:
    """
    Reject reserved identifiers.
    """

    if (
        _CHECK_RESERVED
        and value in reserved
    ):

        raise MetricValidationError(
            f"{field} "
            f"{value!r} "
            f"is reserved."
        )


def _check_prefix(
    value: str,
) -> None:
    """
    Reserved prefixes.
    """

    if not _CHECK_RESERVED:
        return

    for prefix in RESERVED_PREFIXES:

        if value.startswith(
            prefix,
        ):

            raise MetricValidationError(
                f"{value!r} uses "
                "a reserved prefix."
            )


# ==========================================================
# Numeric Helpers
# ==========================================================


def _check_finite(
    value: float,
    field: str,
) -> None:
    """
    Reject NaN/Inf.
    """

    if (
        not ALLOW_NAN
        and math.isnan(
            value,
        )
    ):

        raise MetricValidationError(
            f"{field} "
            "cannot be NaN."
        )

    if (
        not ALLOW_INFINITY
        and math.isinf(
            value,
        )
    ):

        raise MetricValidationError(
            f"{field} "
            "cannot be infinite."
        )


# ==========================================================
# UUID Helper
# ==========================================================


def _check_uuid(
    value: str,
    field: str,
) -> None:
    """
    Validate UUID.
    """

    if not _is_uuid(
        value,
    ):

        raise MetricValidationError(
            f"Invalid UUID "
            f"for {field}."
        )


# ==========================================================
# Identifier Helper
# ==========================================================


def _check_identifier(
    value: str,
    field: str,
) -> None:
    """
    Identifier validation.
    """

    if not _is_identifier(
        value,
    ):

        raise MetricValidationError(
            f"{field} "
            "must be a valid identifier."
        )

    if _is_keyword(
        value,
    ):

        raise MetricValidationError(
            f"{field} "
            "cannot be a Python keyword."
        )
# ==========================================================
# MetricValidator
# ==========================================================


class MetricValidator:
    """
    Production metric validation engine.

    This class is intentionally non-instantiable.

    All validation entry points are implemented as
    static methods to keep validation:

    - deterministic
    - allocation free
    - thread safe
    - side-effect free
    """

    __slots__ = ()

    def __new__(
        cls,
        *args: Any,
        **kwargs: Any,
    ) -> "MetricValidator":

        raise TypeError(
            "MetricValidator cannot be instantiated."
        )

    # ======================================================
    # Internal Helpers
    # ======================================================

    @staticmethod
    def _normalize_string(
        value: str,
    ) -> str:
        """
        Normalize user supplied strings.
        """

        return value.strip()

    @staticmethod
    def _ensure_name(
        name: str,
    ) -> str:

        name = _require_str(
            name,
            "metric name",
        )

        return MetricValidator._normalize_string(
            name,
        )

    @staticmethod
    def _ensure_namespace(
        namespace: str,
    ) -> str:

        namespace = _require_str(
            namespace,
            "namespace",
        )

        return MetricValidator._normalize_string(
            namespace,
        )

    @staticmethod
    def _ensure_unit(
        unit: str,
    ) -> str:

        unit = _require_str(
            unit,
            "unit",
        )

        return MetricValidator._normalize_string(
            unit,
        )

    @staticmethod
    def _ensure_mapping(
        value: Mapping[str, Any],
        field: str,
    ) -> Mapping[str, Any]:

        return _require_mapping(
            value,
            field,
        )

    @staticmethod
    def _ensure_sequence(
        value: Sequence[Any],
        field: str,
    ) -> Sequence[Any]:

        return _require_sequence(
            value,
            field,
        )

    @staticmethod
    def _ensure_finite(
        value: Any,
        field: str,
    ) -> None:

        if isinstance(
            value,
            float,
        ):
            _check_finite(
                value,
                field,
            )

    # ======================================================
    # Primitive Validation
    # (Implemented in Part 2)
    # ======================================================

    @staticmethod
    def validate_name(
        name: str,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_unit(
        unit: str,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_description(
        description: str,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_namespace(
        namespace: str,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_uuid(
        value: str,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_version(
        version: str,
    ) -> None:
        raise NotImplementedError
    # ======================================================
    # 2A. String Validation
    # ======================================================

    @classmethod
    def validate_non_empty_string(
        cls,
        value: Any,
        *,
        field: str = "value",
        maximum: int | None = None,
        minimum: int = 1,
        strip: bool = True,
    ) -> str:
        """
        Validate a required non-empty string.

        Parameters
        ----------
        value
            Value to validate.

        field
            Field name used in error messages.

        maximum
            Optional maximum length.

        minimum
            Minimum allowed length after normalization.

        strip
            Strip surrounding whitespace before validation.

        Returns
        -------
        str
            Normalized string.

        Raises
        ------
        MetricValidationError
        """

        value = _require_str(
            value,
            field,
        )

        if strip:
            value = value.strip()

        if len(value) < minimum:

            raise MetricValidationError(
                f"{field} cannot be empty."
            )

        if (
            maximum is not None
            and len(value) > maximum
        ):

            raise MetricValidationError(
                f"{field} exceeds "
                f"{maximum} characters."
            )

        return value

    @classmethod
    def validate_optional_string(
        cls,
        value: Any,
        *,
        field: str = "value",
        default: str | None = None,
        maximum: int | None = None,
        strip: bool = True,
    ) -> str | None:
        """
        Validate an optional string.

        None is accepted and returned unchanged
        (or replaced with default).

        Returns
        -------
        str | None
        """

        if value is None:

            return default

        value = cls.validate_non_empty_string(
            value,
            field=field,
            maximum=maximum,
            minimum=1,
            strip=strip,
        )

        return value
    @classmethod
    def validate_identifier(
        cls,
        value: Any,
        *,
        field: str = "identifier",
        maximum: int = MAX_NAME_LENGTH,
        allow_keyword: bool = False,
        allow_reserved: bool = False,
    ) -> str:
        """
        Validate a generic identifier.

        Rules
        -----
        - required
        - normalized
        - Python identifier
        - not keyword (optional)
        - not reserved (optional)

        Returns
        -------
        str
            Normalized identifier.
        """

        value = cls.validate_non_empty_string(
            value,
            field=field,
            maximum=maximum,
        )

        _check_identifier(
            value,
            field,
        )

        if (
            not allow_keyword
            and _is_keyword(value)
        ):
            raise MetricValidationError(
                f"{field!r} cannot be "
                "a Python keyword."
            )

        if (
            not allow_reserved
            and _is_reserved_name(value)
        ):
            raise MetricValidationError(
                f"{field!r} is reserved."
            )

        return value

    @classmethod
    def validate_name(
        cls,
        name: Any,
    ) -> str:
        """
        Validate a metric name.

        Compatible with Prometheus/OpenTelemetry.

        Returns
        -------
        str
            Normalized metric name.
        """

        name = cls.validate_non_empty_string(
            name,
            field="metric name",
            maximum=MAX_NAME_LENGTH,
        )

        _check_pattern(
            name,
            pattern=METRIC_NAME_PATTERN,
            field="metric name",
        )

        _check_reserved(
            name,
            reserved=RESERVED_METRIC_NAMES,
            field="metric name",
        )

        _check_prefix(
            name,
        )

        return name
    @classmethod
    def validate_namespace(
        cls,
        namespace: Any,
        *,
        allow_default: bool = True,
    ) -> str:
        """
        Validate metric namespace.

        Rules
        -----
        - required
        - normalized
        - regex validated
        - reserved prefix check

        Returns
        -------
        str
        """

        namespace = cls.validate_non_empty_string(
            namespace,
            field="namespace",
            maximum=MAX_NAMESPACE_LENGTH,
        )

        if (
            allow_default
            and namespace == DEFAULT_NAMESPACE
        ):
            return namespace

        _check_pattern(
            namespace,
            pattern=NAMESPACE_PATTERN,
            field="namespace",
        )

        _check_prefix(
            namespace,
        )

        return namespace

    @classmethod
    def validate_unit(
        cls,
        unit: Any,
        *,
        allow_dimensionless: bool = True,
    ) -> str:
        """
        Validate metric unit.

        Compatible with
        OpenTelemetry semantic conventions.

        Examples
        --------
        s
        ms
        By
        MiBy
        %
        requests
        """

        unit = cls.validate_non_empty_string(
            unit,
            field="unit",
            maximum=MAX_UNIT_LENGTH,
        )

        if (
            allow_dimensionless
            and unit == DEFAULT_UNIT
        ):
            return unit

        _check_pattern(
            unit,
            pattern=UNIT_PATTERN,
            field="unit",
        )

        return unit

    @classmethod
    def validate_description(
        cls,
        description: Any,
    ) -> str:
        """
        Validate metric description.

        Empty descriptions are allowed
        by default.
        """

        if description is None:

            return DEFAULT_DESCRIPTION

        description = _require_str(
            description,
            "description",
        )

        description = description.strip()

        if (
            description == ""
            and ALLOW_EMPTY_DESCRIPTION
        ):
            return description

        _check_length(
            description,
            maximum=MAX_DESCRIPTION_LENGTH,
            field="description",
        )

        return description

    @classmethod
    def normalize_name(
        cls,
        name: str,
    ) -> str:
        """
        Normalize metric name.

        Validation is performed before
        normalization.
        """

        name = cls.validate_name(
            name,
        )

        return name.lower()

    @classmethod
    def normalize_namespace(
        cls,
        namespace: str,
    ) -> str:
        """
        Normalize namespace.
        """

        namespace = cls.validate_namespace(
            namespace,
        )

        return namespace.lower()

    @classmethod
    def normalize_unit(
        cls,
        unit: str,
    ) -> str:
        """
        Normalize unit.

        UCUM units are case-sensitive,
        therefore only surrounding
        whitespace is removed.
        """

        return cls.validate_unit(
            unit,
        )
    # ======================================================
    # 2B. Numeric Validation
    # ======================================================

    @classmethod
    def validate_numeric(
        cls,
        value: Any,
        *,
        field: str = "value",
        allow_bool: bool = False,
        allow_nan: bool = ALLOW_NAN,
        allow_infinity: bool = ALLOW_INFINITY,
    ) -> int | float | Decimal:
        """
        Validate a numeric value.

        Accepted
        --------
        - int
        - float
        - Decimal

        Rejected
        --------
        - complex
        - str
        - bytes
        - containers
        """

        if isinstance(value, bool):

            if allow_bool:
                return value

            raise MetricValidationError(
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

            raise MetricValidationError(
                f"{field} must be numeric."
            )

        if isinstance(
            value,
            Decimal,
        ):

            if not value.is_finite():

                raise MetricValidationError(
                    f"{field} must be finite."
                )

            return value

        if isinstance(
            value,
            float,
        ):

            if (
                math.isnan(value)
                and not allow_nan
            ):

                raise MetricValidationError(
                    f"{field} cannot be NaN."
                )

            if (
                math.isinf(value)
                and not allow_infinity
            ):

                raise MetricValidationError(
                    f"{field} cannot be infinite."
                )

        return value

    @classmethod
    def validate_integer(
        cls,
        value: Any,
        *,
        field: str = "value",
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """
        Validate integer.
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )

        if not isinstance(
            value,
            int,
        ) or isinstance(
            value,
            bool,
        ):

            raise MetricValidationError(
                f"{field} must be an integer."
            )

        if (
            minimum is not None
            and value < minimum
        ):

            raise MetricValidationError(
                f"{field} must be >= {minimum}."
            )

        if (
            maximum is not None
            and value > maximum
        ):

            raise MetricValidationError(
                f"{field} must be <= {maximum}."
            )

        return value

    @classmethod
    def validate_float(
        cls,
        value: Any,
        *,
        field: str = "value",
        minimum: float | None = None,
        maximum: float | None = None,
        allow_integer: bool = True,
    ) -> float:
        """
        Validate floating-point value.
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )

        if isinstance(
            value,
            Decimal,
        ):
            value = float(value)

        elif isinstance(
            value,
            int,
        ):

            if not allow_integer:

                raise MetricValidationError(
                    f"{field} must be float."
                )

            value = float(value)

        elif not isinstance(
            value,
            float,
        ):

            raise MetricValidationError(
                f"{field} must be float."
            )

        if (
            minimum is not None
            and value < minimum
        ):

            raise MetricValidationError(
                f"{field} must be >= {minimum}."
            )

        if (
            maximum is not None
            and value > maximum
        ):

            raise MetricValidationError(
                f"{field} must be <= {maximum}."
            )

        return value
    @classmethod
    def validate_finite(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> int | float | Decimal:
        """
        Validate that a numeric value is finite.

        Returns
        -------
        int | float | Decimal
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )

        if isinstance(
            value,
            Decimal,
        ):

            if not value.is_finite():

                raise MetricValidationError(
                    f"{field} must be finite."
                )

            return value

        if isinstance(
            value,
            float,
        ):

            if not math.isfinite(
                value,
            ):

                raise MetricValidationError(
                    f"{field} must be finite."
                )

        return value

    @classmethod
    def validate_positive(
        cls,
        value: Any,
        *,
        field: str = "value",
        allow_zero: bool = False,
    ) -> int | float | Decimal:
        """
        Validate a positive numeric value.
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if allow_zero:

            if value < 0:

                raise MetricValidationError(
                    f"{field} must be >= 0."
                )

        else:

            if value <= 0:

                raise MetricValidationError(
                    f"{field} must be > 0."
                )

        return value

    @classmethod
    def validate_non_negative(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> int | float | Decimal:
        """
        Validate a non-negative value.
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if value < 0:

            raise MetricValidationError(
                f"{field} must be non-negative."
            )

        return value

    @classmethod
    def validate_range(
        cls,
        value: Any,
        *,
        minimum: int | float | Decimal | None = None,
        maximum: int | float | Decimal | None = None,
        inclusive_min: bool = True,
        inclusive_max: bool = True,
        field: str = "value",
    ) -> int | float | Decimal:
        """
        Validate a numeric range.

        Parameters
        ----------
        minimum
            Lower bound.

        maximum
            Upper bound.

        inclusive_min
            Include lower bound.

        inclusive_max
            Include upper bound.
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if minimum is not None:

            if inclusive_min:

                if value < minimum:

                    raise MetricValidationError(
                        f"{field} must be >= {minimum}."
                    )

            else:

                if value <= minimum:

                    raise MetricValidationError(
                        f"{field} must be > {minimum}."
                    )

        if maximum is not None:

            if inclusive_max:

                if value > maximum:

                    raise MetricValidationError(
                        f"{field} must be <= {maximum}."
                    )

            else:

                if value >= maximum:

                    raise MetricValidationError(
                        f"{field} must be < {maximum}."
                    )

        return value
    # ======================================================
    # Metric Semantic Validation
    # ======================================================

    @classmethod
    def validate_counter_value(
        cls,
        value: Any,
        *,
        field: str = "counter",
        strict: bool = True,
    ) -> int | float | Decimal:
        """
        Validate Counter value.

        OpenTelemetry Counter semantics:
            • numeric
            • finite
            • monotonic
            • non-negative

        Parameters
        ----------
        strict:
            Reserved for future compatibility policies.

        Returns
        -------
        int | float | Decimal
        """

        value = cls.validate_non_negative(
            value,
            field=field,
        )

        if strict:

            if isinstance(value, bool):

                raise InvalidMetricTypeError(
                    f"{field} cannot be bool."
                )

        return value

    @classmethod
    def validate_up_down_counter_value(
        cls,
        value: Any,
        *,
        field: str = "up_down_counter",
        strict: bool = True,
    ) -> int | float | Decimal:
        """
        Validate UpDownCounter value.

        OpenTelemetry UpDownCounter:

            • numeric
            • finite
            • positive or negative
            • zero allowed
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if strict:

            if isinstance(value, bool):

                raise InvalidMetricTypeError(
                    f"{field} cannot be bool."
                )

        return value

    @classmethod
    def validate_gauge_value(
        cls,
        value: Any,
        *,
        field: str = "gauge",
        strict: bool = True,
    ) -> int | float | Decimal:
        """
        Validate Gauge value.

        Gauge represents an instantaneous
        measurement.

        Allowed:

            • positive
            • negative
            • zero

        Rejected:

            • NaN
            • Infinity
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if strict:

            if isinstance(value, bool):

                raise InvalidMetricTypeError(
                    f"{field} cannot be bool."
                )

        return value

    # ======================================================
    # Internal Metric Helpers
    # ======================================================

    @classmethod
    def _validate_metric_numeric(
        cls,
        value: Any,
        *,
        field: str,
    ) -> int | float | Decimal:
        """
        Internal helper shared by all
        metric validators.

        Ensures the value is:

        • numeric
        • finite
        • not bool
        """

        value = cls.validate_finite(
            value,
            field=field,
        )

        if isinstance(
            value,
            bool,
        ):

            raise InvalidMetricTypeError(
                f"{field} cannot be bool."
            )

        return value
                                                                        