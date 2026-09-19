# ==============================================================================
# SciOS Runtime Observability
# JSON Exporter
# ==============================================================================

from __future__ import annotations

import json
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


# json
# typing
# base exporter imported above


# ==============================================================================
# Part 2. Public API
# ==============================================================================


__all__ = [
    "JSONExporter",
]


# ==============================================================================
# Part 3. JSONExporter
# ==============================================================================


class JSONExporter(Exporter):
    """
    JSON exporter for SciOS runtime observability data.

    Extends the base :class:`Exporter` with JSON-specific
    serialization configuration.
    """

    def __init__(
        self,
        name: str = "json",
        *,
        encoding: str = "utf-8",
        ensure_ascii: bool = False,
        indent: int | None = 2,
        sort_keys: bool = False,
        enabled: bool = True,
        options: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Validate JSON-specific configuration
        # ------------------------------------------------------------------

        if not isinstance(
            ensure_ascii,
            bool,
        ):
            raise TypeError(
                "ensure_ascii must be a bool",
            )

        if indent is not None and (
            not isinstance(
                indent,
                int,
            )
            or isinstance(
                indent,
                bool,
            )
            or indent < 0
        ):
            raise ValueError(
                "indent must be a non-negative integer or None",
            )

        if not isinstance(
            sort_keys,
            bool,
        ):
            raise TypeError(
                "sort_keys must be a bool",
            )

        # ------------------------------------------------------------------
        # Initialize base exporter
        # ------------------------------------------------------------------

        super().__init__(
            name=name,
            format=ExportFormat.JSON,
            encoding=encoding,
            enabled=enabled,
            options=options,
        )

        # ------------------------------------------------------------------
        # JSON configuration
        # ------------------------------------------------------------------

        self._ensure_ascii = ensure_ascii
        self._indent = indent
        self._sort_keys = sort_keys

        # Keep JSON configuration synchronized with exporter options.
        self._options.update(
            {
                "ensure_ascii": self._ensure_ascii,
                "indent": self._indent,
                "sort_keys": self._sort_keys,
            },
        )


# ==============================================================================
# Part 4. Core Properties
# ==============================================================================


    @property
    def ensure_ascii(
        self,
    ) -> bool:
        """
        Return whether non-ASCII characters are escaped.
        """

        return self._ensure_ascii


    @property
    def indent(
        self,
    ) -> int | None:
        """
        Return JSON indentation level.
        """

        return self._indent


    @property
    def sort_keys(
        self,
    ) -> bool:
        """
        Return whether JSON object keys are sorted.
        """

        return self._sort_keys


# ==============================================================================
# Part 5. JSON Serialization
# ==============================================================================


    def serialize(
        self,
        payload: ExportPayload,
    ) -> str:
        """
        Serialize a payload to JSON text.
        """

        if not self.validate_payload(
            payload,
        ):
            raise ExportError(
                "invalid JSON export payload",
                exporter=self._name,
            )

        try:
            return json.dumps(
                payload,
                ensure_ascii=self._ensure_ascii,
                indent=self._indent,
                sort_keys=self._sort_keys,
                default=str,
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:

            raise ExportError(
                "failed to serialize payload as JSON",
                exporter=self._name,
                cause=exc,
            ) from exc


    def serialize_mapping(
        self,
        payload: Mapping[str, Any],
    ) -> str:
        """
        Serialize a mapping directly to JSON text.
        """

        if not isinstance(
            payload,
            Mapping,
        ):
            raise TypeError(
                "payload must be a mapping",
            )

        return self.serialize(
            payload,
        )


    def serialize_many(
        self,
        payloads: Iterable[
            ExportPayload
        ],
    ) -> list[str]:
        """
        Serialize multiple payloads to JSON text.
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
        Export one payload as JSON.

        Statistics and lifecycle handling are delegated to the
        base exporter while JSON serialization is provided by
        this class.
        """

        return super().export(
            payload,
            **options,
        )


    def export_many(
        self,
        payloads: Iterable[
            ExportPayload
        ],
        **options: Any,
    ) -> list[ExportResult]:
        """
        Export multiple payloads as JSON.
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
        Validate a JSON-exportable payload.

        JSONExporter accepts the same public payload types as the
        base Exporter. Actual JSON compatibility is verified during
        serialization.
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
        Validate per-export JSON options.

        Supported options:

        - ensure_ascii
        - indent
        - sort_keys
        """

        if not super().validate_options(
            options,
        ):
            return False

        if options is None:
            return True

        if "ensure_ascii" in options:
            if not isinstance(
                options["ensure_ascii"],
                bool,
            ):
                return False

        if "indent" in options:
            indent = options["indent"]

            if indent is not None and (
                not isinstance(
                    indent,
                    int,
                )
                or isinstance(
                    indent,
                    bool,
                )
                or indent < 0
            ):
                return False

        if "sort_keys" in options:
            if not isinstance(
                options["sort_keys"],
                bool,
            ):
                return False

        return True


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================


    def start(
        self,
    ) -> "JSONExporter":
        """
        Start the JSON exporter.
        """

        super().start()

        return self


    def stop(
        self,
    ) -> "JSONExporter":
        """
        Stop the JSON exporter.
        """

        super().stop()

        return self


    def reset(
        self,
    ) -> "JSONExporter":
        """
        Reset JSON exporter runtime state and statistics.
        """

        super().reset()

        return self


    def close(
        self,
    ) -> "JSONExporter":
        """
        Close the JSON exporter permanently.
        """

        super().close()

        return self


# ==============================================================================
# Part 9. Statistics
# ==============================================================================


    @property
    def export_count(
        self,
    ) -> int:
        """
        Return total export attempts.
        """

        return super().export_count


    @property
    def success_count(
        self,
    ) -> int:
        """
        Return successful export count.
        """

        return super().success_count


    @property
    def error_count(
        self,
    ) -> int:
        """
        Return failed export count.
        """

        return super().error_count


    @property
    def bytes_exported(
        self,
    ) -> int:
        """
        Return total number of exported bytes.
        """

        return super().bytes_exported


# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed JSON exporter diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "exporter_type": type(self).__name__,
                "ensure_ascii": self._ensure_ascii,
                "indent": self._indent,
                "sort_keys": self._sort_keys,
            },
        )

        return diagnostics


    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a compact JSON exporter summary.
        """

        summary = super().summary()

        summary.update(
            {
                "exporter_type": type(self).__name__,
                "ensure_ascii": self._ensure_ascii,
                "indent": self._indent,
                "sort_keys": self._sort_keys,
            },
        )

        return summary


# ==============================================================================
# Part 11. Representation
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self._name!r}, "
            f"encoding={self._encoding!r}, "
            f"ensure_ascii={self._ensure_ascii!r}, "
            f"indent={self._indent!r}, "
            f"sort_keys={self._sort_keys!r}, "
            f"enabled={self._enabled!r}, "
            f"state={self._state!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        return (
            f"{self._name}("
            f"format=json, "
            f"state={self._state}, "
            f"enabled={self._enabled}, "
            f"indent={self._indent}, "
            f"sort_keys={self._sort_keys}"
            f")"
        )


# ==============================================================================
# Part 12. End
# ==============================================================================


__all__ = [
    "JSONExporter",
]
