# ==============================================================================
# SciOS Runtime Observability
# Jaeger Exporter
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json
import time

from typing import (
    Any,
    Iterable,
    Mapping,
    Optional,
)

from .exporter import (
    ExportError,
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Part 2. Public API
# ==============================================================================


class JaegerExportError(
    ExportError,
):
    """
    Raised when Jaeger export fails.
    """

    pass


# ==============================================================================
# Part 3. JaegerExporter
# ==============================================================================


class JaegerExporter(
    Exporter,
):
    """
    Jaeger-compatible trace exporter.

    The exporter prepares trace/span payloads for Jaeger transport.
    Network transport is intentionally outside this class.
    """

    def __init__(
        self,
        name: str = "jaeger",
        endpoint: str = "http://localhost:14268/api/traces",
        service_name: str = "scios",
        encoding: str = "utf-8",
        enabled: bool = True,
        options: Optional[
            Mapping[
                str,
                Any,
            ]
        ] = None,
    ) -> None:
        """
        Initialize a Jaeger exporter.
        """

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._name = name
        self._endpoint = endpoint
        self._service_name = service_name
        self._encoding = encoding
        self._enabled = enabled

        # Jaeger exporter produces JSON payloads.
        self._format = ExportFormat.JSON

        # Preserve user-supplied options exactly.
        self._options = (
            dict(options)
            if options is not None
            else {}
        )

        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------

        self._state = "created"

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._export_count = 0
        self._success_count = 0
        self._error_count = 0
        self._bytes_exported = 0

        self._last_export: Optional[
            float
        ] = None

        self._last_error: Optional[
            Exception
        ] = None

        # ------------------------------------------------------------------
        # Initial validation
        # ------------------------------------------------------------------

        self.validate_endpoint()
        self.validate_options(
            self._options,
        )


# ==============================================================================
# Part 4. Core Properties
# ==============================================================================


    @property
    def endpoint(
        self,
    ) -> str:
        """
        Return the Jaeger endpoint.
        """

        return self._endpoint


    @property
    def service_name(
        self,
    ) -> str:
        """
        Return the configured service name.
        """

        return self._service_name


    @property
    def encoding(
        self,
    ) -> str:
        """
        Return the configured encoding.
        """

        return self._encoding


    @property
    def options(
        self,
    ) -> dict[str, Any]:
        """
        Return Jaeger exporter options.
        """

        return self._options


# ==============================================================================
# Part 5. Jaeger Serialization
# ==============================================================================


    def serialize(
        self,
        payload: ExportPayload,
    ) -> str:
        """
        Serialize a payload into Jaeger-compatible JSON text.

        The serializer always returns ``str``.
        """

        if not self.validate_payload(
            payload,
        ):
            error = JaegerExportError(
                "invalid Jaeger export payload",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            # ------------------------------------------------------------------
            # Bytes -> decode first
            # ------------------------------------------------------------------

            if isinstance(
                payload,
                bytes,
            ):
                payload = payload.decode(
                    self._encoding,
                )

            # ------------------------------------------------------------------
            # JSON serialization
            # ------------------------------------------------------------------

            return json.dumps(
                payload,
                ensure_ascii=False,
                indent=None,
            )

        except JaegerExportError:
            raise

        except Exception as exc:

            error = JaegerExportError(
                f"failed to serialize Jaeger payload: {exc}",
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc


    def serialize_span(
        self,
        span: Mapping[str, Any],
    ) -> str:
        """
        Serialize one Jaeger span.

        The input mapping is serialized as-is. The exporter does not
        mutate the span or inject ``service_name`` into the payload.
        """

        if not isinstance(
            span,
            Mapping,
        ):
            error = JaegerExportError(
                "invalid Jaeger span payload",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            return json.dumps(
                dict(span),
                ensure_ascii=False,
                indent=None,
            )

        except Exception as exc:

            error = JaegerExportError(
                f"failed to serialize Jaeger span: {exc}",
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc


    def serialize_many(
        self,
        payloads: Iterable[
            ExportPayload
        ],
    ) -> list[str]:
        """
        Serialize multiple Jaeger payloads.

        Each payload is serialized independently through ``serialize()``.
        """

        if payloads is None:
            error = JaegerExportError(
                "payloads must not be None",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            return [
                self.serialize(
                    payload,
                )
                for payload in payloads
            ]

        except JaegerExportError:
            raise

        except Exception as exc:

            error = JaegerExportError(
                f"failed to serialize Jaeger payloads: {exc}",
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc


# ==============================================================================
# Part 6. Export API
# ==============================================================================


    def export(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload through the Jaeger exporter contract.

        No network request is performed here.
        """

        # ------------------------------------------------------------------
        # Export attempt
        # ------------------------------------------------------------------

        self._export_count += 1

        # ------------------------------------------------------------------
        # Lifecycle guards
        # ------------------------------------------------------------------

        if self._state == "closed":

            error = JaegerExportError(
                "Jaeger exporter is closed",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        if not self._enabled:

            error = JaegerExportError(
                "Jaeger exporter is disabled",
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
            # Validate endpoint
            # --------------------------------------------------------------

            self.validate_endpoint()

            # --------------------------------------------------------------
            # Validate payload
            # --------------------------------------------------------------

            if not self.validate_payload(
                payload,
            ):
                raise JaegerExportError(
                    "invalid Jaeger payload",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Validate options
            # --------------------------------------------------------------

            if not self.validate_options(
                options,
            ):
                raise JaegerExportError(
                    "invalid Jaeger export options",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Ensure exporter is running
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

            byte_count = len(
                serialized.encode(
                    self._encoding,
                ),
            )

            # --------------------------------------------------------------
            # Statistics
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
                payload=serialized,
                format=self._format,
                bytes_exported=byte_count,
                metadata={
                    "endpoint": self._endpoint,
                    "service_name": self._service_name,
                    "encoding": self._encoding,
                    "transport": "jaeger",
                },
            )

        except JaegerExportError as exc:

            self._record_error(
                exc,
            )

            raise

        except ExportError as exc:

            error = JaegerExportError(
                str(exc),
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc

        except Exception as exc:

            error = JaegerExportError(
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
        """
        Export multiple Jaeger payloads.
        """

        return [
            self.export(
                payload,
                **options,
            )
            for payload in payloads
        ]


# ==============================================================================
# Part 7. Validation
# ==============================================================================


    def validate_payload(
        self,
        payload: ExportPayload,
    ) -> bool:
        """
        Validate a Jaeger export payload.
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
        Validate Jaeger exporter options.
        """

        if options is None:
            options = {}

        if not isinstance(
            options,
            Mapping,
        ):
            return False

        for key in options:
            if not isinstance(
                key,
                str,
            ):
                return False

        return True


    def validate_endpoint(
        self,
        endpoint: Optional[str] = None,
    ) -> bool:
        """
        Validate a Jaeger endpoint.

        When ``endpoint`` is omitted, the configured endpoint
        is validated.
        """

        target = (
            self._endpoint
            if endpoint is None
            else endpoint
        )

        if not isinstance(
            target,
            str,
        ):
            raise JaegerExportError(
                "invalid Jaeger endpoint",
                exporter=self._name,
            )

        target = target.strip()

        if not target:
            raise JaegerExportError(
                "invalid Jaeger endpoint",
                exporter=self._name,
            )

        if not (
            target.startswith("http://")
            or target.startswith("https://")
        ):
            raise JaegerExportError(
                "Jaeger endpoint must use http or https",
                exporter=self._name,
            )

        return True


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "JaegerExporter":
        """
        Start the Jaeger exporter.
        """

        if self._state == "closed":
            raise JaegerExportError(
                "cannot start a closed Jaeger exporter",
                exporter=self._name,
            )

        self.validate_endpoint()

        self._state = "running"

        return self


    def stop(
        self,
    ) -> "JaegerExporter":
        """
        Stop the Jaeger exporter.
        """

        if self._state == "closed":
            return self

        self._state = "stopped"

        return self


    def reset(
        self,
    ) -> "JaegerExporter":
        """
        Reset Jaeger exporter runtime state and statistics.
        """

        if self._state == "closed":
            raise JaegerExportError(
                "cannot reset a closed Jaeger exporter",
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
    ) -> "JaegerExporter":
        """
        Permanently close the Jaeger exporter.
        """

        if self._state == "closed":
            return self

        self._state = "closed"

        return self


# ==============================================================================
# Part 9. Error Handling
# ==============================================================================


    def _handle_error(
        self,
        error: JaegerExportError,
    ) -> ExportResult:
        """
        Convert a Jaeger exporter error into an ExportResult.
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
            metadata={
                "endpoint": self._endpoint,
                "service_name": self._service_name,
                "transport": "jaeger",
            },
        )


    def _record_error(
        self,
        error: JaegerExportError,
    ) -> None:
        """
        Record a Jaeger exporter error.
        """

        self._error_count += 1
        self._last_error = error


# ==============================================================================
# Part 10. Statistics
# ==============================================================================


    @property
    def export_count(
        self,
    ) -> int:
        """
        Return total export attempts.
        """

        return self._export_count


    @property
    def success_count(
        self,
    ) -> int:
        """
        Return successful export count.
        """

        return self._success_count


    @property
    def error_count(
        self,
    ) -> int:
        """
        Return failed export count.
        """

        return self._error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """
        Return total exported bytes.
        """

        return self._bytes_exported


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


    def health(
        self,
    ) -> bool:
        """
        Return Jaeger exporter health status.
        """

        return (
            self._state != "closed"
            and self._state != "failed"
            and self._enabled
            and bool(self._endpoint.strip())
        )


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed Jaeger exporter diagnostics.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "service_name": self._service_name,
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
        Return a compact Jaeger exporter summary.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "service_name": self._service_name,
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
        """
        Return developer-oriented representation.
        """

        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"endpoint={self._endpoint!r}, "
            f"service_name={self._service_name!r}, "
            f"encoding={self._encoding!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        """
        Return human-readable representation.
        """

        return (
            f"{self._name}("
            f"endpoint={self._endpoint}, "
            f"service_name={self._service_name}, "
            f"state={self._state}, "
            f"enabled={self._enabled}"
            f")"
        )


# ==============================================================================
# Part 13. End
# ==============================================================================


__all__ = [
    "JaegerExporter",
    "JaegerExportError",
]
