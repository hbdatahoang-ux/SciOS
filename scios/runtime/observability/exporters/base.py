"""
SciOS Runtime Observability
===========================

Generic Exporter Base
---------------------

This module defines the stable exporter contract shared by the
SciOS observability stack.

Architecture
------------

    ExportError
        |
    ExportFormat
        |
    ExportPayload
        |
    ExportResult
        |
    Exporter
        |
        +-- MemoryExporter
        +-- StdoutExporter
        +-- JSONExporter
        +-- PrometheusExporter
        +-- OpenTelemetryExporter
        +-- JaegerExporter
        +-- ZipkinExporter

The base exporter is intentionally independent from metrics, tracing,
logging, OpenTelemetry, and concrete transport implementations.

Python 3.11+
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Optional, TypeAlias


# ==============================================================================
# Part 1. Imports
# ==============================================================================

ExportData: TypeAlias = Mapping[str, Any]
ExportOptions: TypeAlias = Mapping[str, Any]


# ==============================================================================
# Part 2. Exceptions
# ==============================================================================


class ExportError(RuntimeError):
    """
    Base exception for exporter failures.

    ExportError represents an error occurring during export,
    serialization, validation, or exporter lifecycle operations.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.cause = cause


# ==============================================================================
# Part 3. Export Format
# ==============================================================================


class ExportFormat(str, Enum):
    """
    Supported generic export formats.

    Concrete exporters may support only a subset of these formats.
    """

    JSON = "json"
    TEXT = "text"
    BINARY = "binary"
    PROMETHEUS = "prometheus"
    OTLP = "otlp"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"

    def __str__(self) -> str:
        return self.value


# ==============================================================================
# Part 4. Export Payload
# ==============================================================================


@dataclass(slots=True)
class ExportPayload:
    """
    Generic payload passed to an exporter.

    Parameters
    ----------
    name:
        Logical name of the exported item.

    value:
        Payload value. This may be a scalar, mapping, sequence,
        or another JSON-compatible/object value.

    labels:
        Optional labels associated with the payload.

    timestamp:
        Export/event timestamp. If omitted, the current Unix time
        is assigned.

    metadata:
        Optional additional metadata.

    options:
        Per-payload export options.
    """

    name: str
    value: Any
    labels: dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("payload name must be a string")

        self.name = self.name.strip()

        if not self.name:
            raise ValueError("payload name must not be empty")

        if self.timestamp is None:
            self.timestamp = time.time()

        if not isinstance(self.labels, dict):
            self.labels = dict(self.labels)

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        if not isinstance(self.options, dict):
            self.options = dict(self.options)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable mapping representation.
        """

        return {
            "name": self.name,
            "value": self.value,
            "labels": dict(self.labels),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
            "options": dict(self.options),
        }


# ==============================================================================
# Part 5. Export Result
# ==============================================================================


@dataclass(slots=True)
class ExportResult:
    """
    Result returned by an exporter operation.

    A result describes the outcome of one export attempt without
    coupling the caller to a concrete exporter implementation.
    """

    success: bool
    exporter: str
    count: int = 1
    bytes_exported: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    data: Any = None
    timestamp: float = field(default_factory=time.time)

    @property
    def failed(self) -> bool:
        """Return True when the export failed."""

        return not self.success

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation.
        """

        return {
            "success": self.success,
            "exporter": self.exporter,
            "count": self.count,
            "bytes_exported": self.bytes_exported,
            "duration": self.duration,
            "error": self.error,
            "data": self.data,
            "timestamp": self.timestamp,
        }


# ==============================================================================
# Part 6. Exporter
# ==============================================================================


class Exporter:
    """
    Generic base exporter for SciOS observability.

    The class owns:

    - configuration
    - lifecycle
    - payload validation
    - serialization
    - export statistics
    - error tracking
    - diagnostics

    Concrete exporters should override :meth:`_export`.

    Examples
    --------
    A minimal exporter implementation::

        class MemoryExporter(Exporter):

            def _export(self, payload, *, options):
                self.items.append(payload)
                return payload

    Notes
    -----
    ``export()`` accepts per-call options. These options override
    exporter defaults for that operation only and never mutate
    ``self.options``.
    """

    # ==========================================================================
    # Part 6.1. Constructor
    # ==========================================================================

    def __init__(
        self,
        name: str,
        format: ExportFormat = ExportFormat.JSON,
        *,
        encoding: str = "utf-8",
        enabled: bool = True,
        options: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self._name = name
        self._format = format
        self._encoding = encoding
        self._enabled = enabled
        self._options = dict(options or {})

        self._started = False
        self._closed = False

        # ------------------------------------------------------------------
        # Export lifecycle statistics.
        #
        # These counters are owned exclusively by the base Exporter.
        # Subclasses must NOT initialize or increment them independently.
        # ------------------------------------------------------------------

        self._export_count: int = 0
        self._success_count: int = 0
        self._error_count: int = 0
        self._bytes_exported: int = 0

        self._last_export: Optional[float] = None
        self._last_error: Optional[str] = None

        self.validate()

    # ==========================================================================
    # Part 6.2. Configuration Properties
    # ==========================================================================

    @property
    def name(self) -> str:
        """Return exporter name."""

        return self._name

    @property
    def format(self) -> ExportFormat:
        """Return configured export format."""

        return self._format

    @property
    def encoding(self) -> str:
        """Return configured text encoding."""

        return self._encoding

    @property
    def enabled(self) -> bool:
        """Return whether the exporter is enabled."""

        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("enabled must be a bool")

        self._enabled = value

    @property
    def options(self) -> dict[str, Any]:
        """
        Return a copy of exporter options.

        The internal configuration is never exposed directly.
        """

        return dict(self._options)

    @property
    def started(self) -> bool:
        """Return True when the exporter is running."""

        return self._started

    @property
    def closed(self) -> bool:
        """Return True when the exporter has been closed."""

        return self._closed

    @property
    def state(self) -> str:
        """
        Return the current lifecycle state.

        Possible values:

        - ``closed``
        - ``started``
        - ``stopped``
        """

        if self._closed:
            return "closed"

        if self._started:
            return "started"

        return "stopped"

    # ==========================================================================
    # Part 6.3. Statistics Properties
    # ==========================================================================

    @property
    def export_count(self) -> int:
        return self._export_count


    @property
    def success_count(self) -> int:
        return self._success_count


    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def bytes_exported(self) -> int:
        """Return total exported byte count."""

        return self._bytes_exported

    @property
    def last_export(self) -> Optional[float]:
        """Return timestamp of the last export attempt."""

        return self._last_export

    @property
    def last_error(self) -> Optional[str]:
        """Return the last exporter error."""

        return self._last_error

    # ==========================================================================
    # Part 6.4. Lifecycle
    # ==========================================================================

    def start(self) -> "Exporter":
        """
        Start the exporter.

        Calling start repeatedly is idempotent.
        """

        if self._closed:
            raise RuntimeError("cannot start a closed exporter")

        if self._started:
            return self

        self._started = True
        return self

    def stop(self) -> "Exporter":
        """
        Stop the exporter.

        Stopping an already stopped exporter is idempotent.
        """

        if self._closed:
            return self

        if not self._started:
            return self

        self._started = False
        return self

    def reset(self) -> "Exporter":
        """
        Reset runtime statistics and error state.

        Configuration is preserved.
        """

        if self._closed:
            raise RuntimeError("cannot reset a closed exporter")

        self._export_count = 0
        self._success_count = 0
        self._error_count = 0
        self._bytes_exported: int = 0

        self._last_export = None
        self._last_error = None

        return self

    def close(self) -> "Exporter":
        """
        Permanently close the exporter.

        Close is idempotent.
        """

        if self._closed:
            return self

        self._started = False
        self._closed = True

        return self

    # ==========================================================================
    # Part 6.5. Export API
    # ==========================================================================

    def export(
        self,
        payload: ExportPayload | Mapping[str, Any],
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload.

        Per-call options override exporter-level options without
        mutating the exporter configuration.
        """

        started_at = time.perf_counter()
        self._export_count += 1
        self._last_export = time.time()

        try:
            if self._closed:
                raise ExportError(
                    f"exporter '{self.name}' is closed"
                )

            if not self.enabled:
                return ExportResult(
                    success=False,
                    exporter=self.name,
                    count=0,
                    duration=time.perf_counter() - started_at,
                    error="exporter is disabled",
                )

            self.validate_payload(payload)
            self.validate_options(options)

            normalized_payload = self._normalize_payload(payload)

            effective_options = {
                **self._options,
                **normalized_payload.options,
                **options,
            }

            serialized = self.serialize(
                normalized_payload,
                options=effective_options,
            )

            result_data = self._export(
                normalized_payload,
                serialized=serialized,
                options=effective_options,
            )

            byte_count = self._calculate_bytes(serialized)

            self._success_count += 1
            self._bytes_exported += byte_count
            self._last_error = None

            return ExportResult(
                success=True,
                exporter=self.name,
                count=1,
                bytes_exported=byte_count,
                duration=time.perf_counter() - started_at,
                data=result_data,
            )

        except Exception as exc:
            return self._handle_error(
                exc,
                duration=time.perf_counter() - started_at,
            )

    def export_many(
        self,
        payloads: Iterable[
            ExportPayload | Mapping[str, Any]
        ],
        **options: Any,
    ) -> list[ExportResult]:
        """
        Export multiple payloads.

        Each payload is processed independently so one failure does
        not prevent subsequent payloads from being attempted.
        """

        return [
            self.export(payload, **options)
            for payload in payloads
        ]

    def serialize(
        self,
        payload: ExportPayload | Mapping[str, Any],
        *,
        options: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """
        Serialize a payload according to the configured format.

        Concrete exporters may override this method when they require
        a format-specific representation.
        """

        normalized = self._normalize_payload(payload)
        effective_options = dict(options or {})

        if self.format == ExportFormat.JSON:
            return json.dumps(
                normalized.to_dict(),
                ensure_ascii=effective_options.get(
                    "ensure_ascii",
                    False,
                ),
                default=effective_options.get(
                    "default",
                    str,
                ),
                separators=effective_options.get(
                    "separators",
                    (",", ":"),
                ),
            )

        if self.format == ExportFormat.TEXT:
            return str(normalized.to_dict())

        if self.format == ExportFormat.BINARY:
            return json.dumps(
                normalized.to_dict(),
                ensure_ascii=False,
                default=str,
            ).encode(self.encoding)

        return normalized.to_dict()

    def flush(self) -> "Exporter":
        """
        Flush pending exporter output.

        Base implementation is intentionally a no-op.
        Concrete exporters may override it.
        """

        if self._closed:
            raise RuntimeError("cannot flush a closed exporter")

        return self

    # ==========================================================================
    # Part 6.6. Concrete Export Hook
    # ==========================================================================

    def _export(
        self,
        payload: ExportPayload,
        *,
        serialized: Any,
        options: Mapping[str, Any],
    ) -> Any:
        """
        Backend-specific export hook.

        Concrete exporters should override this method.

        The base implementation simply returns the serialized payload,
        which makes the base class useful for contract testing.
        """

        return serialized

    # ==========================================================================
    # Part 6.7. Validation
    # ==========================================================================

    def validate(self) -> None:
        """
        Validate exporter configuration.
        """

        if not isinstance(self._name, str):
            raise TypeError("name must be a string")

        self._name = self._name.strip()

        if not self._name:
            raise ValueError("name must not be empty")

        if not isinstance(self._format, ExportFormat):
            try:
                self._format = ExportFormat(self._format)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"unsupported export format: {self._format!r}"
                ) from exc

        if not isinstance(self._encoding, str):
            raise TypeError("encoding must be a string")

        try:
            "".encode(self._encoding)
        except LookupError as exc:
            raise ValueError(
                f"unknown encoding: {self._encoding!r}"
            ) from exc

        if not isinstance(self._enabled, bool):
            raise TypeError("enabled must be a bool")

        self.validate_options(self._options)

    def validate_payload(
        self,
        payload: ExportPayload | Mapping[str, Any],
    ) -> None:
        """
        Validate an export payload.
        """

        if isinstance(payload, ExportPayload):
            return

        if not isinstance(payload, Mapping):
            raise TypeError(
                "payload must be ExportPayload or a mapping"
            )

        if "name" not in payload:
            raise ValueError(
                "payload mapping must contain 'name'"
            )

    def validate_options(
        self,
        options: Mapping[str, Any],
    ) -> None:
        """
        Validate export options.

        Base implementation only verifies that options are mappings
        with string keys. Concrete exporters may impose additional
        constraints.
        """

        if not isinstance(options, Mapping):
            raise TypeError("options must be a mapping")

        for key in options:
            if not isinstance(key, str):
                raise TypeError(
                    "export option keys must be strings"
                )

    # ==========================================================================
    # Part 6.8. Error Handling
    # ==========================================================================

    def _handle_error(
        self,
        error: Exception,
        *,
        duration: float = 0.0,
        payload: ExportPayload | Mapping[str, Any] | None = None,
    ) -> ExportResult:
        """
        Handle an export failure.
        """
        self._record_error(error)

        return ExportResult(
            success=False,
            exporter=self.name,
            count=0,
            duration=duration,
            error=str(error),
        )


    def _record_error(self, error: BaseException) -> None:
        """
        Record an exporter error.
        """

        self._error_count += 1
        self._last_error = str(error)

    # ==========================================================================
    # Part 6.9. Diagnostics
    # ==========================================================================

    def health(self) -> dict[str, Any]:
        """
        Return a lightweight health snapshot.
        """

        return {
            "name": self.name,
            "state": self.state,
            "enabled": self.enabled,
            "healthy": (
                not self.closed
                and self._last_error is None
            ),
        }

    def diagnostics(self) -> dict[str, Any]:
        """
        Return detailed exporter diagnostics.
        """

        return {
            "name": self.name,
            "format": self.format.value,
            "encoding": self.encoding,
            "enabled": self.enabled,
            "state": self.state,
            "started": self.started,
            "closed": self.closed,
            "statistics": {
                "export_count": self.export_count,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "bytes_exported": self.bytes_exported,
                "last_export": self.last_export,
                "last_error": self.last_error,
            },
            "options": self.options,
        }

    def summary(self) -> dict[str, Any]:
        """
        Return a compact exporter summary.
        """

        return {
            "name": self.name,
            "format": self.format.value,
            "state": self.state,
            "enabled": self.enabled,
            "export_count": self.export_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "bytes_exported": self.bytes_exported,
        }

    # ==========================================================================
    # Part 6.10. Representation
    # ==========================================================================

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"format={self.format.value!r}, "
            f"enabled={self.enabled!r}, "
            f"state={self.state!r}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"(name={self.name!r}, "
            f"format={self.format.value!r}, "
            f"state={self.state!r})"
        )

    # ==========================================================================
    # Part 6.11. Internal Helpers
    # ==========================================================================

    @staticmethod
    def _normalize_payload(
        payload: ExportPayload | Mapping[str, Any],
    ) -> ExportPayload:
        """
        Normalize a mapping into ExportPayload.
        """

        if isinstance(payload, ExportPayload):
            return payload

        return ExportPayload(
            name=str(payload["name"]),
            value=payload.get("value"),
            labels=dict(payload.get("labels", {})),
            timestamp=payload.get("timestamp"),
            metadata=dict(payload.get("metadata", {})),
            options=dict(payload.get("options", {})),
        )

    def _calculate_bytes(self, data: Any) -> int:
        """
        Calculate the serialized byte size.
        """

        if data is None:
            return 0

        if isinstance(data, bytes):
            return len(data)

        if isinstance(data, str):
            return len(data.encode(self.encoding))

        try:
            encoded = json.dumps(
                data,
                ensure_ascii=False,
                default=str,
            ).encode(self.encoding)
        except (TypeError, UnicodeError):
            return 0

        return len(encoded)

    # ==================================================================
    # Internal statistics helpers
    # ==================================================================

    def _record_success(
        self,
        payload: ExportPayload | Mapping[str, Any],
    ) -> ExportResult:
        """
        Build a successful export result.

        Counter updates are owned by export().
        """
        return ExportResult(
            success=True,
            exporter=self.name,
            payload=payload,
        )

# ==============================================================================
# Part 7. Public API
# ==============================================================================

# ------------------------------------------------------------------------------
# Backward Compatibility
# ------------------------------------------------------------------------------

BaseExporter = Exporter


# ------------------------------------------------------------------------------
# Legacy Compatibility API
# ------------------------------------------------------------------------------

class ExportStatus(str, Enum):
    """
    Legacy exporter status.

    Kept for backward compatibility with the pre-v0.1 exporter API.
    """

    SUCCESS = "success"
    ERROR = "error"
    FAILED = "failed"
    DISABLED = "disabled"
    PENDING = "pending"


class ExportCapability(str, Enum):
    """
    Legacy exporter capability flags.

    Kept for backward compatibility with concrete exporters.
    """

    SERIALIZATION = "serialization"
    BATCHING = "batching"
    STREAMING = "streaming"


class ExportMode(str, Enum):
    """
    Legacy exporter operating mode.

    Kept for backward compatibility with concrete exporters.
    """

    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"
    STREAM = "stream"


@dataclass
class ExportRecord:
    """
    Legacy export record compatibility object.
    """

    name: str
    value: Any = None
    labels: dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "labels": dict(self.labels),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
            "options": dict(self.options),
        }


# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------

__all__ = [
    # Current API
    "ExportData",
    "ExportError",
    "ExportFormat",
    "ExportOptions",
    "ExportPayload",
    "ExportResult",
    "Exporter",

    # Legacy compatibility API
    "BaseExporter",
    "ExportRecord",
    "ExportStatus",
    "ExportCapability",
    "ExportMode",
]