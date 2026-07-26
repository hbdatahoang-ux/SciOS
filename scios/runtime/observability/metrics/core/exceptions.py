"""
SciOS Observability
==================

Exception hierarchy for the SciOS-NG Observability subsystem.

This module provides the common exception foundation used by all
metric components, including:

    • Metrics
    • Registry
    • Collectors
    • Exporters
    • Validation
    • Runtime
    • Serialization
    • Context propagation
    • Distributed execution

Design Goals
------------
- Strongly typed exceptions
- Stable error codes
- Machine-readable metadata
- Human-friendly messages
- Thread-safe
- Exporter friendly
- Logging friendly
- Production diagnostics

Notes
-----
All observability exceptions should inherit from ``MetricError``.
"""

from __future__ import annotations

import time
import traceback
import uuid

from enum import Enum
from typing import Any
from typing import Final
from typing import Mapping
from typing import TypeAlias

__all__ = [
    "ErrorSeverity",
    "MetricErrorCode",
]

# ==========================================================
# Error Codes
# ==========================================================


class MetricErrorCode(str, Enum):
    """
    Stable error codes.

    Error codes are intended for:

    • logging

    • telemetry

    • exporters

    • APIs

    • dashboards

    They should remain stable across releases.
    """

    # ----------------------------------
    # Generic
    # ----------------------------------

    UNKNOWN = "METRIC_UNKNOWN"

    INTERNAL = "METRIC_INTERNAL"

    RUNTIME = "METRIC_RUNTIME"

    NOT_IMPLEMENTED = "METRIC_NOT_IMPLEMENTED"

    # ----------------------------------
    # Validation
    # ----------------------------------

    VALIDATION = "METRIC_VALIDATION"

    INVALID_NAME = "INVALID_NAME"

    INVALID_UNIT = "INVALID_UNIT"

    INVALID_DESCRIPTION = "INVALID_DESCRIPTION"

    INVALID_LABEL = "INVALID_LABEL"

    INVALID_ATTRIBUTE = "INVALID_ATTRIBUTE"

    INVALID_METADATA = "INVALID_METADATA"

    INVALID_CONTEXT = "INVALID_CONTEXT"

    INVALID_VALUE = "INVALID_VALUE"

    INVALID_TYPE = "INVALID_TYPE"

    # ----------------------------------
    # Lifecycle
    # ----------------------------------

    FROZEN = "METRIC_FROZEN"

    CLOSED = "METRIC_CLOSED"

    DISABLED = "METRIC_DISABLED"

    READ_ONLY = "METRIC_READ_ONLY"

    ALREADY_EXISTS = "METRIC_ALREADY_EXISTS"

    NOT_FOUND = "METRIC_NOT_FOUND"

    # ----------------------------------
    # Runtime
    # ----------------------------------

    SNAPSHOT = "METRIC_SNAPSHOT"

    SERIALIZATION = "METRIC_SERIALIZATION"

    EXPORT = "METRIC_EXPORT"

    IMPORT = "METRIC_IMPORT"

    REGISTRY = "METRIC_REGISTRY"

    COLLECTOR = "METRIC_COLLECTOR"

    # ----------------------------------
    # Concurrency
    # ----------------------------------

    LOCK = "METRIC_LOCK"

    VERSION = "METRIC_VERSION"

    TIMEOUT = "METRIC_TIMEOUT"

    CAS = "METRIC_COMPARE_AND_SWAP"

    # ----------------------------------
    # Distributed
    # ----------------------------------

    PROPAGATION = "METRIC_PROPAGATION"

    TRACE = "METRIC_TRACE"

    BACKEND = "METRIC_BACKEND"

    NETWORK = "METRIC_NETWORK"


# ==========================================================
# Severity
# ==========================================================


class ErrorSeverity(str, Enum):
    """
    Exception severity.

    Compatible with common logging systems.
    """

    DEBUG = "debug"

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    CRITICAL = "critical"

    FATAL = "fatal"


# ==========================================================
# Type Aliases
# ==========================================================

ErrorDetails: TypeAlias = Mapping[str, Any]

ErrorUUID: TypeAlias = str


# ==========================================================
# Constants
# ==========================================================

DEFAULT_ERROR_CODE: Final = MetricErrorCode.UNKNOWN

DEFAULT_SEVERITY: Final = ErrorSeverity.ERROR

MAX_MESSAGE_LENGTH: Final[int] = 4096


# ==========================================================
# Helper Functions
# ==========================================================


def utc_timestamp() -> float:
    """
    Current UTC timestamp.
    """

    return time.time()


def generate_error_id() -> ErrorUUID:
    """
    Generate globally unique error identifier.
    """

    return uuid.uuid4().hex


def truncate_message(
    message: str,
    *,
    limit: int = MAX_MESSAGE_LENGTH,
) -> str:
    """
    Truncate oversized messages.
    """

    if len(message) <= limit:
        return message

    return message[: limit - 3] + "..."


def capture_traceback() -> str:
    """
    Capture current traceback.
    """

    return traceback.format_exc()


def normalize_details(
    details: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """
    Normalize optional details mapping.
    """

    if details is None:
        return {}

    return dict(details)


def normalize_message(
    message: str | Exception,
) -> str:
    """
    Normalize exception message.
    """

    if isinstance(message, Exception):
        return str(message)

    return truncate_message(
        str(message)
    )


def normalize_error_code(
    code: MetricErrorCode | str | None,
) -> MetricErrorCode:
    """
    Normalize error code.
    """

    if code is None:
        return DEFAULT_ERROR_CODE

    if isinstance(code, MetricErrorCode):
        return code

    try:
        return MetricErrorCode(code)

    except ValueError:
        return MetricErrorCode.UNKNOWN


def normalize_severity(
    severity: ErrorSeverity | str | None,
) -> ErrorSeverity:
    """
    Normalize severity.
    """

    if severity is None:
        return DEFAULT_SEVERITY

    if isinstance(
        severity,
        ErrorSeverity,
    ):
        return severity

    try:
        return ErrorSeverity(severity)

    except ValueError:
        return DEFAULT_SEVERITY


def build_error_record(
    *,
    message: str,
    code: MetricErrorCode,
    severity: ErrorSeverity,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a structured error record.

    This helper is shared by all MetricError subclasses.
    """

    return {
        "id": generate_error_id(),
        "timestamp": utc_timestamp(),
        "message": normalize_message(message),
        "code": normalize_error_code(code).value,
        "severity": normalize_severity(severity).value,
        "details": normalize_details(details),
    }
# ==========================================================
# Part 2. Base Exceptions
# ==========================================================


class MetricError(RuntimeError):
    """
    Base exception for the SciOS Observability subsystem.

    All metric-related exceptions inherit from this class.

    Features
    --------
    - Stable error code
    - Severity level
    - Timestamp
    - UUID
    - Structured details
    - Cause chaining
    - Diagnostics
    """

    __slots__ = (
        "_id",
        "_timestamp",
        "_message",
        "_code",
        "_severity",
        "_details",
        "_cause",
    )

    def __init__(
        self,
        message: str = "Metric error.",
        *,
        code: MetricErrorCode = MetricErrorCode.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        message = normalize_message(message)

        super().__init__(message)

        self._id = generate_error_id()

        self._timestamp = utc_timestamp()

        self._message = message

        self._code = normalize_error_code(code)

        self._severity = normalize_severity(severity)

        self._details = normalize_details(details)

        self._cause = cause

    # ======================================================
    # Properties
    # ======================================================

    @property
    def id(self) -> str:
        return self._id

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def message(self) -> str:
        return self._message

    @property
    def code(self) -> MetricErrorCode:
        return self._code

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity

    @property
    def details(self) -> Mapping[str, Any]:
        return dict(self._details)

    @property
    def cause(self) -> BaseException | None:
        return self._cause

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize exception to a structured dictionary.
        """

        return {
            "id": self._id,
            "timestamp": self._timestamp,
            "type": self.__class__.__name__,
            "message": self._message,
            "code": self._code.value,
            "severity": self._severity.value,
            "details": dict(self._details),
            "cause": (
                repr(self._cause)
                if self._cause is not None
                else None
            ),
        }

    # ======================================================
    # Helpers
    # ======================================================

    def diagnostics(self) -> dict[str, Any]:
        """
        Diagnostic information for logging/export.
        """

        return self.to_dict()

    # ======================================================
    # String representation
    # ======================================================

    def __str__(self) -> str:
        return (
            f"[{self._code.value}] "
            f"{self._message}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code={self._code.value!r}, "
            f"severity={self._severity.value!r}, "
            f"message={self._message!r})"
        )


# ==========================================================
# Runtime Exception
# ==========================================================


class MetricRuntimeError(MetricError):
    """
    Runtime failure during metric execution.

    Examples
    --------
    - collection failure
    - exporter failure
    - registry failure
    - runtime state corruption
    """

    def __init__(
        self,
        message: str = "Metric runtime error.",
        *,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            code=MetricErrorCode.RUNTIME,
            severity=ErrorSeverity.ERROR,
            details=details,
            cause=cause,
        )


# ==========================================================
# Internal Exception
# ==========================================================


class MetricInternalError(MetricError):
    """
    Internal invariant violation.

    This exception indicates a bug or an unexpected internal
    state rather than an invalid user operation.
    """

    def __init__(
        self,
        message: str = "Internal metric error.",
        *,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            code=MetricErrorCode.INTERNAL,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            cause=cause,
        )
# ==========================================================
# Part 3. Validation Exceptions
# ==========================================================


class MetricValidationError(MetricError):
    """
    Base exception for metric validation failures.
    """

    __slots__ = (
        "_field",
        "_value",
        "_expected",
    )

    def __init__(
        self,
        message: str = "Metric validation failed.",
        *,
        code: MetricErrorCode = MetricErrorCode.VALIDATION,
        field: str | None = None,
        value: Any = None,
        expected: Any = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            code=code,
            severity=ErrorSeverity.ERROR,
            details=details,
            cause=cause,
        )

        self._field = field
        self._value = value
        self._expected = expected

    # ======================================================
    # Properties
    # ======================================================

    @property
    def field(self) -> str | None:
        return self._field

    @property
    def value(self) -> Any:
        return self._value

    @property
    def expected(self) -> Any:
        return self._expected

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "field": self._field,
                "value": self._value,
                "expected": self._expected,
            }
        )

        return data


# ==========================================================
# Invalid Metric Name
# ==========================================================


class InvalidMetricNameError(MetricValidationError):
    """
    Raised when a metric name is invalid.
    """

    def __init__(
        self,
        name: Any,
        *,
        expected: str = (
            "Prometheus/OpenTelemetry compatible metric name"
        ),
    ) -> None:

        super().__init__(
            message=f"Invalid metric name: {name!r}",
            code=MetricErrorCode.INVALID_NAME,
            field="name",
            value=name,
            expected=expected,
        )


# ==========================================================
# Invalid Metric Unit
# ==========================================================


class InvalidMetricUnitError(MetricValidationError):
    """
    Raised when a metric unit is invalid.
    """

    def __init__(
        self,
        unit: Any,
        *,
        expected: str = "UCUM unit or '1'",
    ) -> None:

        super().__init__(
            message=f"Invalid metric unit: {unit!r}",
            code=MetricErrorCode.INVALID_UNIT,
            field="unit",
            value=unit,
            expected=expected,
        )


# ==========================================================
# Invalid Metric Type
# ==========================================================


class InvalidMetricTypeError(MetricValidationError):
    """
    Raised when a metric type is unsupported.
    """

    def __init__(
        self,
        metric_type: Any,
        *,
        expected: Any = (
            "MetricType enum value"
        ),
    ) -> None:

        super().__init__(
            message=f"Invalid metric type: {metric_type!r}",
            code=MetricErrorCode.INVALID_TYPE,
            field="metric_type",
            value=metric_type,
            expected=expected,
        )


# ==========================================================
# Invalid Labels
# ==========================================================


class InvalidLabelError(MetricValidationError):
    """
    Raised when metric labels are invalid.
    """

    def __init__(
        self,
        labels: Any,
        *,
        expected: str = (
            "Mapping[str, Any]"
        ),
    ) -> None:

        super().__init__(
            message="Invalid metric labels.",
            code=MetricErrorCode.INVALID_LABEL,
            field="labels",
            value=labels,
            expected=expected,
        )


# ==========================================================
# Invalid Attributes
# ==========================================================


class InvalidAttributeError(MetricValidationError):
    """
    Raised when metric attributes are invalid.
    """

    def __init__(
        self,
        attributes: Any,
        *,
        expected: str = (
            "Mapping[str, Any]"
        ),
    ) -> None:

        super().__init__(
            message="Invalid metric attributes.",
            code=MetricErrorCode.INVALID_ATTRIBUTE,
            field="attributes",
            value=attributes,
            expected=expected,
        )


# ==========================================================
# Invalid Metadata
# ==========================================================


class InvalidMetadataError(MetricValidationError):
    """
    Raised when metric metadata is invalid.
    """

    def __init__(
        self,
        metadata: Any,
        *,
        expected: str = (
            "MetricMetadata or Mapping[str, Any]"
        ),
    ) -> None:

        super().__init__(
            message="Invalid metric metadata.",
            code=MetricErrorCode.INVALID_METADATA,
            field="metadata",
            value=metadata,
            expected=expected,
        )
# ==========================================================
# Part 4. Lifecycle Exceptions
# ==========================================================


class MetricLifecycleError(MetricRuntimeError):
    """
    Base exception for metric lifecycle failures.

    Examples
    --------
    - frozen
    - closed
    - disabled
    - read-only
    """

    __slots__ = (
        "_resource",
        "_state",
        "_expected_state",
    )

    def __init__(
        self,
        message: str = "Metric lifecycle error.",
        *,
        code: MetricErrorCode = MetricErrorCode.RUNTIME,
        resource: str | None = None,
        state: str | None = None,
        expected_state: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            details=details,
            cause=cause,
        )

        self._code = code

        self._resource = resource

        self._state = state

        self._expected_state = expected_state

    # ======================================================
    # Properties
    # ======================================================

    @property
    def resource(
        self,
    ) -> str | None:

        return self._resource

    @property
    def state(
        self,
    ) -> str | None:

        return self._state

    @property
    def expected_state(
        self,
    ) -> str | None:

        return self._expected_state

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "resource": self._resource,
                "state": self._state,
                "expected_state": self._expected_state,
            }
        )

        return data


# ==========================================================
# Frozen
# ==========================================================


class MetricFrozenError(MetricLifecycleError):
    """
    Raised when attempting to mutate a frozen metric.
    """

    def __init__(
        self,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message=f"{resource} is frozen.",
            code=MetricErrorCode.FROZEN,
            resource=resource,
            state="frozen",
            expected_state="mutable",
        )


# ==========================================================
# Closed
# ==========================================================


class MetricClosedError(MetricLifecycleError):
    """
    Raised when operating on a closed metric.
    """

    def __init__(
        self,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message=f"{resource} is closed.",
            code=MetricErrorCode.CLOSED,
            resource=resource,
            state="closed",
            expected_state="open",
        )


# ==========================================================
# Disabled
# ==========================================================


class MetricDisabledError(MetricLifecycleError):
    """
    Raised when using a disabled metric.
    """

    def __init__(
        self,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message=f"{resource} is disabled.",
            code=MetricErrorCode.DISABLED,
            resource=resource,
            state="disabled",
            expected_state="enabled",
        )


# ==========================================================
# Read Only
# ==========================================================


class MetricReadOnlyError(MetricLifecycleError):
    """
    Raised when modifying a read-only metric.
    """

    def __init__(
        self,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message=f"{resource} is read-only.",
            code=MetricErrorCode.READ_ONLY,
            resource=resource,
            state="read_only",
            expected_state="writable",
        )


# ==========================================================
# Already Exists
# ==========================================================


class MetricAlreadyExistsError(MetricLifecycleError):
    """
    Raised when attempting to register an existing metric.
    """

    def __init__(
        self,
        name: str,
    ) -> None:

        super().__init__(
            message=f"Metric '{name}' already exists.",
            code=MetricErrorCode.ALREADY_EXISTS,
            resource=name,
            state="registered",
            expected_state="not_registered",
        )


# ==========================================================
# Not Found
# ==========================================================


class MetricNotFoundError(MetricLifecycleError):
    """
    Raised when a metric cannot be located.
    """

    def __init__(
        self,
        name: str,
    ) -> None:

        super().__init__(
            message=f"Metric '{name}' was not found.",
            code=MetricErrorCode.NOT_FOUND,
            resource=name,
            state="missing",
            expected_state="existing",
        )
# ==========================================================
# Part 5. Runtime Exceptions
# ==========================================================


class MetricOperationError(MetricRuntimeError):
    """
    Base exception for runtime metric operations.

    Used for failures during:

    - collection
    - export
    - serialization
    - registry
    - snapshot
    - runtime context

    This class carries additional runtime metadata useful for
    diagnostics and observability.
    """

    __slots__ = (
        "_operation",
        "_resource",
        "_component",
    )

    def __init__(
        self,
        message: str = "Metric runtime operation failed.",
        *,
        code: MetricErrorCode = MetricErrorCode.RUNTIME,
        operation: str | None = None,
        resource: str | None = None,
        component: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            details=details,
            cause=cause,
        )

        self._code = code

        self._operation = operation

        self._resource = resource

        self._component = component

    # ======================================================
    # Properties
    # ======================================================

    @property
    def operation(self) -> str | None:
        return self._operation

    @property
    def resource(self) -> str | None:
        return self._resource

    @property
    def component(self) -> str | None:
        return self._component

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "operation": self._operation,
                "resource": self._resource,
                "component": self._component,
            }
        )

        return data


# ==========================================================
# Overflow
# ==========================================================


class MetricOverflowError(MetricOperationError):
    """
    Raised when a metric exceeds supported limits.
    """

    def __init__(
        self,
        *,
        resource: str = "metric",
        value: Any = None,
        maximum: Any = None,
    ) -> None:

        super().__init__(
            message=f"{resource} overflow detected.",
            code=MetricErrorCode.RUNTIME,
            operation="overflow",
            resource=resource,
            component="runtime",
            details={
                "value": value,
                "maximum": maximum,
            },
        )


# ==========================================================
# Export
# ==========================================================


class MetricExportError(MetricOperationError):
    """
    Raised when exporting metrics fails.
    """

    def __init__(
        self,
        exporter: str,
        *,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=f"Metric export failed via '{exporter}'.",
            code=MetricErrorCode.EXPORT,
            operation="export",
            resource=exporter,
            component="exporter",
            details=details,
            cause=cause,
        )


# ==========================================================
# Serialization
# ==========================================================


class MetricSerializationError(MetricOperationError):
    """
    Raised when serialization/deserialization fails.
    """

    def __init__(
        self,
        *,
        format: str | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message="Metric serialization failed.",
            code=MetricErrorCode.SERIALIZATION,
            operation="serialization",
            resource=format,
            component="serializer",
            cause=cause,
        )


# ==========================================================
# Snapshot
# ==========================================================


class MetricSnapshotError(MetricOperationError):
    """
    Raised when snapshot operations fail.
    """

    def __init__(
        self,
        *,
        operation: str = "snapshot",
        details: Mapping[str, Any] | None = None,
    ) -> None:

        super().__init__(
            message="Metric snapshot operation failed.",
            code=MetricErrorCode.SNAPSHOT,
            operation=operation,
            component="snapshot",
            details=details,
        )


# ==========================================================
# Context
# ==========================================================


class MetricContextError(MetricOperationError):
    """
    Raised when metric context operations fail.
    """

    def __init__(
        self,
        *,
        operation: str = "context",
        details: Mapping[str, Any] | None = None,
    ) -> None:

        super().__init__(
            message="Metric context operation failed.",
            code=MetricErrorCode.INVALID_CONTEXT,
            operation=operation,
            component="context",
            details=details,
        )


# ==========================================================
# Registry
# ==========================================================


class MetricRegistryError(MetricOperationError):
    """
    Raised when registry operations fail.
    """

    def __init__(
        self,
        *,
        operation: str = "registry",
        details: Mapping[str, Any] | None = None,
    ) -> None:

        super().__init__(
            message="Metric registry operation failed.",
            code=MetricErrorCode.REGISTRY,
            operation=operation,
            component="registry",
            details=details,
        )


# ==========================================================
# Collector
# ==========================================================


class MetricCollectorError(MetricOperationError):
    """
    Raised when metric collection fails.
    """

    def __init__(
        self,
        *,
        collector: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message="Metric collection failed.",
            code=MetricErrorCode.COLLECTOR,
            operation="collect",
            resource=collector,
            component="collector",
            details=details,
            cause=cause,
        )
# ==========================================================
# Part 6. Concurrency Exceptions
# ==========================================================


class MetricConcurrencyError(MetricRuntimeError):
    """
    Base exception for metric concurrency failures.

    Raised when concurrent access, synchronization, or
    optimistic locking fails.
    """

    __slots__ = (
        "_resource",
        "_operation",
        "_thread_id",
    )

    def __init__(
        self,
        message: str = "Metric concurrency error.",
        *,
        code: MetricErrorCode = MetricErrorCode.LOCK,
        resource: str | None = None,
        operation: str | None = None,
        thread_id: int | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            details=details,
            cause=cause,
        )

        self._code = code
        self._resource = resource
        self._operation = operation
        self._thread_id = thread_id

    # ======================================================
    # Properties
    # ======================================================

    @property
    def resource(self) -> str | None:
        return self._resource

    @property
    def operation(self) -> str | None:
        return self._operation

    @property
    def thread_id(self) -> int | None:
        return self._thread_id

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "resource": self._resource,
                "operation": self._operation,
                "thread_id": self._thread_id,
            }
        )

        return data


# ==========================================================
# Lock Error
# ==========================================================


class MetricLockError(MetricConcurrencyError):
    """
    Raised when acquiring or releasing a metric lock fails.
    """

    def __init__(
        self,
        *,
        resource: str = "metric",
        operation: str = "lock",
        thread_id: int | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=f"Lock operation failed for '{resource}'.",
            code=MetricErrorCode.LOCK,
            resource=resource,
            operation=operation,
            thread_id=thread_id,
            cause=cause,
        )


# ==========================================================
# Version Mismatch
# ==========================================================


class MetricVersionMismatchError(MetricConcurrencyError):
    """
    Raised when optimistic version checking fails.
    """

    __slots__ = (
        "_expected_version",
        "_actual_version",
    )

    def __init__(
        self,
        *,
        expected_version: int,
        actual_version: int,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message="Metric version mismatch.",
            code=MetricErrorCode.VERSION,
            resource=resource,
            operation="version_check",
            details={
                "expected_version": expected_version,
                "actual_version": actual_version,
            },
        )

        self._expected_version = expected_version
        self._actual_version = actual_version

    @property
    def expected_version(self) -> int:
        return self._expected_version

    @property
    def actual_version(self) -> int:
        return self._actual_version

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "expected_version": self._expected_version,
                "actual_version": self._actual_version,
            }
        )

        return data


# ==========================================================
# Compare-And-Swap Failure
# ==========================================================


class MetricCASFailure(MetricConcurrencyError):
    """
    Raised when an atomic compare-and-swap operation fails.
    """

    __slots__ = (
        "_expected",
        "_observed",
    )

    def __init__(
        self,
        *,
        expected: Any,
        observed: Any,
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message="Compare-and-swap operation failed.",
            code=MetricErrorCode.CAS,
            resource=resource,
            operation="compare_and_swap",
            details={
                "expected": expected,
                "observed": observed,
            },
        )

        self._expected = expected
        self._observed = observed

    @property
    def expected(self) -> Any:
        return self._expected

    @property
    def observed(self) -> Any:
        return self._observed

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "expected": self._expected,
                "observed": self._observed,
            }
        )

        return data


# ==========================================================
# Timeout
# ==========================================================


class MetricTimeoutError(MetricConcurrencyError):
    """
    Raised when a metric operation exceeds its timeout.
    """

    __slots__ = (
        "_timeout",
        "_elapsed",
    )

    def __init__(
        self,
        *,
        timeout: float,
        elapsed: float | None = None,
        operation: str = "operation",
        resource: str = "metric",
    ) -> None:

        super().__init__(
            message=f"Metric {operation} timed out.",
            code=MetricErrorCode.TIMEOUT,
            resource=resource,
            operation=operation,
            details={
                "timeout": timeout,
                "elapsed": elapsed,
            },
        )

        self._timeout = timeout
        self._elapsed = elapsed

    @property
    def timeout(self) -> float:
        return self._timeout

    @property
    def elapsed(self) -> float | None:
        return self._elapsed

    def to_dict(self) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "timeout": self._timeout,
                "elapsed": self._elapsed,
            }
        )

        return data
# ==========================================================
# Part 7. Distributed Exceptions
# ==========================================================


class MetricDistributedError(MetricRuntimeError):
    """
    Base exception for distributed observability failures.

    Covers failures involving:

    - distributed schedulers
    - remote workers
    - tracing
    - exporters
    - context propagation
    - remote backends
    """

    __slots__ = (
        "_component",
        "_endpoint",
        "_resource",
    )

    def __init__(
        self,
        message: str = "Distributed metric error.",
        *,
        code: MetricErrorCode = MetricErrorCode.BACKEND,
        component: str | None = None,
        endpoint: str | None = None,
        resource: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message=message,
            details=details,
            cause=cause,
        )

        self._code = code

        self._component = component

        self._endpoint = endpoint

        self._resource = resource

    # ======================================================
    # Properties
    # ======================================================

    @property
    def component(
        self,
    ) -> str | None:

        return self._component

    @property
    def endpoint(
        self,
    ) -> str | None:

        return self._endpoint

    @property
    def resource(
        self,
    ) -> str | None:

        return self._resource

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = super().to_dict()

        data.update(
            {
                "component": self._component,
                "endpoint": self._endpoint,
                "resource": self._resource,
            }
        )

        return data


# ==========================================================
# Context Propagation
# ==========================================================


class MetricPropagationError(MetricDistributedError):
    """
    Raised when context propagation fails.
    """

    def __init__(
        self,
        *,
        protocol: str | None = None,
        endpoint: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message="Metric context propagation failed.",
            code=MetricErrorCode.PROPAGATION,
            component=protocol,
            endpoint=endpoint,
            details=details,
            cause=cause,
        )


# ==========================================================
# Trace
# ==========================================================


class MetricTraceError(MetricDistributedError):
    """
    Raised when distributed tracing fails.
    """

    def __init__(
        self,
        *,
        trace_id: str | None = None,
        span_id: str | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        super().__init__(
            message="Distributed trace operation failed.",
            code=MetricErrorCode.TRACE,
            component="trace",
            resource=trace_id,
            details={
                "trace_id": trace_id,
                "span_id": span_id,
                **(details or {}),
            },
            cause=cause,
        )


# ==========================================================
# Exporter Unavailable
# ==========================================================


class MetricExporterUnavailable(MetricDistributedError):
    """
    Raised when an exporter backend is unavailable.
    """

    def __init__(
        self,
        exporter: str,
        *,
        endpoint: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:

        super().__init__(
            message=f"Exporter '{exporter}' is unavailable.",
            code=MetricErrorCode.EXPORT,
            component=exporter,
            endpoint=endpoint,
            details=details,
        )


# ==========================================================
# Backend
# ==========================================================


class MetricBackendError(MetricDistributedError):
    """
    Raised when a remote observability backend fails.

    Examples
    --------
    - Prometheus Remote Write
    - OpenTelemetry Collector
    - Jaeger
    - Tempo
    - Kafka
    - Redis
    - Ray
    - Dask
    """

    def __init__(
        self,
        backend: str,
        *,
        endpoint: str | None = None,
        status: int | None = None,
        details: Mapping[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:

        payload = dict(details or {})

        if status is not None:
            payload["status"] = status

        super().__init__(
            message=f"Backend '{backend}' reported an error.",
            code=MetricErrorCode.BACKEND,
            component=backend,
            endpoint=endpoint,
            details=payload,
            cause=cause,
        )
# ==========================================================
# Part 8. Diagnostics
# ==========================================================

class MetricDiagnosticsMixin:
    """
    Shared diagnostic helpers for all metric exceptions.
    """

    @property
    def error_code(self) -> MetricErrorCode:
        return self.code

    @property
    def severity(self) -> ErrorSeverity:
        return self._severity

    @property
    def details(self) -> Mapping[str, Any]:
        return dict(self._details)

    def diagnostics(self) -> dict[str, Any]:
        return self.to_dict()

    def format(self) -> str:
        return (
            f"[{self.code.value}] "
            f"{self.message}"
        )

    def pretty(self) -> str:
        import json

        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
            default=str,
        )

    def dump(self) -> dict[str, Any]:
        return self.to_dict()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code={self.code.value!r}, "
            f"severity={self.severity.value!r}, "
            f"message={self.message!r})"
        )
# ==========================================================
# Part 9. Production Helpers
# ==========================================================

from collections.abc import Callable
from typing import TypeVar

_T = TypeVar("_T")


# ==========================================================
# wrap()
# ==========================================================

def wrap(
    exc: BaseException,
    *,
    message: str | None = None,
    code: MetricErrorCode = MetricErrorCode.INTERNAL,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    details: Mapping[str, Any] | None = None,
) -> MetricError:
    """
    Wrap any exception into MetricError.

    Existing MetricError instances are returned unchanged.

    Examples
    --------
    try:
        ...
    except Exception as exc:
        raise wrap(exc)
    """

    if isinstance(exc, MetricError):
        return exc

    return MetricInternalError(
        message=message or str(exc),
        details={
            "wrapped_exception": exc.__class__.__name__,
            **(dict(details) if details else {}),
        },
        cause=exc,
    )


# ==========================================================
# raise_if()
# ==========================================================

def raise_if(
    condition: bool,
    exception: MetricError | type[MetricError],
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Raise an exception when condition is True.

    Examples
    --------
    raise_if(value < 0,
             MetricValidationError,
             "Negative value")

    raise_if(
        metric.frozen,
        MetricFrozenError()
    )
    """

    if not condition:
        return

    if isinstance(exception, MetricError):
        raise exception

    raise exception(*args, **kwargs)


# ==========================================================
# format_exception()
# ==========================================================

def format_exception(
    exc: BaseException,
    *,
    include_traceback: bool = False,
) -> str:
    """
    Format exception for logging.

    Parameters
    ----------
    include_traceback
        Include traceback if available.
    """

    if isinstance(exc, MetricError):

        text = (
            f"[{exc.code.value}] "
            f"{exc.message}"
        )

    else:

        text = (
            f"{exc.__class__.__name__}: "
            f"{exc}"
        )

    if include_traceback:

        tb = capture_traceback()

        if tb.strip():

            text += "\n\n"

            text += tb

    return text


# ==========================================================
# safe_execute()
# ==========================================================

def safe_execute(
    func: Callable[..., _T],
    *args: Any,
    **kwargs: Any,
) -> _T:
    """
    Execute callable.

    Unexpected exceptions are automatically wrapped.

    Examples
    --------
    value = safe_execute(
        exporter.export,
        snapshot,
    )
    """

    try:

        return func(
            *args,
            **kwargs,
        )

    except MetricError:

        raise

    except Exception as exc:

        raise wrap(exc) from exc


# ==========================================================
# exception_to_record()
# ==========================================================

def exception_to_record(
    exc: BaseException,
) -> dict[str, Any]:
    """
    Convert exception into structured record.
    """

    if isinstance(
        exc,
        MetricError,
    ):

        return exc.to_dict()

    return {

        "type":
            exc.__class__.__name__,

        "message":
            str(exc),

    }


# ==========================================================
# Final Polish
# ==========================================================

def is_metric_exception(
    exc: BaseException,
) -> bool:
    """
    Return True if exception belongs to
    the Metric exception hierarchy.
    """

    return isinstance(
        exc,
        MetricError,
    )


def root_cause(
    exc: BaseException,
) -> BaseException:
    """
    Return deepest cause.

    Supports chained exceptions.
    """

    current = exc

    while getattr(
        current,
        "__cause__",
        None,
    ) is not None:

        current = current.__cause__

    return current


def exception_name(
    exc: BaseException,
) -> str:
    """
    Return exception class name.
    """

    return exc.__class__.__name__


def error_code_of(
    exc: BaseException,
) -> str:
    """
    Return stable error code.
    """

    if isinstance(
        exc,
        MetricError,
    ):
        return exc.code.value

    return MetricErrorCode.UNKNOWN.value


def severity_of(
    exc: BaseException,
) -> str:
    """
    Return exception severity.
    """

    if isinstance(
        exc,
        MetricError,
    ):
        return exc.severity.value

    return ErrorSeverity.ERROR.value   
    @classmethod
    def validate_histogram_value(
        cls,
        value: Any,
        *,
        field: str = "histogram",
        strict: bool = True,
        allow_zero: bool = True,
    ) -> int | float | Decimal:
        """
        Validate a Histogram observation.

        Histogram observations are expected to be
        finite numeric values. By default negative
        observations are rejected to align with
        latency, size and throughput measurements.
        """

        value = cls._validate_metric_numeric(
            value,
            field=field,
        )

        if allow_zero:
            cls._validate_bounds(
                value,
                minimum=0,
                field=field,
            )
        else:
            cls._validate_bounds(
                value,
                minimum=0,
                inclusive_min=False,
                field=field,
            )

        return value

    @classmethod
    def validate_summary_value(
        cls,
        value: Any,
        *,
        field: str = "summary",
        strict: bool = True,
        allow_zero: bool = True,
    ) -> int | float | Decimal:
        """
        Validate a Summary observation.

        Summary metrics generally represent latency,
        payload size or other positive observations.
        """

        value = cls._validate_metric_numeric(
            value,
            field=field,
        )

        if allow_zero:
            cls._validate_bounds(
                value,
                minimum=0,
                field=field,
            )
        else:
            cls._validate_bounds(
                value,
                minimum=0,
                inclusive_min=False,
                field=field,
            )

        return value

    @classmethod
    def validate_timer_value(
        cls,
        value: Any,
        *,
        field: str = "timer",
        allow_zero: bool = True,
        maximum: float | Decimal | None = None,
    ) -> int | float | Decimal:
        """
        Validate a timer duration.

        Durations must never be negative.
        """

        value = cls._validate_metric_numeric(
            value,
            field=field,
        )

        cls._validate_bounds(
            value,
            minimum=0,
            maximum=maximum,
            inclusive_min=allow_zero,
            field=field,
        )

        return value

    @classmethod
    def validate_observable_value(
        cls,
        value: Any,
        *,
        field: str = "observable",
        callback: Callable[..., Any] | None = None,
    ) -> int | float | Decimal:
        """
        Validate an Observable instrument value.

        If a callback is supplied it will be invoked
        and its returned value will be validated.
        """

        if callback is not None:

            if not callable(callback):

                raise InvalidMetricTypeError(
                    f"{field} callback must be callable."
                )

            value = callback()

        return cls._validate_metric_numeric(
            value,
            field=field,
        )

    # ======================================================
    # Observable Helpers
    # ======================================================

    @classmethod
    def validate_observable_callback(
        cls,
        callback: Callable[..., Any],
    ) -> Callable[..., Any]:
        """
        Validate an observable callback without
        executing it.
        """

        if not callable(callback):

            raise InvalidMetricTypeError(
                "Observable callback must be callable."
            )

        return callback

    @classmethod
    def validate_measurement_sequence(
        cls,
        measurements: Iterable[Any],
        *,
        field: str = "measurements",
    ) -> tuple[int | float | Decimal, ...]:
        """
        Validate a sequence of observable
        measurements.
        """

        validated: list[int | float | Decimal] = []

        for value in measurements:

            validated.append(
                cls.validate_observable_value(
                    value,
                    field=field,
                )
            )

        return tuple(validated)
    # ======================================================
    # 2C. Boolean / UUID / Version Validation
    # ======================================================

    @classmethod
    def validate_boolean(
        cls,
        value: Any,
        *,
        field: str = "value",
        allow_none: bool = False,
    ) -> bool | None:
        """
        Validate a boolean value.

        Parameters
        ----------
        value
            Value to validate.

        allow_none
            Whether None is accepted.

        Returns
        -------
        bool | None
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if not isinstance(
            value,
            bool,
        ):

            raise InvalidMetricTypeError(
                f"{field} must be bool."
            )

        return value

    @classmethod
    def validate_uuid(
        cls,
        value: Any,
        *,
        field: str = "uuid",
        allow_none: bool = False,
        normalize: bool = True,
    ) -> str | None:
        """
        Validate a UUID.

        Accepted
        --------
        • uuid.UUID
        • UUID string

        Returns
        -------
        Canonical UUID string.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if isinstance(
            value,
            uuid.UUID,
        ):

                return str(value) if normalize else value.hex

        value = cls.validate_non_empty_string(
            value,
            field=field,
            maximum=64,
        )

        try:

            parsed = uuid.UUID(value)

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):

            raise MetricValidationError(
                f"Invalid UUID for {field}."
            ) from None

        return str(parsed) if normalize else parsed.hex

    @classmethod
    def validate_version(
        cls,
        value: Any,
        *,
        field: str = "version",
        allow_none: bool = False,
        maximum: int = 64,
    ) -> str | None:
        """
        Validate a semantic version.

        Supported examples
        ------------------
        1
        1.0
        1.0.0
        2.1.3-alpha
        2.1.3+build42
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            maximum=maximum,
        )

        if not _matches(
            VERSION_PATTERN,
            value,
        ):

            raise MetricValidationError(
                f"Invalid semantic version: {value!r}"
            )

        return value
    # ======================================================
    # 2D. Collection Validation
    # ======================================================

    @classmethod
    def validate_mapping(
        cls,
        value: Any,
        *,
        field: str = "mapping",
        allow_none: bool = False,
        key_type: type | tuple[type, ...] | None = None,
        value_type: type | tuple[type, ...] | None = None,
        minimum_size: int | None = None,
        maximum_size: int | None = None,
    ) -> Mapping[Any, Any] | None:
        """
        Validate a mapping object.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if not isinstance(
            value,
            Mapping,
        ):

            raise InvalidMetricTypeError(
                f"{field} must implement Mapping."
            )

        cls.validate_length(
            value,
            minimum=minimum_size,
            maximum=maximum_size,
            field=field,
        )

        if key_type is not None:

            for key in value:

                if not isinstance(
                    key,
                    key_type,
                ):

                    raise InvalidMetricTypeError(
                        f"{field} contains an invalid key type."
                    )

        if value_type is not None:

            for item in value.values():

                if not isinstance(
                    item,
                    value_type,
                ):

                    raise InvalidMetricTypeError(
                        f"{field} contains an invalid value type."
                    )

        return value

    @classmethod
    def validate_sequence(
        cls,
        value: Any,
        *,
        field: str = "sequence",
        allow_none: bool = False,
        item_type: type | tuple[type, ...] | None = None,
        minimum_size: int | None = None,
        maximum_size: int | None = None,
        allow_string: bool = False,
    ) -> Sequence[Any] | None:
        """
        Validate a sequence.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if (
            isinstance(
                value,
                (str, bytes, bytearray),
            )
            and not allow_string
        ):

            raise InvalidMetricTypeError(
                f"{field} must not be a string."
            )

        if not isinstance(
            value,
            Sequence,
        ):

            raise InvalidMetricTypeError(
                f"{field} must implement Sequence."
            )

        cls.validate_length(
            value,
            minimum=minimum_size,
            maximum=maximum_size,
            field=field,
        )

        if item_type is not None:

            for item in value:

                if not isinstance(
                    item,
                    item_type,
                ):

                    raise InvalidMetricTypeError(
                        f"{field} contains an invalid item type."
                    )

        return value

    @classmethod
    def validate_set(
        cls,
        value: Any,
        *,
        field: str = "set",
        allow_none: bool = False,
        item_type: type | tuple[type, ...] | None = None,
        minimum_size: int | None = None,
        maximum_size: int | None = None,
    ) -> set[Any] | frozenset[Any] | None:
        """
        Validate a set-like collection.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if not isinstance(
            value,
            (set, frozenset),
        ):

            raise InvalidMetricTypeError(
                f"{field} must be a set."
            )

        cls.validate_length(
            value,
            minimum=minimum_size,
            maximum=maximum_size,
            field=field,
        )

        if item_type is not None:

            for item in value:

                if not isinstance(
                    item,
                    item_type,
                ):

                    raise InvalidMetricTypeError(
                        f"{field} contains an invalid item type."
                    )

        return value

    @classmethod
    def validate_length(
        cls,
        value: Any,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
        exact: int | None = None,
        field: str = "value",
    ) -> int:
        """
        Validate the length of an object implementing __len__().

        Returns
        -------
        int
            Computed length.
        """

        try:

            length = len(value)

        except Exception as exc:

            raise InvalidMetricTypeError(
                f"{field} has no valid length."
            ) from exc

        if exact is not None and length != exact:

            raise MetricValidationError(
                f"{field} must contain exactly "
                f"{exact} element(s)."
            )

        if (
            minimum is not None
            and length < minimum
        ):

            raise MetricValidationError(
                f"{field} must contain at least "
                f"{minimum} element(s)."
            )

        if (
            maximum is not None
            and length > maximum
        ):

            raise MetricValidationError(
                f"{field} must contain at most "
                f"{maximum} element(s)."
            )

        return length
    # ======================================================
    # 2E. Pattern Validation
    # ======================================================

    @classmethod
    def validate_regex(
        cls,
        value: Any,
        *,
        pattern: str | Pattern[str],
        field: str = "value",
        flags: re.RegexFlag | int = 0,
        fullmatch: bool = True,
        allow_none: bool = False,
        strip: bool = True,
    ) -> str | None:
        """
        Validate a string against a regular expression.

        Parameters
        ----------
        value
            Value to validate.

        pattern
            Compiled regex or regex pattern string.

        field
            Field name used in exception messages.

        flags
            Regex compilation flags when `pattern` is a string.

        fullmatch
            If True, the entire string must match.
            Otherwise, `search()` semantics are used.

        allow_none
            Whether None is accepted.

        strip
            Strip leading/trailing whitespace before matching.

        Returns
        -------
        str | None
            Normalized string.

        Raises
        ------
        MetricValidationError
            If validation fails.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            strip=strip,
        )

        if isinstance(
            pattern,
            str,
        ):
            regex = re.compile(
                pattern,
                flags,
            )

        elif isinstance(
            pattern,
            re.Pattern,
        ):
            regex = pattern

        else:

            raise InvalidMetricTypeError(
                "pattern must be a string or compiled regular expression."
            )

        if fullmatch:

            matched = regex.fullmatch(
                value,
            )

        else:

            matched = regex.search(
                value,
            )

        if matched is None:

            raise MetricValidationError(
                f"{field!r} does not match the required pattern."
            )

        return value
    @classmethod
    def validate_pattern(
        cls,
        value: Any,
        *,
        pattern: str | Pattern[str],
        field: str = "value",
        flags: re.RegexFlag | int = 0,
        fullmatch: bool = True,
        allow_none: bool = False,
        strip: bool = True,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> str | None:
        """
        Validate a string against a pattern.

        This is a higher-level wrapper around
        ``validate_regex()`` that additionally
        performs optional length validation.

        Parameters
        ----------
        value
            Value to validate.

        pattern
            Regular expression.

        field
            Field name.

        minimum
            Optional minimum length.

        maximum
            Optional maximum length.

        Returns
        -------
        str | None
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            minimum=minimum or 1,
            maximum=maximum,
            strip=strip,
        )

        value = cls.validate_regex(
            value,
            pattern=pattern,
            field=field,
            flags=flags,
            fullmatch=fullmatch,
            allow_none=False,
            strip=False,
        )

        return value

    @classmethod
    def validate_identifier_pattern(
        cls,
        value: Any,
        *,
        field: str = "identifier",
        maximum: int = MAX_NAME_LENGTH,
    ) -> str:
        """
        Validate a generic identifier pattern.

        Used by:

        - labels
        - attributes
        - metadata
        - namespaces
        - service names
        """

        return cls.validate_pattern(
            value,
            pattern=IDENTIFIER_PATTERN,
            field=field,
            maximum=maximum,
        )
    @classmethod
    def validate_prefix(
        cls,
        value: Any,
        *,
        prefixes: str | Sequence[str],
        field: str = "value",
        ignore_case: bool = False,
        allow_none: bool = False,
        strip: bool = True,
    ) -> str | None:
        """
        Validate that a string starts with one of the
        allowed prefixes.

        Parameters
        ----------
        value
            String to validate.

        prefixes
            Allowed prefix or collection of prefixes.

        ignore_case
            Perform case-insensitive comparison.

        Returns
        -------
        str | None
            Normalized value.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            strip=strip,
        )

        if isinstance(prefixes, str):

            prefixes = (prefixes,)

        else:

            prefixes = tuple(prefixes)

        if not prefixes:

            raise MetricValidationError(
                "No prefixes were provided."
            )

        if ignore_case:

            candidate = value.lower()

            valid = any(
                candidate.startswith(
                    prefix.lower(),
                )
                for prefix in prefixes
            )

        else:

            valid = any(
                value.startswith(prefix)
                for prefix in prefixes
            )

        if not valid:

            allowed = ", ".join(
                repr(p)
                for p in prefixes
            )

            raise MetricValidationError(
                f"{field} must start with one of: {allowed}."
            )

        return value

    @classmethod
    def validate_reserved(
        cls,
        value: Any,
        *,
        reserved: Collection[str],
        field: str = "value",
        ignore_case: bool = False,
        allow_none: bool = False,
        strip: bool = True,
    ) -> str | None:
        """
        Validate that a value is not reserved.

        Parameters
        ----------
        reserved
            Reserved identifiers.

        ignore_case
            Case-insensitive comparison.

        Returns
        -------
        str | None
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            strip=strip,
        )

        if ignore_case:

            reserved_set = {
                item.lower()
                for item in reserved
            }

            if value.lower() in reserved_set:

                raise MetricValidationError(
                    f"{field!r} is reserved."
                )

        else:

            if value in reserved:

                raise MetricValidationError(
                    f"{field!r} is reserved."
                )

        return value
    @classmethod
    def validate_suffix(
        cls,
        value: Any,
        *,
        suffixes: str | Sequence[str],
        field: str = "value",
        ignore_case: bool = False,
        allow_none: bool = False,
        strip: bool = True,
    ) -> str | None:
        """
        Validate that a string ends with one of the
        allowed suffixes.

        Examples
        --------
        .json
        .yaml
        .prom
        .bin
        .otel
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        value = cls.validate_non_empty_string(
            value,
            field=field,
            strip=strip,
        )

        if isinstance(
            suffixes,
            str,
        ):
            suffixes = (suffixes,)

        else:
            suffixes = tuple(suffixes)

        if not suffixes:

            raise MetricValidationError(
                "No suffixes were provided."
            )

        if ignore_case:

            candidate = value.lower()

            matched = any(
                candidate.endswith(
                    suffix.lower(),
                )
                for suffix in suffixes
            )

        else:

            matched = any(
                value.endswith(
                    suffix,
                )
                for suffix in suffixes
            )

        if not matched:

            raise MetricValidationError(
                f"{field} has an invalid suffix."
            )

        return value

    @classmethod
    def validate_identifier_pattern(
        cls,
        value: Any,
        *,
        field: str = "identifier",
        maximum: int = MAX_NAME_LENGTH,
    ) -> str:
        """
        Validate a generic identifier.

        Used by:

        • labels

        • attributes

        • metadata

        • runtime identifiers

        • service names
        """

        return cls.validate_pattern(
            value,
            pattern=IDENTIFIER_PATTERN,
            field=field,
            maximum=maximum,
        )

    @classmethod
    def validate_glob(
        cls,
        value: Any,
        *,
        field: str = "glob",
        allow_double_star: bool = True,
        allow_question: bool = True,
        allow_character_class: bool = True,
    ) -> str:
        """
        Validate a filesystem / namespace glob.

        Supported examples
        ------------------
        metrics.*
        runtime.**
        *.json
        logs/*.txt
        node[0-9]*
        """

        value = cls.validate_non_empty_string(
            value,
            field=field,
        )

        # Reject control characters.
        for ch in value:

            if ord(ch) < 32:

                raise MetricValidationError(
                    f"{field} contains control characters."
                )

        if not allow_double_star and "**" in value:

            raise MetricValidationError(
                f"{field} cannot contain '**'."
            )

        if not allow_question and "?" in value:

            raise MetricValidationError(
                f"{field} cannot contain '?'."
            )

        if (
            not allow_character_class
            and (
                "[" in value
                or "]" in value
            )
        ):

            raise MetricValidationError(
                f"{field} cannot contain character classes."
            )

        try:

            re.compile(
                fnmatch.translate(
                    value,
                )
            )

        except re.error as exc:

            raise MetricValidationError(
                f"Invalid glob pattern: {value!r}"
            ) from exc

        return value
    # ======================================================
    # 2F. Generic Helpers
    # ======================================================

    @classmethod
    def validate_type(
        cls,
        value: Any,
        expected_type: type | tuple[type, ...],
        *,
        field: str = "value",
        allow_none: bool = False,
    ) -> Any:
        """
        Validate exact object type.

        Parameters
        ----------
        expected_type
            Expected Python type.

        Notes
        -----
        This uses type() instead of isinstance()
        for strict validation.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if type(value) not in (
            expected_type
            if isinstance(
                expected_type,
                tuple,
            )
            else (
                expected_type,
            )
        ):

            raise InvalidMetricTypeError(
                f"{field} must be "
                f"{expected_type}, "
                f"got {type(value).__name__}."
            )

        return value


    @classmethod
    def validate_instance(
        cls,
        value: Any,
        expected_type: type | tuple[type, ...],
        *,
        field: str = "value",
        allow_none: bool = False,
    ) -> Any:
        """
        Validate isinstance() compatibility.

        Supports inheritance.
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if not isinstance(
            value,
            expected_type,
        ):

            raise InvalidMetricTypeError(
                f"{field} must be instance of "
                f"{expected_type}."
            )

        return value


    @classmethod
    def validate_callable(
        cls,
        value: Any,
        *,
        field: str = "callable",
        allow_none: bool = False,
    ) -> Callable[..., Any] | None:
        """
        Validate callable object.

        Used by:

        - Observable metrics
        - Hooks
        - Collectors
        - Exporters
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if not callable(value):

            raise InvalidMetricTypeError(
                f"{field} must be callable."
            )

        return value


    @classmethod
    def validate_enum(
        cls,
        value: Any,
        enum_type: type[Enum],
        *,
        field: str = "enum",
        allow_none: bool = False,
    ) -> Enum | None:
        """
        Validate Enum value.

        Accepts:

        - Enum instance
        - Enum value
        """

        if value is None:

            if allow_none:
                return None

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if isinstance(
            value,
            enum_type,
        ):

            return value


        try:

            return enum_type(
                value,
            )

        except (
            ValueError,
            TypeError,
        ):

            raise InvalidMetricTypeError(
                f"Invalid {field}: {value!r}"
            ) from None


    @classmethod
    def validate_not_none(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> Any:
        """
        Ensure value is not None.
        """

        if value is None:

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        return value


    @classmethod
    def validate_optional(
        cls,
        value: Any,
        validator: Callable[..., Any],
        *,
        field: str = "value",
        **kwargs: Any,
    ) -> Any:
        """
        Apply validator only when value
        is not None.

        Example
        -------
        validate_optional(
            version,
            validate_version
        )
        """

        if value is None:

            return None

        return validator(
            value,
            field=field,
            **kwargs,
        )
    # ======================================================
    # 2G. Final Polish
    # ======================================================

    @classmethod
    def normalize_string(
        cls,
        value: Any,
        *,
        field: str = "string",
        strip: bool = True,
        collapse_spaces: bool = True,
        lowercase: bool = False,
        maximum: int | None = None,
        allow_empty: bool = False,
    ) -> str:
        """
        Normalize a string value.

        Operations
        ----------
        - Convert to string
        - Strip whitespace
        - Collapse repeated spaces
        - Optional lowercase
        - Optional length limit
        """

        if value is None:

            raise MetricValidationError(
                f"{field} cannot be None."
            )

        if isinstance(
            value,
            bytes,
        ):

            value = value.decode(
                "utf-8",
                errors="replace",
            )

        elif not isinstance(
            value,
            str,
        ):

            value = str(value)


        if strip:

            value = value.strip()


        if collapse_spaces:

            value = re.sub(
                r"\s+",
                " ",
                value,
            )


        if lowercase:

            value = value.lower()


        if not allow_empty and not value:

            raise MetricValidationError(
                f"{field} cannot be empty."
            )


        if maximum is not None:

            if len(value) > maximum:

                raise MetricValidationError(
                    f"{field} exceeds maximum length "
                    f"{maximum}."
                )

        return value


    @classmethod
    def normalize_identifier(
        cls,
        value: Any,
        *,
        field: str = "identifier",
        lowercase: bool = True,
        replace_invalid: bool = True,
        separator: str = "_",
        maximum: int = MAX_NAME_LENGTH,
    ) -> str:
        """
        Normalize identifiers used by:

        - metric names
        - labels
        - attributes
        - namespaces
        - service names
        """

        value = cls.normalize_string(
            value,
            field=field,
            lowercase=lowercase,
            maximum=maximum,
        )


        if replace_invalid:

            value = re.sub(
                r"[^a-zA-Z0-9_]+",
                separator,
                value,
            )


            value = re.sub(
                r"_+",
                "_",
                value,
            )


            value = value.strip(
                separator,
            )


        if not value:

            raise MetricValidationError(
                f"{field} became empty after normalization."
            )


        return value


    @classmethod
    def sanitize_string(
        cls,
        value: Any,
        *,
        field: str = "string",
        remove_control: bool = True,
        maximum: int | None = None,
        replacement: str = "",
    ) -> str:
        """
        Remove unsafe characters.

        Used before:

        - logging
        - exporting
        - serialization
        """

        value = cls.normalize_string(
            value,
            field=field,
            maximum=maximum,
            allow_empty=True,
        )


        if remove_control:

            value = "".join(
                ch
                for ch in value
                if ord(ch) >= 32
            )


        if replacement:

            value = value.replace(
                "\n",
                replacement,
            )

            value = value.replace(
                "\r",
                replacement,
            )


        return value


    # ======================================================
    # Compatibility Helpers
    # ======================================================


    @classmethod
    def ensure_string(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> str:
        """
        Backward compatible string conversion.
        """

        return cls.normalize_string(
            value,
            field=field,
            allow_empty=True,
        )


    @classmethod
    def ensure_sequence(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> Sequence[Any]:
        """
        Convert compatible iterables into sequences.
        """

        if isinstance(
            value,
            Sequence,
        ):

            return value


        if isinstance(
            value,
            Iterable,
        ):

            return tuple(value)


        raise InvalidMetricTypeError(
            f"{field} cannot be converted to sequence."
        )


    @classmethod
    def ensure_mapping(
        cls,
        value: Any,
        *,
        field: str = "value",
    ) -> Mapping[Any, Any]:
        """
        Convert compatible mapping objects.
        """

        if isinstance(
            value,
            Mapping,
        ):

            return value


        raise InvalidMetricTypeError(
            f"{field} is not mapping compatible."
        )
    # ======================================================
    # Part 3. Label Validation
    # ======================================================


    @classmethod
    def validate_label_key(
        cls,
        value: Any,
        *,
        field: str = "label_key",
        maximum: int = MAX_NAME_LENGTH,
        normalize: bool = True,
    ) -> str:
        """
        Validate a metric label key.

        Rules
        -----
        - Must be a valid identifier.
        - Cannot contain spaces.
        - Cannot be reserved.
        - Must be stable for indexing.

        Examples
        --------
        valid:

            service
            instance_id
            gpu_device

        invalid:

            "service name"
            "123 key"
        """

        if normalize:

            value = cls.normalize_identifier(
                value,
                field=field,
                maximum=maximum,
            )

        else:

            value = cls.validate_identifier_pattern(
                value,
                field=field,
                maximum=maximum,
            )


        if value in RESERVED_NAMES:

            raise InvalidLabelError(
                f"{field} uses reserved name: {value}"
            )


        return value



    @classmethod
    def validate_label_value(
        cls,
        value: Any,
        *,
        field: str = "label_value",
        maximum: int = MAX_VALUE_LENGTH,
        allow_empty: bool = False,
    ) -> str:
        """
        Validate a metric label value.

        Label values are converted to strings
        because exporters generally require
        string representation.
        """

        if value is None:

            raise InvalidLabelError(
                f"{field} cannot be None."
            )


        value = cls.sanitize_string(
            value,
            field=field,
            maximum=maximum,
        )


        if not allow_empty and not value:

            raise InvalidLabelError(
                f"{field} cannot be empty."
            )


        return value



    @classmethod
    def validate_labels(
        cls,
        value: Any,
        *,
        field: str = "labels",
        maximum_labels: int = MAX_LABEL_COUNT,
        normalize_keys: bool = True,
        copy: bool = True,
    ) -> dict[str, str]:
        """
        Validate a collection of labels.

        Returns
        -------
        dict[str, str]

        Guarantees
        ----------
        - Valid keys
        - Valid values
        - No duplicated keys
        - Exporter-safe strings
        """

        if value is None:

            return {}


        value = cls.validate_mapping(
            value,
            field=field,
            maximum_size=maximum_labels,
        )


        result: dict[str, str] = {}


        for key, item in value.items():

            label_key = cls.validate_label_key(
                key,
                field=f"{field}.key",
                normalize=normalize_keys,
            )


            label_value = cls.validate_label_value(
                item,
                field=f"{field}.{label_key}",
            )


            if label_key in result:

                raise InvalidLabelError(
                    f"Duplicate label key: {label_key}"
                )


            result[label_key] = label_value


        if copy:

            return dict(result)


        return result
    # ======================================================
    # Part 4. Attribute Validation
    # ======================================================


    @classmethod
    def validate_attribute_key(
        cls,
        value: Any,
        *,
        field: str = "attribute_key",
        maximum: int = MAX_NAME_LENGTH,
        normalize: bool = True,
    ) -> str:
        """
        Validate an attribute key.

        Attribute keys follow the same stability
        requirements as labels.

        Rules
        -----
        - identifier format
        - no whitespace
        - no reserved names
        """

        if normalize:

            value = cls.normalize_identifier(
                value,
                field=field,
                maximum=maximum,
            )

        else:

            value = cls.validate_identifier_pattern(
                value,
                field=field,
                maximum=maximum,
            )


        if value in RESERVED_NAMES:

            raise InvalidAttributeError(
                f"{field} uses reserved name: {value}"
            )


        return value



    @classmethod
    def validate_attribute_value(
        cls,
        value: Any,
        *,
        field: str = "attribute_value",
        maximum_string_length: int = MAX_VALUE_LENGTH,
        maximum_sequence_length: int = MAX_ATTRIBUTE_LENGTH,
        allow_none: bool = False,
    ) -> Any:
        """
        Validate OpenTelemetry compatible attribute value.

        Supported types
        ---------------

        Primitive:

        - str
        - bool
        - int
        - float

        Arrays:

        - list
        - tuple

        """

        if value is None:

            if allow_none:

                return None

            raise InvalidAttributeError(
                f"{field} cannot be None."
            )


        # ------------------------------
        # Boolean
        # ------------------------------

        if isinstance(
            value,
            bool,
        ):

            return value



        # ------------------------------
        # Integer
        # ------------------------------

        if isinstance(
            value,
            int,
        ):

            return value



        # ------------------------------
        # Float
        # ------------------------------

        if isinstance(
            value,
            float,
        ):

            return cls.validate_finite(
                value,
                field=field,
            )



        # ------------------------------
        # String
        # ------------------------------

        if isinstance(
            value,
            str,
        ):

            return cls.sanitize_string(
                value,
                field=field,
                maximum=maximum_string_length,
            )



        # ------------------------------
        # Sequence
        # ------------------------------

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):

            if len(value) > maximum_sequence_length:

                raise InvalidAttributeError(
                    f"{field} sequence exceeds maximum size."
                )


            result = []

            for item in value:

                result.append(
                    cls.validate_attribute_value(
                        item,
                        field=f"{field}[]",
                        maximum_string_length=maximum_string_length,
                        maximum_sequence_length=maximum_sequence_length,
                    )
                )


            return tuple(result)



        raise InvalidAttributeError(
            f"Unsupported attribute type: "
            f"{type(value).__name__}"
        )



    @classmethod
    def validate_attributes(
        cls,
        value: Any,
        *,
        field: str = "attributes",
        maximum_attributes: int = MAX_ATTRIBUTE_COUNT,
        normalize_keys: bool = True,
        copy: bool = True,
    ) -> dict[str, Any]:
        """
        Validate attribute mapping.

        Guarantees
        ----------
        - valid keys
        - valid values
        - deterministic output
        - exporter safe
        """

        if value is None:

            return {}


        value = cls.validate_mapping(
            value,
            field=field,
            maximum_size=maximum_attributes,
        )


        result: dict[str, Any] = {}


        for key, item in value.items():


            attribute_key = cls.validate_attribute_key(
                key,
                field=f"{field}.key",
                normalize=normalize_keys,
            )


            attribute_value = cls.validate_attribute_value(
                item,
                field=f"{field}.{attribute_key}",
            )


            if attribute_key in result:

                raise InvalidAttributeError(
                    f"Duplicate attribute key: {attribute_key}"
                )


            result[attribute_key] = attribute_value



        if copy:

            return dict(result)


        return result
    # ======================================================
    # Part 5. Metadata Validation
    # ======================================================


    @classmethod
    def validate_metadata(
        cls,
        value: Any,
        *,
        field: str = "metadata",
        maximum_entries: int = MAX_METADATA_COUNT,
        normalize_keys: bool = True,
        copy: bool = True,
    ) -> dict[str, Any]:
        """
        Validate metric metadata.

        Metadata represents descriptive
        information about a metric object.

        Examples
        --------
        {
            "owner": "SciOS",
            "component": "scheduler",
            "version": "1.0.0",
            "domain": "physics"
        }
        """

        if value is None:

            return {}


        value = cls.validate_mapping(
            value,
            field=field,
            maximum_size=maximum_entries,
        )


        result: dict[str, Any] = {}


        for key, item in value.items():


            metadata_key = (
                cls.normalize_identifier(
                    key,
                    field=f"{field}.key",
                )
                if normalize_keys
                else
                cls.validate_identifier_pattern(
                    key,
                    field=f"{field}.key",
                )
            )


            if metadata_key in RESERVED_NAMES:

                raise InvalidMetadataError(
                    f"Reserved metadata key: {metadata_key}"
                )


            metadata_value = cls.validate_metadata_value(
                item,
                field=f"{field}.{metadata_key}",
            )


            result[metadata_key] = metadata_value



        return dict(result) if copy else result



    @classmethod
    def validate_metadata_value(
        cls,
        value: Any,
        *,
        field: str = "metadata_value",
    ) -> Any:
        """
        Validate metadata values.

        Metadata supports richer values than labels
        but must remain serialization safe.
        """

        if value is None:

            return None


        if isinstance(
            value,
            (
                str,
                bool,
                int,
            ),
        ):

            return value



        if isinstance(
            value,
            float,
        ):

            return cls.validate_finite(
                value,
                field=field,
            )



        if isinstance(
            value,
            Mapping,
        ):

            return cls.validate_metadata(
                value,
                field=field,
            )



        if isinstance(
            value,
            Sequence,
        ) and not isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):

            return tuple(
                cls.validate_metadata_value(
                    item,
                    field=f"{field}[]",
                )
                for item in value
            )


        raise InvalidMetadataError(
            f"Unsupported metadata type: "
            f"{type(value).__name__}"
        )



    @classmethod
    def validate_tags(
        cls,
        value: Any,
        *,
        field: str = "tags",
        maximum_tags: int = MAX_TAG_COUNT,
        normalize: bool = True,
    ) -> tuple[str, ...]:
        """
        Validate metadata tags.

        Tags are lightweight string identifiers.

        Example
        -------
        (
            "production",
            "gpu",
            "distributed"
        )
        """

        if value is None:

            return ()


        value = cls.validate_sequence(
            value,
            field=field,
            maximum_size=maximum_tags,
        )


        result = []


        for tag in value:


            if normalize:

                tag = cls.normalize_identifier(
                    tag,
                    field=f"{field}.tag",
                )

            else:

                tag = cls.validate_identifier_pattern(
                    tag,
                    field=f"{field}.tag",
                )


            if tag in result:

                continue


            result.append(tag)



        return tuple(result)



    @classmethod
    def validate_annotations(
        cls,
        value: Any,
        *,
        field: str = "annotations",
        maximum_annotations: int = MAX_ANNOTATION_COUNT,
    ) -> dict[str, str]:
        """
        Validate annotations.

        Annotations are human-readable metadata
        attached to runtime objects.

        Example
        -------
        {
            "created_by": "kernel",
            "purpose": "benchmark"
        }
        """

        if value is None:

            return {}


        value = cls.validate_mapping(
            value,
            field=field,
            maximum_size=maximum_annotations,
        )


        result: dict[str, str] = {}


        for key, item in value.items():


            key = cls.normalize_identifier(
                key,
                field=f"{field}.key",
            )


            item = cls.sanitize_string(
                item,
                field=f"{field}.{key}",
                maximum=MAX_VALUE_LENGTH,
            )


            result[key] = item



        return result
    # ======================================================
    # Part 6. Descriptor Validation
    # ======================================================


    @classmethod
    def validate_metric_type(
        cls,
        value: Any,
        *,
        field: str = "metric_type",
        allow_none: bool = False,
    ) -> str | None:
        """
        Validate metric instrument type.

        Supported metric types:

        - counter
        - up_down_counter
        - gauge
        - histogram
        - summary
        - timer
        - observable_counter
        - observable_gauge
        """

        if value is None:

            if allow_none:
                return None

            raise InvalidMetricTypeError(
                f"{field} cannot be None."
            )


        value = cls.normalize_identifier(
            value,
            field=field,
        )


        allowed = {

            "counter",

            "up_down_counter",

            "gauge",

            "histogram",

            "summary",

            "timer",

            "observable_counter",

            "observable_gauge",

        }


        if value not in allowed:

            raise InvalidMetricTypeError(
                f"Unsupported metric type: {value}"
            )


        return value



    @classmethod
    def validate_value_type(
        cls,
        value: Any,
        *,
        metric_type: str | None = None,
        field: str = "value_type",
    ) -> str:
        """
        Validate metric value data type.

        Supported:

        - int
        - float
        - number
        - histogram
        - summary
        """

        if value is None:

            raise InvalidMetricTypeError(
                f"{field} cannot be None."
            )


        value = cls.normalize_identifier(
            value,
            field=field,
        )


        allowed = {

            "int",

            "integer",

            "float",

            "double",

            "number",

            "histogram",

            "summary",

        }


        if value not in allowed:

            raise InvalidMetricTypeError(
                f"Unsupported value type: {value}"
            )


        # semantic checks

        if metric_type == "counter":

            if value not in {
                "int",
                "integer",
                "number",
            }:

                raise InvalidMetricTypeError(
                    "Counter requires numeric value."
                )


        if metric_type == "histogram":

            if value not in {
                "float",
                "double",
                "number",
            }:

                raise InvalidMetricTypeError(
                    "Histogram requires numeric observations."
                )


        return value



    @classmethod
    def validate_descriptor(
        cls,
        value: Any,
        *,
        field: str = "descriptor",
        copy: bool = True,
    ) -> dict[str, Any]:
        """
        Validate a complete metric descriptor.

        Expected schema
        ----------------

        {
            name,
            type,
            unit,
            description,
            value_type,
            labels,
            attributes,
            metadata
        }

        """

        if value is None:

            raise InvalidMetadataError(
                "Descriptor cannot be None."
            )


        value = cls.validate_mapping(
            value,
            field=field,
        )


        result: dict[str, Any] = {}


        # ------------------------------
        # Name
        # ------------------------------

        if "name" not in value:

            raise InvalidMetricNameError(
                "Descriptor requires name."
            )


        result["name"] = (
            cls.validate_name(
                value["name"],
            )
        )


        # ------------------------------
        # Type
        # ------------------------------

        metric_type = (
            cls.validate_metric_type(
                value.get(
                    "type"
                )
            )
        )

        result["type"] = metric_type


        # ------------------------------
        # Value type
        # ------------------------------

        if "value_type" in value:

            result["value_type"] = (
                cls.validate_value_type(
                    value["value_type"],
                    metric_type=metric_type,
                )
            )


        # ------------------------------
        # Optional fields
        # ------------------------------

        if "unit" in value:

            result["unit"] = (
                cls.validate_unit(
                    value["unit"]
                )
            )


        if "description" in value:

            result["description"] = (
                cls.validate_description(
                    value["description"]
                )
            )


        if "labels" in value:

            result["labels"] = (
                cls.validate_labels(
                    value["labels"]
                )
            )


        if "attributes" in value:

            result["attributes"] = (
                cls.validate_attributes(
                    value["attributes"]
                )
            )


        if "metadata" in value:

            result["metadata"] = (
                cls.validate_metadata(
                    value["metadata"]
                )
            )


        return dict(result) if copy else result



    @classmethod
    def compatibility(
        cls,
        descriptor: Mapping[str, Any],
        *,
        target: str,
        field: str = "descriptor",
    ) -> bool:
        """
        Check descriptor compatibility with
        a backend/exporter.

        Examples:

        prometheus
        otlp
        csv
        json
        """

        target = cls.normalize_identifier(
            target,
            field="target",
        )


        metric_type = (
            descriptor.get(
                "type"
            )
        )


        if target == "prometheus":

            unsupported = {

                "summary",

            }


            if metric_type in unsupported:

                return False



        if target == "otlp":

            return True



        if target == "csv":

            return True



        raise MetricValidationError(
            f"Unknown compatibility target: {target}"
        )
    # ======================================================
    # Part 7. Runtime Validation
    # ======================================================


    @classmethod
    def validate_counter(
        cls,
        value: Any,
        *,
        field: str = "counter",
        allow_zero: bool = True,
    ) -> int:
        """
        Validate counter runtime value.

        Counter rules
        --------------
        - integer only
        - monotonically increasing
        - non-negative
        """

        value = cls.validate_integer(
            value,
            field=field,
        )


        if value < 0:

            raise MetricValidationError(
                f"{field} cannot be negative."
            )


        if not allow_zero and value == 0:

            raise MetricValidationError(
                f"{field} cannot be zero."
            )


        return value



    @classmethod
    def validate_gauge(
        cls,
        value: Any,
        *,
        field: str = "gauge",
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> float:
        """
        Validate gauge value.

        Gauge rules
        -----------
        - numeric
        - finite
        - can increase/decrease
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )


        value = float(value)


        cls.validate_finite(
            value,
            field=field,
        )


        if minimum is not None:

            if value < minimum:

                raise MetricValidationError(
                    f"{field} below minimum."
                )


        if maximum is not None:

            if value > maximum:

                raise MetricValidationError(
                    f"{field} exceeds maximum."
                )


        return value



    @classmethod
    def validate_histogram(
        cls,
        value: Any,
        *,
        field: str = "histogram",
    ) -> float:
        """
        Validate histogram observation.

        Histogram receives
        individual samples.
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )


        value = float(value)


        cls.validate_finite(
            value,
            field=field,
        )


        return value



    @classmethod
    def validate_summary(
        cls,
        value: Any,
        *,
        field: str = "summary",
    ) -> float:
        """
        Validate summary observation.

        Summary metrics store
        statistical samples.
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )


        value = float(value)


        cls.validate_finite(
            value,
            field=field,
        )


        return value



    @classmethod
    def validate_timer(
        cls,
        value: Any,
        *,
        field: str = "timer",
        unit: str = "seconds",
    ) -> float:
        """
        Validate timer duration.

        Timer rules
        -----------
        - finite number
        - non-negative duration
        """

        value = cls.validate_numeric(
            value,
            field=field,
        )


        value = float(value)


        cls.validate_finite(
            value,
            field=field,
        )


        if value < 0:

            raise MetricValidationError(
                f"{field} duration cannot be negative."
            )


        return value
    # ======================================================
    # Part 8. Batch Validation
    # ======================================================


    @classmethod
    def validate_metrics(
        cls,
        value: Any,
        *,
        field: str = "metrics",
        maximum: int = MAX_METRIC_COUNT,
        copy: bool = True,
    ) -> list[Any]:
        """
        Validate a collection of metric objects.

        Supported input:

        - list
        - tuple
        - mapping values

        Guarantees:

        - collection type safety
        - no None metrics
        - deterministic output
        """

        if value is None:

            raise MetricValidationError(
                f"{field} cannot be None."
            )


        if isinstance(
            value,
            Mapping,
        ):

            value = list(
                value.values()
            )


        value = cls.validate_sequence(
            value,
            field=field,
            maximum_size=maximum,
        )


        result = []


        for index, metric in enumerate(value):

            if metric is None:

                raise MetricValidationError(
                    f"{field}[{index}] cannot be None."
                )


            # Object-level validation.
            #
            # Metric classes may implement
            # validate() in future versions.

            validator = getattr(
                metric,
                "validate",
                None,
            )

            if callable(
                validator
            ):

                validator()


            result.append(
                metric
            )


        return list(result) if copy else result



    @classmethod
    def validate_registry(
        cls,
        value: Any,
        *,
        field: str = "registry",
        maximum: int = MAX_METRIC_COUNT,
    ) -> dict[str, Any]:
        """
        Validate metric registry.

        Expected format:

        {
            "cpu_usage": Metric,
            "memory_usage": Metric
        }

        Rules:

        - key must be valid metric identifier
        - metric object cannot be None
        - duplicate names rejected
        """

        value = cls.validate_mapping(
            value,
            field=field,
            maximum_size=maximum,
        )


        result: dict[str, Any] = {}


        for name, metric in value.items():


            metric_name = cls.validate_identifier_pattern(
                name,
                field=f"{field}.name",
            )


            if metric_name in result:

                raise MetricAlreadyExistsError(
                    f"Duplicate metric: {metric_name}"
                )


            if metric is None:

                raise MetricValidationError(
                    f"Metric {metric_name} is None."
                )


            validator = getattr(
                metric,
                "validate",
                None,
            )

            if callable(
                validator
            ):

                validator()


            result[metric_name] = metric


        return result



    @classmethod
    def validate_snapshot(
        cls,
        value: Any,
        *,
        field: str = "snapshot",
        require_timestamp: bool = True,
        require_version: bool = True,
    ) -> dict[str, Any]:
        """
        Validate metric snapshot.

        Expected:

        {
            "timestamp": float,
            "version": int,
            "metrics": [...]
        }

        Used by:

        - persistence
        - restore
        - replication
        """

        value = cls.validate_mapping(
            value,
            field=field,
        )


        result: dict[str, Any] = {}



        # ------------------------------
        # Timestamp
        # ------------------------------

        timestamp = value.get(
            "timestamp"
        )


        if require_timestamp:

            if timestamp is None:

                raise MetricSnapshotError(
                    "Snapshot timestamp missing."
                )


            result["timestamp"] = (
                cls.validate_numeric(
                    timestamp,
                    field=f"{field}.timestamp",
                )
            )



        # ------------------------------
        # Version
        # ------------------------------

        version = value.get(
            "version"
        )


        if require_version:

            if version is None:

                raise MetricSnapshotError(
                    "Snapshot version missing."
                )


            result["version"] = (
                cls.validate_integer(
                    version,
                    field=f"{field}.version",
                )
            )



        # ------------------------------
        # Metrics
        # ------------------------------

        if "metrics" in value:

            result["metrics"] = (
                cls.validate_metrics(
                    value["metrics"],
                    field=f"{field}.metrics",
                )
            )



        # ------------------------------
        # Metadata
        # ------------------------------

        if "metadata" in value:

            result["metadata"] = (
                cls.validate_metadata(
                    value["metadata"],
                    field=f"{field}.metadata",
                )
            )


        return result
    # ======================================================
    # Part 9. Diagnostics
    # ======================================================


    @classmethod
    def warnings(
        cls,
        value: Any,
        *,
        field: str = "object",
    ) -> list[dict[str, Any]]:
        """
        Generate non-blocking warnings.

        Returns
        -------
        list[dict]

        Example
        -------
        [
            {
                "level": "warning",
                "field": "name",
                "message": "...",
            }
        ]
        """

        warnings: list[dict[str, Any]] = []


        if value is None:

            warnings.append(
                {
                    "level": "warning",
                    "field": field,
                    "message": "Value is None.",
                }
            )

            return warnings


        if isinstance(
            value,
            Mapping,
        ):


            # Empty metadata

            if not value:

                warnings.append(
                    {
                        "level": "info",
                        "field": field,
                        "message":
                            "Object contains no fields.",
                    }
                )


            # Detect suspicious keys

            for key in value.keys():

                if isinstance(
                    key,
                    str,
                ):

                    if key != key.strip():

                        warnings.append(
                            {
                                "level": "warning",
                                "field":
                                    f"{field}.{key}",
                                "message":
                                    "Key contains whitespace.",
                            }
                        )



        return warnings



    @classmethod
    def diagnostics(
        cls,
        value: Any,
        *,
        field: str = "object",
    ) -> dict[str, Any]:
        """
        Produce full diagnostic report.

        Output:

        {
            warnings: [],
            errors: [],
            statistics: {}
        }
        """

        report = {

            "field": field,

            "valid": True,

            "warnings": [],

            "errors": [],

            "statistics": {},

        }


        report["warnings"] = (
            cls.warnings(
                value,
                field=field,
            )
        )


        if value is None:

            report["valid"] = False

            report["errors"].append(
                {
                    "message":
                        "Object is None."
                }
            )


        if isinstance(
            value,
            Mapping,
        ):

            report["statistics"] = {

                "keys":
                    len(value),

                "type":
                    type(value).__name__,

            }


        return report



    @classmethod
    def repair_suggestions(
        cls,
        value: Any,
        *,
        field: str = "object",
    ) -> list[str]:
        """
        Generate automatic repair suggestions.

        Used by:

        - CLI tools
        - dashboards
        - self-healing agents
        """

        suggestions: list[str] = []


        if value is None:

            suggestions.append(
                "Provide a valid object."
            )

            return suggestions



        if isinstance(
            value,
            Mapping,
        ):


            for key in value.keys():

                if isinstance(
                    key,
                    str,
                ):


                    if key != key.strip():

                        suggestions.append(
                            f"Trim whitespace from key '{key}'."
                        )


                    if " " in key:

                        suggestions.append(
                            f"Normalize key '{key}' "
                            "to identifier format."
                        )



        return suggestions



    @classmethod
    def lint(
        cls,
        value: Any,
        *,
        field: str = "object",
        strict: bool = False,
    ) -> dict[str, Any]:
        """
        Run complete validation lint.

        Unlike validate_* methods,
        lint never raises immediately.

        Returns
        -------
        Diagnostic report
        """

        report = cls.diagnostics(
            value,
            field=field,
        )


        report["suggestions"] = (
            cls.repair_suggestions(
                value,
                field=field,
            )
        )


        if strict:

            report["valid"] = (
                report["valid"]
                and
                len(
                    report["warnings"]
                )
                == 0
            )


        return report
    # ======================================================
    # Part 10. Production Utilities
    # ======================================================


    @classmethod
    def normalize(
        cls,
        value: Any,
        *,
        field: str = "value",
        recursive: bool = True,
    ) -> Any:
        """
        Normalize arbitrary validation input.

        Operations:

        - normalize strings
        - normalize identifiers
        - normalize mappings
        - normalize sequences
        """

        if value is None:

            return None


        if isinstance(
            value,
            str,
        ):

            return cls.normalize_string(
                value,
                field=field,
            )


        if isinstance(
            value,
            Mapping,
        ) and recursive:


            return {
                cls.normalize_identifier(
                    key,
                    field=f"{field}.key",
                ):
                    cls.normalize(
                        item,
                        field=f"{field}.{key}",
                        recursive=True,
                    )

                for key, item in value.items()
            }



        if isinstance(
            value,
            Sequence,
        ) and not isinstance(
            value,
            (
                str,
                bytes,
            ),
        ) and recursive:


            return [

                cls.normalize(
                    item,
                    field=f"{field}[]",
                    recursive=True,
                )

                for item in value

            ]


        return value



    @classmethod
    def sanitize(
        cls,
        value: Any,
        *,
        field: str = "value",
        remove_sensitive: bool = True,
    ) -> Any:
        """
        Sanitize data before:

        - logging
        - exporting
        - serialization
        """

        sensitive_keys = {

            "password",

            "secret",

            "token",

            "api_key",

            "private_key",

        }


        if isinstance(
            value,
            Mapping,
        ):

            result = {}


            for key, item in value.items():

                normalized_key = str(key).lower()


                if (
                    remove_sensitive
                    and
                    normalized_key in sensitive_keys
                ):

                    result[key] = "***REDACTED***"

                else:

                    result[key] = cls.sanitize(
                        item,
                        field=f"{field}.{key}",
                        remove_sensitive=remove_sensitive,
                    )


            return result



        if isinstance(
            value,
            str,
        ):

            return cls.sanitize_string(
                value,
                field=field,
            )


        if isinstance(
            Sequence,
        ):

            return [

                cls.sanitize(
                    item,
                    field=f"{field}[]",
                )

                for item in value

            ]


        return value



    @classmethod
    def infer_defaults(
        cls,
        value: Mapping[str, Any],
        *,
        metric_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Infer missing descriptor defaults.

        Used by:

        - MetricDescriptor
        - Registry
        - Import compatibility
        """

        result = dict(value)


        if "type" not in result:

            result["type"] = (
                metric_type
                or
                "gauge"
            )


        if "value_type" not in result:

            defaults = {

                "counter": "integer",

                "up_down_counter": "integer",

                "gauge": "double",

                "histogram": "double",

                "summary": "double",

                "timer": "double",

            }


            result["value_type"] = (
                defaults.get(
                    result["type"],
                    "double",
                )
            )



        if "labels" not in result:

            result["labels"] = {}


        if "attributes" not in result:

            result["attributes"] = {}


        if "metadata" not in result:

            result["metadata"] = {}


        return result



    @classmethod
    def strict(
        cls,
        enabled: bool = True,
    ) -> dict[str, bool]:
        """
        Configure strict validation mode.

        Strict mode:

        - reject warnings
        - reject implicit conversion
        - reject unknown fields
        """

        return {

            "strict": enabled,

            "allow_conversion":
                not enabled,

            "allow_unknown":
                not enabled,

        }



    @classmethod
    def compatibility_mode(
        cls,
        version: str = "legacy",
    ) -> dict[str, str]:
        """
        Compatibility policy.

        Supported:

        - legacy
        - stable
        - strict
        """

        allowed = {

            "legacy",

            "stable",

            "strict",

        }


        if version not in allowed:

            raise MetricValidationError(
                f"Unknown compatibility mode: {version}"
            )


        return {

            "mode": version,

        }



    @classmethod
    def finalize(
        cls,
        value: Any,
        *,
        field: str = "object",
        strict: bool = False,
        sanitize: bool = True,
        normalize: bool = True,
    ) -> Any:
        """
        Final validation pipeline.

        Pipeline:

        input
          |
          v
        normalize
          |
          v
        sanitize
          |
          v
        lint
          |
          v
        output
        """

        result = value


        if normalize:

            result = cls.normalize(
                result,
                field=field,
            )


        if sanitize:

            result = cls.sanitize(
                result,
                field=field,
            )


        report = cls.lint(
            result,
            field=field,
            strict=strict,
        )


        if strict and not report["valid"]:

            raise MetricValidationError(
                f"Validation failed: {report}"
            )


        return result                                                                                                                                                                                             