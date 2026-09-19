# ==============================================================================
# SciOS Runtime Observability
# Exporter
# ==============================================================================

from __future__ import annotations

import codecs
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, TypeAlias


# ==============================================================================
# Part 1. Exceptions
# ==============================================================================


class ExportError(RuntimeError):
    """
    Base exception for exporter failures.
    """

    def __init__(
        self,
        message: str,
        *,
        exporter: str | None = None,
        cause: Exception | None = None,
    ) -> None:

        super().__init__(
            message,
        )

        self.exporter = exporter
        self.cause = cause


# ==============================================================================
# Part 2. Exporter Types
# ==============================================================================


class ExportFormat(
    str,
    Enum,
):
    """
    Supported exporter formats.
    """

    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"


ExportPayload: TypeAlias = (
    Mapping[str, Any]
    | list[Any]
    | tuple[Any, ...]
    | str
    | bytes
    | int
    | float
    | bool
    | None
)


@dataclass(
    slots=True,
)
class ExportResult:
    """
    Result returned by an exporter operation.
    """

    success: bool = False

    payload: ExportPayload = None

    format: ExportFormat = (
        ExportFormat.JSON
    )

    bytes_exported: int = 0

    error: Optional[Exception] = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ==============================================================================
# Part 3. Exporter Configuration
# ==============================================================================

# Configuration is represented directly by the Exporter constructor.
#
# Public configuration:
#
#     name
#     format
#     encoding
#     enabled
#     options


# ==============================================================================
# Part 4. Exporter
# ==============================================================================


class Exporter:
    """
    Base exporter for SciOS runtime observability data.

    Provides configuration, lifecycle state, export statistics,
    and a stable foundation for concrete exporters.
    """

    def __init__(
        self,
        name: str = "exporter",
        *,
        format: ExportFormat = ExportFormat.JSON,
        encoding: str = "utf-8",
        enabled: bool = True,
        options: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Validate name
        # ------------------------------------------------------------------

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "name must be a string",
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "name must not be empty",
            )

        # ------------------------------------------------------------------
        # Validate format
        # ------------------------------------------------------------------

        if isinstance(
            format,
            str,
        ):
            try:
                format = ExportFormat(
                    format.strip().lower(),
                )
            except ValueError as exc:
                raise ValueError(
                    f"unsupported export format: {format!r}",
                ) from exc

        elif not isinstance(
            format,
            ExportFormat,
        ):
            raise TypeError(
                "format must be an ExportFormat",
            )

        # ------------------------------------------------------------------
        # Validate encoding
        # ------------------------------------------------------------------

        if not isinstance(
            encoding,
            str,
        ):
            raise TypeError(
                "encoding must be a string",
            )

        encoding = encoding.strip()

        if not encoding:
            raise ValueError(
                "encoding must not be empty",
            )

        try:
            codecs.lookup(
                encoding,
            )
        except LookupError as exc:
            raise ValueError(
                f"unsupported encoding: {encoding!r}",
            ) from exc

        # ------------------------------------------------------------------
        # Validate enabled
        # ------------------------------------------------------------------

        if not isinstance(
            enabled,
            bool,
        ):
            raise TypeError(
                "enabled must be a bool",
            )

        # ------------------------------------------------------------------
        # Validate options
        # ------------------------------------------------------------------

        if options is None:

            normalized_options: dict[
                str,
                Any,
            ] = {
                "indent": 2,
                "ensure_ascii": False,
            }

        else:

            if not isinstance(
                options,
                Mapping,
            ):
                raise TypeError(
                    "options must be a mapping",
                )

            normalized_options = {
                "indent": 2,
                "ensure_ascii": False,
                **dict(options),
            }

        # ------------------------------------------------------------------
        # Configuration state
        # ------------------------------------------------------------------

        self._name = name
        self._format = format
        self._encoding = encoding
        self._enabled = enabled
        self._options = normalized_options

        # ------------------------------------------------------------------
        # Lifecycle state
        # ------------------------------------------------------------------

        self._state = "created"

        # ------------------------------------------------------------------
        # Export statistics
        # ------------------------------------------------------------------

        self._export_count: int = 0
        self._success_count: int = 0
        self._error_count: int = 0
        self._bytes_exported: int = 0

        # ------------------------------------------------------------------
        # Last operation state
        # ------------------------------------------------------------------

        self._last_export: float | None = None
        self._last_error: ExportError | None = None

    # ----------------------------------------------------------------------
    # Core properties
    # ----------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        return self._name

    @property
    def format(
        self,
    ) -> ExportFormat:
        return self._format

    @property
    def encoding(
        self,
    ) -> str:
        return self._encoding

    @property
    def enabled(
        self,
    ) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "enabled must be a bool",
            )

        self._enabled = value

    @property
    def state(
        self,
    ) -> str:
        return self._state

    @property
    def options(
        self,
    ) -> dict[str, Any]:
        return self._options

    # ----------------------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------------------

    @property
    def export_count(
        self,
    ) -> int:
        return self._export_count

    @property
    def success_count(
        self,
    ) -> int:
        return self._success_count

    @property
    def error_count(
        self,
    ) -> int:
        return self._error_count

    @property
    def bytes_exported(
        self,
    ) -> int:
        return self._bytes_exported

    @property
    def last_export(
        self,
    ) -> float | None:
        return self._last_export

    @property
    def last_error(
        self,
    ) -> ExportError | None:
        return self._last_error



# ==============================================================================
# Part 5. Core Properties
# ==============================================================================


    @property
    def name(
        self,
    ) -> str:
        """Return the exporter name."""

        return self._name


    @property
    def format(
        self,
    ) -> ExportFormat:
        """Return the configured export format."""

        return self._format


    @property
    def encoding(
        self,
    ) -> str:
        """Return the configured text encoding."""

        return self._encoding


    @property
    def enabled(
        self,
    ) -> bool:
        """Return whether the exporter is enabled."""

        return self._enabled


    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        """Enable or disable the exporter."""

        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "enabled must be a bool",
            )

        self._enabled = value


    @property
    def options(
        self,
    ) -> dict[str, Any]:
        """
        Return exporter configuration options.

        The internal mapping is intentionally exposed so concrete
        exporters can update exporter-specific configuration.
        """

        return self._options


    @property
    def state(
        self,
    ) -> str:
        """Return the current exporter lifecycle state."""

        return self._state


# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "Exporter":
        """Start the exporter."""

        if self._state == "closed":
            raise ExportError(
                "cannot start a closed exporter",
                exporter=self._name,
            )

        self._state = "running"

        return self


    def stop(
        self,
    ) -> "Exporter":
        """Stop the exporter."""

        if self._state == "closed":
            return self

        self._state = "stopped"

        return self


    def reset(
        self,
    ) -> "Exporter":
        """
        Reset runtime state and export statistics.

        Configuration is preserved.
        """

        if self._state == "closed":
            raise ExportError(
                "cannot reset a closed exporter",
                exporter=self._name,
            )

        self._export_count = 0
        self._success_count = 0
        self._error_count = 0
        self._bytes_exported = 0

        self._last_export = None
        self._last_error = None

        self._state = "created"

        return self


    def close(
        self,
    ) -> "Exporter":
        """Close the exporter permanently."""

        if self._state == "closed":
            return self

        self._state = "closed"

        return self


# ==============================================================================
# Part 7. Export API
# ==============================================================================


    def export(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload.

        Every invocation counts as one export attempt.
        Failed attempts increment error_count.
        """

        # ------------------------------------------------------------------
        # Count export attempt
        # ------------------------------------------------------------------

        self._export_count += 1

        # ------------------------------------------------------------------
        # Lifecycle guards
        # ------------------------------------------------------------------

        if self._state == "closed":
            error = ExportError(
                "exporter is closed",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        if not self._enabled:
            error = ExportError(
                "exporter is disabled",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            # --------------------------------------------------------------
            # Validate configuration
            # --------------------------------------------------------------

            self.validate()

            # --------------------------------------------------------------
            # Validate payload
            # --------------------------------------------------------------

            if not self.validate_payload(
                payload,
            ):
                raise ExportError(
                    "invalid export payload",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Validate call options
            # --------------------------------------------------------------

            if not self.validate_options(
                options,
            ):
                raise ExportError(
                    "invalid export options",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Ensure running
            # --------------------------------------------------------------

            if self._state in {
                "created",
                "stopped",
            }:
                self.start()

            # --------------------------------------------------------------
            # Serialize
            # --------------------------------------------------------------

            serialized = self.serialize(
                payload,
            )

            # --------------------------------------------------------------
            # Calculate byte size
            # --------------------------------------------------------------

            if isinstance(
                serialized,
                bytes,
            ):
                exported = serialized
                byte_count = len(
                    serialized,
                )

            else:
                exported = serialized
                byte_count = len(
                    serialized.encode(
                        self._encoding,
                    ),
                )

            # --------------------------------------------------------------
            # Success statistics
            # --------------------------------------------------------------

            self._success_count += 1
            self._bytes_exported += byte_count
            self._last_export = time.time()
            self._last_error = None

            # --------------------------------------------------------------
            # Result
            # --------------------------------------------------------------

            return ExportResult(
                success=True,
                payload=exported,
                format=self._format,
                bytes_exported=byte_count,
            )

        except ExportError as exc:

            self._record_error(
                exc,
            )

            raise

        except Exception as exc:

            error = ExportError(
                str(exc),
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc


    def export_many(
        self,
        payloads: Iterable[
            ExportPayload
        ],
        **options: Any,
    ) -> list[ExportResult]:
        """Export multiple payloads."""

        return [
            self.export(
                payload,
                **options,
            )
            for payload in payloads
        ]


    def serialize(
        self,
        payload: ExportPayload,
    ) -> str | bytes:
        """
        Serialize a payload according to the configured format.
        """

        if not self.validate_payload(
            payload,
        ):
            raise ExportError(
                "invalid export payload",
                exporter=self._name,
            )

        # ------------------------------------------------------------------
        # BYTES
        # ------------------------------------------------------------------

        if self._format is ExportFormat.BYTES:

            if isinstance(
                payload,
                bytes,
            ):
                return payload

            if isinstance(
                payload,
                str,
            ):
                return payload.encode(
                    self._encoding,
                )

            return json.dumps(
                payload,
                default=str,
                **self._json_options(),
            ).encode(
                self._encoding,
            )

        # ------------------------------------------------------------------
        # TEXT
        # ------------------------------------------------------------------

        if self._format is ExportFormat.TEXT:

            if isinstance(
                payload,
                str,
            ):
                return payload

            if isinstance(
                payload,
                bytes,
            ):
                return payload.decode(
                    self._encoding,
                )

            return json.dumps(
                payload,
                default=str,
                **self._json_options(),
            )

        # ------------------------------------------------------------------
        # JSON
        # ------------------------------------------------------------------

        return json.dumps(
            payload,
            default=str,
            **self._json_options(),
        )


    def _json_options(
        self,
    ) -> dict[str, Any]:
        """
        Return JSON serialization options.

        Only options accepted by json.dumps() are forwarded.
        """

        allowed = {
            "indent",
            "ensure_ascii",
            "sort_keys",
            "separators",
            "allow_nan",
            "check_circular",
            "skipkeys",
        }

        return {
            key: value
            for key, value in self._options.items()
            if key in allowed
        }


    def flush(
        self,
    ) -> "Exporter":
        """
        Flush pending exporter state.

        Base exporter has no external buffer, so this is a
        lifecycle-compatible no-op.
        """

        if self._state == "closed":
            raise ExportError(
                "cannot flush a closed exporter",
                exporter=self._name,
            )

        return self


# ==============================================================================
# Part 8. Validation
# ==============================================================================


    def validate(
        self,
    ) -> bool:
        """
        Validate exporter configuration.

        Raises ExportError when the current configuration is invalid.
        """

        if (
            not isinstance(
                self._name,
                str,
            )
            or not self._name.strip()
        ):
            raise ExportError(
                "invalid exporter name",
                exporter=self._name,
            )

        if not isinstance(
            self._format,
            ExportFormat,
        ):
            raise ExportError(
                "invalid exporter format",
                exporter=self._name,
            )

        if (
            not isinstance(
                self._encoding,
                str,
            )
            or not self._encoding.strip()
        ):
            raise ExportError(
                "invalid exporter encoding",
                exporter=self._name,
            )

        try:
            codecs.lookup(
                self._encoding,
            )
        except LookupError as exc:
            raise ExportError(
                "invalid exporter encoding",
                exporter=self._name,
                cause=exc,
            ) from exc

        if not isinstance(
            self._enabled,
            bool,
        ):
            raise ExportError(
                "invalid exporter enabled state",
                exporter=self._name,
            )

        if not self.validate_options(
            self._options,
        ):
            raise ExportError(
                "invalid exporter options",
                exporter=self._name,
            )

        return True


    def validate_payload(
        self,
        payload: ExportPayload,
    ) -> bool:
        """
        Validate an export payload.

        Returns False for unsupported payload types rather than
        raising directly.
        """

        if payload is None:
            return True

        return isinstance(
            payload,
            (
                Mapping,
                list,
                tuple,
                str,
                bytes,
                int,
                float,
                bool,
            ),
        )


    def validate_options(
        self,
        options: Optional[
            Mapping[
                str,
                Any,
            ]
        ] = None,
    ) -> bool:
        """
        Validate exporter options.

        Option keys must be strings.
        """

        if options is None:
            return True

        if not isinstance(
            options,
            Mapping,
        ):
            return False

        return all(
            isinstance(
                key,
                str,
            )
            for key in options
        )


# ==============================================================================
# Part 9. Error Handling
# ==============================================================================


    def _handle_error(
        self,
        error: ExportError,
    ) -> ExportResult:
        """
        Record an exporter error and return a failed result.

        This helper is retained for lifecycle APIs that use result-based
        error handling.
        """

        self._record_error(
            error,
        )

        return ExportResult(
            success=False,
            payload=None,
            format=self._format,
            bytes_exported=0,
            error=error,
        )


    def _record_error(
        self,
        error: ExportError,
    ) -> None:
        """
        Record one exporter failure.

        This is the single authority responsible for updating
        error statistics.
        """

        if not isinstance(
            error,
            ExportError,
        ):
            error = ExportError(
                str(error),
                exporter=self._name,
                cause=error,
            )

        self._error_count += 1
        self._last_error = error


# ==============================================================================
# Part 10. Statistics
# ==============================================================================


    @property
    def export_count(
        self,
    ) -> int:
        """Return total number of export attempts."""

        return self._export_count


    @property
    def success_count(
        self,
    ) -> int:
        """Return total number of successful exports."""

        return self._success_count


    @property
    def error_count(
        self,
    ) -> int:
        """Return total number of failed exports."""

        return self._error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """Return total number of exported bytes."""

        return self._bytes_exported


    @property
    def last_export(
        self,
    ) -> Optional[float]:
        """Return the timestamp of the last successful export."""

        return self._last_export


    @property
    def last_error(
        self,
    ) -> Optional[ExportError]:
        """Return the most recent exporter error."""

        return self._last_error


# ==============================================================================
# Part 11. State / Diagnostics
# ==============================================================================


    def health(
        self,
    ) -> bool:
        """
        Return whether the exporter is currently healthy.
        """

        return (
            self._enabled
            and self._state
            not in {
                "closed",
                "failed",
            }
        )


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed exporter diagnostics.
        """

        return {
            "name": self._name,
            "format": self._format.value,
            "encoding": self._encoding,
            "enabled": self._enabled,
            "state": self._state,
            "healthy": self.health(),
            "export_count": self._export_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "bytes_exported": self._bytes_exported,
            "last_export": self._last_export,
            "last_error": (
                str(self._last_error)
                if self._last_error is not None
                else None
            ),
        }


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a compact exporter summary.
        """

        return {
            "name": self._name,
            "format": self._format.value,
            "state": self._state,
            "enabled": self._enabled,
            "healthy": self.health(),
            "export_count": self._export_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "bytes_exported": self._bytes_exported,
        }


# ==============================================================================
# Part 12. Representation
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"format={self._format.value!r}, "
            f"encoding={self._encoding!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        return (
            f"{self._name}("
            f"format={self._format.value}, "
            f"state={self._state}, "
            f"enabled={self._enabled}"
            f")"
        )

# ==============================================================================
# Compatibility API
# ==============================================================================

TraceExporter = Exporter
