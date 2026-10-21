# ==============================================================================
# SciOS Runtime Observability
# OpenTelemetry Exporter
# ==============================================================================

from __future__ import annotations

import json
import time
from typing import Any, Iterable, Mapping, Optional

from .exporter import (
    ExportError,
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Part 1. Imports
# ==============================================================================

# typing
# time
# base exporter


# ==============================================================================
# Part 2. Public API
# ==============================================================================


class OTELExportError(
    ExportError,
):
    """
    Raised when an OpenTelemetry export operation fails.
    """

    pass


__all__ = [
    "OTELExporter",
    "OTELExportError",
]


# ==============================================================================
# Part 3. OTELExporter
# ==============================================================================


class OTELExporter(
    Exporter,
):
    """
    OpenTelemetry-compatible trace exporter.

    This implementation provides the exporter contract and serialization
    layer without requiring the OpenTelemetry SDK to be installed.
    """

    def __init__(
        self,
        name: str = "otel",
        *,
        endpoint: str = "http://localhost:4318",
        encoding: str = "utf-8",
        enabled: bool = True,
        options: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Validate endpoint
        # ------------------------------------------------------------------

        if not isinstance(
            endpoint,
            str,
        ):
            raise TypeError(
                "endpoint must be a string",
            )

        endpoint = endpoint.strip()

        if not endpoint:
            raise ValueError(
                "endpoint must not be empty",
            )

        # ------------------------------------------------------------------
        # Validate options
        # ------------------------------------------------------------------

        if options is None:
            normalized_options: dict[
                str,
                Any,
            ] = {}

        else:
            if not isinstance(
                options,
                Mapping,
            ):
                raise TypeError(
                    "options must be a mapping",
                )

            normalized_options = dict(
                options,
            )

        # ------------------------------------------------------------------
        # Base exporter
        # ------------------------------------------------------------------

        super().__init__(
            name=name,
            format=ExportFormat.JSON,
            encoding=encoding,
            enabled=enabled,
            options=normalized_options,
        )

        # ------------------------------------------------------------------
        # OTEL configuration
        # ------------------------------------------------------------------

        self._endpoint = endpoint

        # ------------------------------------------------------------------
        # Runtime state
        # ------------------------------------------------------------------

        self._last_export: float | None = None


# ==============================================================================
# Part 4. Core Properties
# ==============================================================================


    @property
    def endpoint(
        self,
    ) -> str:
        """
        Return the configured OpenTelemetry endpoint.
        """

        return self._endpoint


    @property
    def encoding(
        self,
    ) -> str:
        """
        Return the configured payload encoding.
        """

        return self._encoding


    @property
    def options(
        self,
    ) -> dict[str, Any]:
        """
        Return OpenTelemetry exporter options.
        """

        return self._options


# ==============================================================================
# Part 5. OTEL Export
# ==============================================================================


    def serialize(
        self,
        payload: ExportPayload,
    ) -> str:
        """
        Serialize a payload into OTEL JSON text.

        The serializer always returns ``str``.
        """

        if not self.validate_payload(
            payload,
        ):
            raise OTELExportError(
                "invalid OTEL export payload",
                exporter=self._name,
            )

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

            error = OTELExportError(
                f"failed to serialize OTEL payload: {exc}",
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc


    def export(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """
        Export one payload using the OpenTelemetry exporter contract.
        """

        # ------------------------------------------------------------------
        # Export attempt
        # ------------------------------------------------------------------

        self._export_count += 1

        # ------------------------------------------------------------------
        # Lifecycle guards
        # ------------------------------------------------------------------

        if self._state == "closed":

            error = OTELExportError(
                "OpenTelemetry exporter is closed",
                exporter=self._name,
            )

            self._record_error(
                error,
            )

            raise error

        if not self._enabled:

            error = OTELExportError(
                "OpenTelemetry exporter is disabled",
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
                raise OTELExportError(
                    "invalid OpenTelemetry payload",
                    exporter=self._name,
                )

            # --------------------------------------------------------------
            # Validate options
            # --------------------------------------------------------------

            if not self.validate_options(
                options,
            ):
                raise OTELExportError(
                    "invalid OpenTelemetry export options",
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

            # ``serialize()`` always returns str.
            exported = serialized

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
                payload=exported,
                format=self._format,
                bytes_exported=byte_count,
                metadata={
                    "endpoint": self._endpoint,
                    "encoding": self._encoding,
                    "transport": "otel",
                },
            )

        except OTELExportError as exc:

            # ``serialize()`` may already have recorded the error.
            # Avoid incrementing the error counter twice.
            if self._last_error is not exc:
                self._record_error(
                    exc,
                )

            raise

        except ExportError as exc:

            error = OTELExportError(
                str(exc),
                exporter=self._name,
                cause=exc,
            )

            self._record_error(
                error,
            )

            raise error from exc

        except Exception as exc:

            error = OTELExportError(
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
        Export multiple OpenTelemetry payloads.
        """

        return [
            self.export(
                payload,
                **options,
            )
            for payload in payloads
        ]


# ==============================================================================
# Part 6. Validation
# ==============================================================================


    def validate_payload(
        self,
        payload: ExportPayload,
    ) -> bool:
        """
        Validate an OpenTelemetry payload.
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
        Validate OpenTelemetry export options.
        """

        if options is None:
            return True

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

# ==============================================================================
# Part 7. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "OTELExporter":
        """
        Start the OpenTelemetry exporter.
        """

        if self._state == "closed":
            raise OTELExportError(
                "cannot start a closed OpenTelemetry exporter",
                exporter=self._name,
            )

        self._state = "running"

        return self


    def stop(
        self,
    ) -> "OTELExporter":
        """
        Stop the OpenTelemetry exporter.
        """

        if self._state == "closed":
            return self

        self._state = "stopped"

        return self


    def reset(
        self,
    ) -> "OTELExporter":
        """
        Reset exporter runtime state and statistics.
        """

        if self._state == "closed":
            raise OTELExportError(
                "cannot reset a closed OpenTelemetry exporter",
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
    ) -> "OTELExporter":
        """
        Permanently close the exporter.
        """

        if self._state == "closed":
            return self

        self._state = "closed"

        return self


# ==============================================================================
# Part 8. Error Handling
# ==============================================================================


    def _handle_error(
        self,
        error: OTELExportError,
    ) -> ExportResult:
        """
        Convert an OpenTelemetry exporter error into an ExportResult.
        """

        self._record_error(
            error,
        )

        return ExportResult(
            success=False,
            payload=None,
            format=ExportFormat.JSON,
            bytes_exported=0,
            error=error,
            metadata={
                "endpoint": self._endpoint,
                "transport": "otel",
            },
        )


    def _record_error(
        self,
        error: ExportError,
    ) -> None:
        """
        Record exporter error state.
        """

        self._error_count += 1
        self._last_error = error


# ==============================================================================
# Part 9. Statistics
# ==============================================================================


    @property
    def export_count(
        self,
    ) -> int:
        """
        Return total number of export attempts.
        """

        return self._export_count


    @property
    def success_count(
        self,
    ) -> int:
        """
        Return total number of successful exports.
        """

        return self._success_count


    @property
    def error_count(
        self,
    ) -> int:
        """
        Return total number of failed exports.
        """

        return self._error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """
        Return total number of exported bytes.
        """

        return self._bytes_exported


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================


    def health(
        self,
    ) -> bool:
        """
        Return whether the exporter is healthy.
        """

        return (
            self._state != "closed"
            and self._state != "failed"
            and self._enabled
        )


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed OpenTelemetry exporter diagnostics.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
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
            "transport": "otel",
        }


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a compact OpenTelemetry exporter summary.
        """

        return {
            "name": self._name,
            "endpoint": self._endpoint,
            "state": self._state,
            "enabled": self._enabled,
            "healthy": self.health(),
            "export_count": self._export_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "bytes_exported": self._bytes_exported,
        }


# ==============================================================================
# Part 11. Representation
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Return the developer representation.
        """

        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"endpoint={self._endpoint!r}, "
            f"encoding={self._encoding!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        """
        Return the human-readable representation.
        """

        return (
            f"{self._name}("
            f"endpoint={self._endpoint}, "
            f"state={self._state}, "
            f"enabled={self._enabled}"
            f")"
        )


# ==============================================================================
# Part 12. End
# ==============================================================================
