# ==============================================================================
# SciOS Runtime Observability
# Zipkin Exporter
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


class ZipkinExportError(
    ExportError,
):
    """
    Raised when Zipkin export fails.
    """

    pass


# ==============================================================================
# Part 3. ZipkinExporter
# ==============================================================================


class ZipkinExporter(
    Exporter,
):
    """
    Zipkin-compatible trace exporter.

    The exporter prepares trace/span payloads for Zipkin transport.
    Network transport is intentionally outside this class.
    """

    def __init__(
        self,
        name: str = "zipkin",
        endpoint: str = "http://localhost:9411/api/v2/spans",
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
        Initialize a Zipkin exporter.
        """

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._name = name
        self._endpoint = endpoint
        self._service_name = service_name
        self._encoding = encoding
        self._enabled = enabled

        # Zipkin exporter produces JSON payloads.
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
        Return the configured Zipkin endpoint.
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
        Return the configured text encoding.
        """

        return self._encoding


    @property
    def options(
        self,
    ) -> dict[str, Any]:
        """
        Return a copy of exporter options.
        """

        return dict(
            self._options,
        )


# ==============================================================================
# Part 5. Zipkin Serialization
# ==============================================================================


    def serialize(
        self,
        payload: ExportPayload,
    ) -> str:
        """
        Serialize a payload into Zipkin-compatible JSON text.

        The serializer always returns ``str``.
        """

        # ------------------------------------------------------------------
        # Validate payload
        # ------------------------------------------------------------------

        if not self.validate_payload(
            payload,
        ):
            error = ZipkinExportError(
                "invalid Zipkin export payload",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            # ------------------------------------------------------------------
            # Bytes -> decode to text
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

        except Exception as exc:

            error = ZipkinExportError(
                f"failed to serialize Zipkin payload: {exc}",
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
        Serialize one Zipkin span.

        The input span is serialized without mutation or
        automatic injection of exporter configuration.
        """

        # ------------------------------------------------------------------
        # Validate span
        # ------------------------------------------------------------------

        if not isinstance(
            span,
            Mapping,
        ):
            error = ZipkinExportError(
                "invalid Zipkin span payload",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        try:

            # ------------------------------------------------------------------
            # Serialize span
            # ------------------------------------------------------------------

            return json.dumps(
                dict(span),
                ensure_ascii=False,
                indent=None,
            )

        except Exception as exc:

            error = ZipkinExportError(
                f"failed to serialize Zipkin span: {exc}",
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
        Serialize multiple Zipkin payloads.
        """

        return [
            self.serialize(
                payload,
            )
            for payload in payloads
        ]


# ==============================================================================
# Part 6. Export API
# ==============================================================================


    def export(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload through the Zipkin exporter contract.

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

            error = ZipkinExportError(
                "Zipkin exporter is closed",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        if not self._enabled:

            error = ZipkinExportError(
                "Zipkin exporter is disabled",
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
                raise ZipkinExportError(
                    "invalid Zipkin payload",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Validate options
            # --------------------------------------------------------------

            if not self.validate_options(
                options,
            ):
                raise ZipkinExportError(
                    "invalid Zipkin export options",
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
                    "transport": "zipkin",
                },
            )

        except ZipkinExportError as exc:

            self._record_error(
                exc,
            )

            raise

        except ExportError as exc:

            error = ZipkinExportError(
                str(exc),
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc

        except Exception as exc:

            error = ZipkinExportError(
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
        Export multiple Zipkin payloads.
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
        Validate a Zipkin export payload.
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
        Validate Zipkin exporter options.
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
        Validate a Zipkin endpoint.

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
            raise ZipkinExportError(
                "invalid Zipkin endpoint",
                exporter=self._name,
            )

        target = target.strip()

        if not target:
            raise ZipkinExportError(
                "invalid Zipkin endpoint",
                exporter=self._name,
            )

        if not (
            target.startswith("http://")
            or target.startswith("https://")
        ):
            raise ZipkinExportError(
                "Zipkin endpoint must use http or https",
                exporter=self._name,
            )

        return True


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "ZipkinExporter":
        """
        Start the Zipkin exporter.
        """

        if self._state == "closed":
            raise ZipkinExportError(
                "Zipkin exporter is closed",
                exporter=self._name,
            )

        self._state = "running"

        return self


    def stop(
        self,
    ) -> "ZipkinExporter":
        """
        Stop the Zipkin exporter.
        """

        if self._state == "closed":
            raise ZipkinExportError(
                "Zipkin exporter is closed",
                exporter=self._name,
            )

        self._state = "stopped"

        return self


    def reset(
        self,
    ) -> "ZipkinExporter":
        """
        Reset exporter runtime statistics and state.
        """

        if self._state == "closed":
            raise ZipkinExportError(
                "Zipkin exporter is closed",
                exporter=self._name,
            )

        self._state = "created"

        self._export_count = 0
        self._success_count = 0
        self._error_count = 0
        self._bytes_exported = 0

        self._last_export = None
        self._last_error = None

        return self


    def close(
        self,
    ) -> "ZipkinExporter":
        """
        Permanently close the Zipkin exporter.
        """

        self._state = "closed"

        return self


# ==============================================================================
# Part 9. Error Handling
# ==============================================================================


    def _handle_error(
        self,
        error: Exception,
    ) -> ZipkinExportError:
        """
        Normalize an exception into ZipkinExportError.
        """

        if isinstance(
            error,
            ZipkinExportError,
        ):
            normalized = error

        elif isinstance(
            error,
            ExportError,
        ):
            normalized = ZipkinExportError(
                str(error),
                exporter=self._name,
                cause=error,
            )

        else:
            normalized = ZipkinExportError(
                str(error),
                exporter=self._name,
                cause=error,
            )

        self._record_error(
            normalized,
        )

        return normalized


    def _record_error(
        self,
        error: Exception,
    ) -> None:
        """
        Record one exporter error.
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
        Return the total number of export attempts.
        """

        return self._export_count


    @property
    def success_count(
        self,
    ) -> int:
        """
        Return the number of successful exports.
        """

        return self._success_count


    @property
    def error_count(
        self,
    ) -> int:
        """
        Return the number of failed operations.
        """

        return self._error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """
        Return the total number of exported bytes.
        """

        return self._bytes_exported


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return Zipkin exporter health information.
        """

        return {
            "healthy": (
                self._enabled
                and self._state != "closed"
                and self.validate_endpoint()
            ),
            "state": self._state,
            "enabled": self._enabled,
            "endpoint": self._endpoint,
            "service_name": self._service_name,
        }


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed exporter diagnostics.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "service_name": self._service_name,
            "encoding": self._encoding,
            "enabled": self._enabled,
            "state": self._state,
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
            "transport": "zipkin",
            "state": self._state,
            "enabled": self._enabled,
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
        Return the developer representation.
        """

        return (
            "ZipkinExporter("
            f"name={self._name!r}, "
            f"endpoint={self._endpoint!r}, "
            f"service_name={self._service_name!r}, "
            f"encoding={self._encoding!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            ")"
        )


    def __str__(
        self,
    ) -> str:
        """
        Return the human-readable representation.
        """

        return (
            f"ZipkinExporter("
            f"{self._name}, "
            f"{self._endpoint}, "
            f"state={self._state}"
            ")"
        )


# ==============================================================================
# Part 13. End
# ==============================================================================
