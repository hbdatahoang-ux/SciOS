"""
SciOS-NG Runtime Observability
JSON Exporter
==============================

File:
    scios/runtime/observability/exporters/json.py

Purpose
-------
Export observability payloads as JSON text.

Design
------
``Exporter.format`` remains the stable base-class property returning
``ExportFormat.JSON``.

The callable serialization API is intentionally named
``format_string`` rather than ``format``.

Python
------
3.11+
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import io
import json
import threading
import time

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Mapping, Optional, TextIO

from .base import (
    ExportError,
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Part 2. Constants
# ==============================================================================

JSON_EXPORTER_VERSION: str = "0.3.0-alpha"

DEFAULT_JSON_STREAM: TextIO = io.StringIO()

DEFAULT_JSON_INDENT: Optional[int] = None
DEFAULT_JSON_ENSURE_ASCII: bool = False
DEFAULT_JSON_SORT_KEYS: bool = False
DEFAULT_JSON_ALLOW_NAN: bool = True
DEFAULT_JSON_CHECK_CIRCULAR: bool = True
DEFAULT_JSON_SKIP_KEYS: bool = False

DEFAULT_JSON_PREFIX: str = ""
DEFAULT_JSON_SUFFIX: str = "\n"

DEFAULT_JSON_AUTO_FLUSH: bool = True


# ==============================================================================
# Part 3. JSON Export Options
# ==============================================================================


@dataclass(slots=True)
class JSONExportOptions:
    """
    Configuration for ``JSONExporter``.
    """

    stream: TextIO = DEFAULT_JSON_STREAM

    indent: Optional[int] = DEFAULT_JSON_INDENT
    ensure_ascii: bool = DEFAULT_JSON_ENSURE_ASCII
    sort_keys: bool = DEFAULT_JSON_SORT_KEYS
    allow_nan: bool = DEFAULT_JSON_ALLOW_NAN
    check_circular: bool = DEFAULT_JSON_CHECK_CIRCULAR
    skip_keys: bool = DEFAULT_JSON_SKIP_KEYS

    prefix: str = DEFAULT_JSON_PREFIX
    suffix: str = DEFAULT_JSON_SUFFIX

    auto_flush: bool = DEFAULT_JSON_AUTO_FLUSH

    def validate(self) -> bool:
        """Validate exporter options."""

        if not hasattr(self.stream, "write"):
            raise TypeError(
                "stream must provide a write() method"
            )

        if self.indent is not None:
            if not isinstance(self.indent, int):
                raise TypeError(
                    "indent must be an integer or None"
                )

            if self.indent < 0:
                raise ValueError(
                    "indent must be >= 0"
                )

        boolean_options = {
            "ensure_ascii": self.ensure_ascii,
            "sort_keys": self.sort_keys,
            "allow_nan": self.allow_nan,
            "check_circular": self.check_circular,
            "skip_keys": self.skip_keys,
            "auto_flush": self.auto_flush,
        }

        for name, value in boolean_options.items():
            if not isinstance(value, bool):
                raise TypeError(
                    f"{name} must be bool"
                )

        if not isinstance(self.prefix, str):
            raise TypeError(
                "prefix must be a string"
            )

        if not isinstance(self.suffix, str):
            raise TypeError(
                "suffix must be a string"
            )

        return True


# ==============================================================================
# Part 4. JSON Exporter
# ==============================================================================


class JSONExporter(Exporter):
    """
    Export arbitrary observability objects as JSON.

    The exporter supports:

    * primitive values
    * mappings
    * sequences
    * ``ExportPayload``
    * dataclasses
    * enums
    * objects exposing ``to_dict()``
    * ordinary objects exposing ``__dict__``

    ``serialize()`` returns pure JSON.

    ``format_string()`` returns the final stream representation including
    configured prefix and suffix.

    Lifecycle statistics are owned by the base ``Exporter`` contract.
    JSON-specific statistics are maintained locally.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "json",
        *,
        stream: Optional[TextIO] = None,
        options: Optional[JSONExportOptions] = None,
        encoding: str = "utf-8",
        enabled: bool = True,
    ) -> None:

        # ==================================================================
        # Part 1. Resolve configuration
        # ==================================================================

        if options is not None:
            options.validate()

            configured_stream = options.stream

            indent = options.indent
            ensure_ascii = options.ensure_ascii
            sort_keys = options.sort_keys
            allow_nan = options.allow_nan
            check_circular = options.check_circular
            skip_keys = options.skip_keys

            prefix = options.prefix
            suffix = options.suffix
            auto_flush = options.auto_flush

        else:
            configured_stream = (
                stream
                if stream is not None
                else io.StringIO()
            )

            indent = DEFAULT_JSON_INDENT
            ensure_ascii = DEFAULT_JSON_ENSURE_ASCII
            sort_keys = DEFAULT_JSON_SORT_KEYS
            allow_nan = DEFAULT_JSON_ALLOW_NAN
            check_circular = DEFAULT_JSON_CHECK_CIRCULAR
            skip_keys = DEFAULT_JSON_SKIP_KEYS

            prefix = DEFAULT_JSON_PREFIX
            suffix = DEFAULT_JSON_SUFFIX
            auto_flush = DEFAULT_JSON_AUTO_FLUSH

        # ==================================================================
        # Part 2. Initialize subclass state BEFORE Exporter.__init__()
        #
        # Exporter.__init__() may invoke self.validate(). Therefore every
        # JSON-specific attribute accessed by validation must exist before
        # calling super().__init__().
        # ==================================================================

        # ------------------------------------------------------------------
        # Output stream
        # ------------------------------------------------------------------

        self._stream: TextIO = configured_stream

        # ------------------------------------------------------------------
        # JSON serialization configuration
        # ------------------------------------------------------------------

        self._indent: Optional[int] = indent
        self._ensure_ascii: bool = ensure_ascii
        self._sort_keys: bool = sort_keys
        self._allow_nan: bool = allow_nan
        self._check_circular: bool = check_circular
        self._skip_keys: bool = skip_keys

        # ------------------------------------------------------------------
        # Output formatting
        # ------------------------------------------------------------------

        self._prefix: str = prefix
        self._suffix: str = suffix
        self._auto_flush: bool = auto_flush

        # ------------------------------------------------------------------
        # JSON-specific runtime statistics
        #
        # These are intentionally different from the base Exporter
        # lifecycle counters.
        #
        #   bytes_written   = UTF-8/encoding bytes physically written
        #   lines_written   = logical newline count
        #   objects_exported = successful write operations
        #
        # DO NOT initialize:
        #
        #   _export_count
        #   _success_count
        #   _failure_count
        #
        # Those belong to Exporter.
        # ------------------------------------------------------------------

        self._bytes_written: int = 0
        self._lines_written: int = 0
        self._objects_exported: int = 0

        # ------------------------------------------------------------------
        # Last JSON output
        # ------------------------------------------------------------------

        self._last_output: Optional[str] = None
        self._last_output_time: Optional[float] = None

        # ------------------------------------------------------------------
        # Synchronization
        # ------------------------------------------------------------------

        self._json_lock = threading.RLock()

        # ------------------------------------------------------------------
        # Version
        # ------------------------------------------------------------------

        self._version: str = JSON_EXPORTER_VERSION

        # ==================================================================
        # Part 3. Base exporter initialization
        # ==================================================================

        super().__init__(
            name=name,
            format=ExportFormat.JSON,
            encoding=encoding,
            enabled=enabled,
            options={
                "indent": self._indent,
                "ensure_ascii": self._ensure_ascii,
                "sort_keys": self._sort_keys,
                "allow_nan": self._allow_nan,
                "check_circular": self._check_circular,
                "skip_keys": self._skip_keys,
                "prefix": self._prefix,
                "suffix": self._suffix,
                "auto_flush": self._auto_flush,
            },
        )

    # ==========================================================================
    # Part 5. Export Statistics
    # ==========================================================================

    @property
    def export_count(self) -> int:
        """
        Return the total number of export attempts.

        The underlying counter is owned by ``Exporter``.
        """
        return self._export_count

    @property
    def success_count(self) -> int:
        """
        Return the number of successful export attempts.

        The underlying counter is owned by ``Exporter``.
        """
        return self._success_count

    @property
    def failure_count(self) -> int:
        """Return the number of failed export attempts."""
        return self.error_count

    # ==========================================================================
    # Part 5. Properties
    # ==========================================================================

    @property
    def version(self) -> str:
        """Return exporter version."""

        return self._version

    @property
    def stream(self) -> TextIO:
        """Return configured output stream."""

        return self._stream

    @property
    def indent(self) -> Optional[int]:
        """Return JSON indentation."""

        return self._indent

    @property
    def ensure_ascii(self) -> bool:
        """Return Unicode escaping configuration."""

        return self._ensure_ascii

    @property
    def sort_keys(self) -> bool:
        """Return key sorting configuration."""

        return self._sort_keys

    @property
    def allow_nan(self) -> bool:
        """Return NaN/Infinity configuration."""

        return self._allow_nan

    @property
    def check_circular(self) -> bool:
        """Return circular-reference checking configuration."""

        return self._check_circular

    @property
    def skip_keys(self) -> bool:
        """Return non-basic dictionary key handling."""

        return self._skip_keys

    @property
    def prefix(self) -> str:
        """Return output prefix."""

        return self._prefix

    @property
    def suffix(self) -> str:
        """Return output suffix."""

        return self._suffix

    @property
    def auto_flush(self) -> bool:
        """Return auto-flush configuration."""

        return self._auto_flush

    @property
    def bytes_written(self) -> int:
        """Return total number of encoded bytes written."""

        return self._bytes_written

    @property
    def lines_written(self) -> int:
        """Return number of newline characters written."""

        return self._lines_written

    @property
    def objects_exported(self) -> int:
        """Return number of successfully exported objects."""

        return self._objects_exported

    @property
    def last_output(self) -> Optional[str]:
        """Return the most recently written formatted output."""

        return self._last_output

    @property
    def last_output_time(self) -> Optional[float]:
        """Return timestamp of the last successful write."""

        return self._last_output_time

    # ==========================================================================
    # Part 6. JSON Serialization
    # ==========================================================================

    def _json_kwargs(self) -> dict[str, Any]:
        """Build the canonical ``json.dumps`` configuration."""

        return {
            "indent": self._indent,
            "ensure_ascii": self._ensure_ascii,
            "sort_keys": self._sort_keys,
            "allow_nan": self._allow_nan,
            "check_circular": self._check_circular,
            "skipkeys": self._skip_keys,
            "default": self._json_default,
        }

    def _json_default(self, obj: Any) -> Any:
        """
        Convert supported non-standard Python objects into JSON values.
        """

        # ------------------------------------------------------------------
        # ExportPayload
        # ------------------------------------------------------------------

        if isinstance(obj, ExportPayload):
            return {
                "name": obj.name,
                "value": obj.value,
                "labels": dict(obj.labels),
                "timestamp": obj.timestamp,
                "metadata": dict(obj.metadata),
                "options": dict(obj.options),
            }

        # ------------------------------------------------------------------
        # Dataclass
        # ------------------------------------------------------------------

        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        # ------------------------------------------------------------------
        # Enum
        # ------------------------------------------------------------------

        if isinstance(obj, Enum):
            return obj.value

        # ------------------------------------------------------------------
        # to_dict()
        # ------------------------------------------------------------------

        to_dict = getattr(obj, "to_dict", None)

        if callable(to_dict):
            value = to_dict()

            if value is obj:
                raise TypeError(
                    f"to_dict() returned self for "
                    f"{type(obj).__name__}"
                )

            return value

        # ------------------------------------------------------------------
        # Mapping-like objects
        # ------------------------------------------------------------------

        if isinstance(obj, Mapping):
            return dict(obj)

        # ------------------------------------------------------------------
        # __dict__
        # ------------------------------------------------------------------

        if hasattr(obj, "__dict__"):
            return vars(obj)

        raise TypeError(
            f"Object of type {type(obj).__name__} "
            "is not JSON serializable"
        )

    def serialize(self, obj: Any) -> str:
        """
        Serialize an arbitrary object into pure JSON.

        This method intentionally does NOT add prefix/suffix.

        Therefore:

            exporter.serialize(value)
            exporter.encode(value)

        always produce the same string.
        """

        try:
            return json.dumps(
                obj,
                **self._json_kwargs(),
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise ExportError(
                f"JSON serialization failed: {exc}"
            ) from exc

    def format_string(self, obj: Any) -> str:
        """
        Serialize an object and add configured prefix/suffix.
        """

        serialized = self.serialize(obj)

        return (
            f"{self._prefix}"
            f"{serialized}"
            f"{self._suffix}"
        )

    def encode(self, obj: Any) -> str:
        """
        Encode an object as JSON.

        Alias for ``serialize()``.
        """

        return self.serialize(obj)

    def deserialize(
        self,
        payload: str,
    ) -> Any:
        """
        Deserialize JSON text.

        Configured prefix/suffix are stripped when present.

        Raises
        ------
        TypeError
            If payload is not a string.

        ValueError
            If payload is not valid JSON.
        """

        if not isinstance(
            payload,
            str,
        ):
            raise TypeError(
                "payload must be a string"
            )

        text = payload

        if self._prefix and text.startswith(
            self._prefix
        ):
            text = text[
                len(self._prefix):
            ]

        if self._suffix and text.endswith(
            self._suffix
        ):
            text = text[
                : -len(self._suffix)
            ]

        return json.loads(text)

    def decode(self, payload: str) -> Any:
        """Decode JSON text."""

        return self.deserialize(payload)

    # ==========================================================================
    # Part 7. Validation
    # ==========================================================================

    def validate_stream(self) -> bool:
        """Validate configured stream."""

        if not hasattr(self._stream, "write"):
            raise TypeError(
                "stream must provide a write() method"
            )

        if self._auto_flush and not hasattr(
            self._stream,
            "flush",
        ):
            raise TypeError(
                "stream must provide a flush() method "
                "when auto_flush is enabled"
            )

        return True

    def validate_output(
        self,
        output: Any,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate JSON output.

        Prefix/suffix are accepted when configured.
        """

        if not isinstance(output, str):
            if raise_error:
                raise TypeError(
                    "JSON output must be a string"
                )
            return False

        text = output

        if self._prefix and text.startswith(self._prefix):
            text = text[len(self._prefix):]

        if self._suffix and text.endswith(self._suffix):
            text = text[:-len(self._suffix)]

        try:
            json.loads(text)

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            if raise_error:
                raise ValueError(
                    "Invalid JSON output"
                ) from exc

            return False

        return True

    def validate_payload(
        self,
        payload: Any,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate a payload.

        JSONExporter intentionally accepts arbitrary JSON-compatible
        Python objects, not only ExportPayload.
        """

        try:
            self.serialize(payload)
            return True

        except ExportError as exc:
            if raise_error:
                raise

            return False

    def validate(self) -> bool:
        """
        Validate exporter configuration.

        This method is safe to call from ``Exporter.__init__`` because
        subclass state is initialized beforehand.
        """

        result = super().validate()

        self.validate_stream()

        JSONExportOptions(
            stream=self._stream,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self._sort_keys,
            allow_nan=self._allow_nan,
            check_circular=self._check_circular,
            skip_keys=self._skip_keys,
            prefix=self._prefix,
            suffix=self._suffix,
            auto_flush=self._auto_flush,
        ).validate()

        return bool(result)

    # ==========================================================================
    # Part 8. Snapshot / Diagnostics
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a complete runtime snapshot of the JSON exporter.

        Base exporter lifecycle state is represented at the top level.
        JSON-specific configuration and runtime state are grouped under
        the ``"json"`` namespace.
        """

        return {
            # ==================================================================
            # Base exporter state
            # ==================================================================

            "name": self.name,
            "format": self.format.value,
            "version": self.version,
            "enabled": self.enabled,

            "export_count": self.export_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,

            "bytes_exported": getattr(
                self,
                "_bytes_exported",
                0,
            ),

            "last_export": getattr(
                self,
                "_last_export",
                None,
            ),

            "last_error": getattr(
                self,
                "_last_error",
                None,
            ),

            # ==================================================================
            # JSON exporter state
            # ==================================================================

            "json": {
                # Configuration
                "indent": self.indent,
                "ensure_ascii": self.ensure_ascii,
                "sort_keys": self.sort_keys,
                "allow_nan": self.allow_nan,
                "check_circular": self.check_circular,
                "skip_keys": self.skip_keys,

                "prefix": self.prefix,
                "suffix": self.suffix,
                "auto_flush": self.auto_flush,

                # Runtime statistics
                "bytes_written": self.bytes_written,
                "lines_written": self.lines_written,
                "objects_exported": self.objects_exported,

                # Last output
                "last_output": self.last_output,
                "last_output_time": self.last_output_time,
            },
        }

    # ==========================================================================
    # Part 9. Writing
    # ==========================================================================

    def write(
        self,
        text: str,
    ) -> int:
        """
        Write JSON text to the configured stream.

        Returns
        -------
        int
            Number of bytes written using the configured encoding.
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text must be a string"
            )

        if not text:
            return 0

        byte_count = len(
            text.encode(
                self._encoding,
            )
        )

        with self._json_lock:
            self._stream.write(text)

            if self._auto_flush:
                self._stream.flush()

            self._bytes_written += byte_count
            self._lines_written += text.count("\n")
            self._objects_exported += 1

            self._last_output = text
            self._last_output_time = time.time()

        return byte_count

    def write_stream(
        self,
        text: str,
        stream: TextIO,
    ) -> int:
        """
        Write text to an arbitrary stream without changing exporter state.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        if not hasattr(stream, "write"):
            raise TypeError(
                "stream must provide a write() method"
            )

        if self._auto_flush and not hasattr(
            stream,
            "flush",
        ):
            raise TypeError(
                "stream must provide a flush() method "
                "when auto_flush is enabled"
            )

        if not text:
            return 0

        stream.write(text)

        if self._auto_flush:
            stream.flush()

        return len(
            text.encode(self._encoding)
        )

    def flush(self) -> "JSONExporter":
        """Flush configured stream."""

        with self._json_lock:
            self._stream.flush()

        return self

    # ==========================================================================
    # Part 10. Export
    # ==========================================================================

    def export(
        self,
        payload: Any,
        **options: Any,
    ) -> ExportResult:
        """Serialize and export one object."""

        start_time = time.perf_counter()

        with self._json_lock:
            self._export_count += 1
            self._last_export = time.time()

        try:
            self.validate()

            serialized = self.serialize(
                payload,
                **options,
            )

            byte_count = self.write(
                serialized,
            )

            with self._json_lock:
                self._success_count += 1

            return ExportResult(
                success=True,
                exporter=self._name,
                count=1,
                bytes_exported=byte_count,
                duration=time.perf_counter() - start_time,
                error=None,
                data=serialized,
                timestamp=time.time(),
            )

        except Exception as exc:
            with self._json_lock:
                self._failure_count += 1
                self._last_error = str(exc)

            return ExportResult(
                success=False,
                exporter=self._name,
                count=0,
                bytes_exported=0,
                duration=time.perf_counter() - start_time,
                error=str(exc),
                data=None,
                timestamp=time.time(),
            )

    def export_payload(
        self,
        payload: ExportPayload,
        **options: Any,
    ) -> ExportResult:
        """Export an ExportPayload."""

        return self.export(
            payload,
            **options,
        )

    def export_many(
        self,
        payloads: Any,
        **options: Any,
    ) -> list[ExportResult]:
        """
        Export multiple objects in input order.

        Each object is exported independently. A failure for one object
        does not prevent subsequent objects from being exported.
        """

        if isinstance(payloads, (str, bytes)):
            raise TypeError(
                "payloads must be an iterable of objects"
            )

        try:
            iterator = iter(payloads)
        except TypeError as exc:
            raise TypeError(
                "payloads must be iterable"
            ) from exc

        return [
            self.export(
                payload,
                **options,
            )
            for payload in iterator
        ]

    def export_text(
        self,
        text: str,
    ) -> ExportResult:
        """
        Export an already serialized JSON string.

        The text must contain valid JSON. Prefix/suffix are not added
        automatically because the caller supplied the serialized text.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        if not self.validate_output(text):
            raise ValueError(
                "text is not valid JSON"
            )

        start_time = time.perf_counter()

        try:
            byte_count = self.write(text)

            return ExportResult(
                success=True,
                exporter=self._name,
                count=1,
                bytes_exported=byte_count,
                duration=(
                    time.perf_counter()
                    - start_time
                ),
                error=None,
                data=text,
                timestamp=time.time(),
            )

        except Exception as exc:
            return ExportResult(
                success=False,
                exporter=self._name,
                count=0,
                bytes_exported=0,
                duration=(
                    time.perf_counter()
                    - start_time
                ),
                error=str(exc),
                data=None,
                timestamp=time.time(),
            )

    def export_object(
        self,
        obj: Any,
    ) -> ExportResult:
        """Serialize and export an arbitrary object."""

        return self.export(obj)

    def export_dict(
        self,
        data: Mapping[str, Any],
    ) -> ExportResult:
        """Export a mapping as JSON."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping"
            )

        return self.export_object(
            dict(data)
        )

    def export_list(
        self,
        data: list[Any],
    ) -> ExportResult:
        """Export a list as JSON."""

        if not isinstance(data, list):
            raise TypeError(
                "data must be a list"
            )

        return self.export_object(data)

    # ==========================================================================
    # Part 11. Configuration
    # ==========================================================================

    def set_indent(
        self,
        indent: Optional[int],
    ) -> "JSONExporter":
        """Set JSON indentation."""

        if indent is not None:
            if not isinstance(indent, int):
                raise TypeError(
                    "indent must be an integer or None"
                )

            if indent < 0:
                raise ValueError(
                    "indent must be >= 0"
                )

        self._indent = indent
        return self

    def set_ensure_ascii(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set Unicode escaping behavior."""

        if not isinstance(value, bool):
            raise TypeError(
                "ensure_ascii must be bool"
            )

        self._ensure_ascii = value
        return self

    def set_sort_keys(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set key sorting behavior."""

        if not isinstance(value, bool):
            raise TypeError(
                "sort_keys must be bool"
            )

        self._sort_keys = value
        return self

    def set_allow_nan(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set NaN/Infinity handling."""

        if not isinstance(value, bool):
            raise TypeError(
                "allow_nan must be bool"
            )

        self._allow_nan = value
        return self

    def set_check_circular(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set circular-reference checking."""

        if not isinstance(value, bool):
            raise TypeError(
                "check_circular must be bool"
            )

        self._check_circular = value
        return self

    def set_skip_keys(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set non-basic dictionary key handling."""

        if not isinstance(value, bool):
            raise TypeError(
                "skip_keys must be bool"
            )

        self._skip_keys = value
        return self

    def set_prefix(
        self,
        value: str,
    ) -> "JSONExporter":
        """Set output prefix."""

        if not isinstance(value, str):
            raise TypeError(
                "prefix must be a string"
            )

        self._prefix = value
        return self

    def set_suffix(
        self,
        value: str,
    ) -> "JSONExporter":
        """Set output suffix."""

        if not isinstance(value, str):
            raise TypeError(
                "suffix must be a string"
            )

        self._suffix = value
        return self

    def set_auto_flush(
        self,
        value: bool,
    ) -> "JSONExporter":
        """Set automatic stream flushing."""

        if not isinstance(value, bool):
            raise TypeError(
                "auto_flush must be bool"
            )

        self._auto_flush = value
        return self

    # ==========================================================================
    # Part 12. Protocols
    # ==========================================================================

    def __call__(
        self,
        obj: Any,
    ) -> ExportResult:
        """Export an arbitrary object."""

        return self.export_object(obj)

    def __len__(self) -> int:
        """Return number of successfully exported objects."""

        return self._objects_exported

    def __repr__(self) -> str:
        """Return concise developer representation."""

        return (
            "JSONExporter("
            f"name={self._name!r}, "
            f"format={self._format.value!r}, "
            f"stream={type(self._stream).__name__!r}, "
            f"indent={self._indent!r}, "
            f"ensure_ascii={self._ensure_ascii!r}, "
            f"sort_keys={self._sort_keys!r}"
            ")"
        )

    def __str__(self) -> str:
        """Return human-readable description."""

        return (
            "JSONExporter("
            f"name={self._name!r}, "
            f"format={self._format.value!r}"
            ")"
        )


# ==============================================================================
# Part 13. Public API
# ==============================================================================

__all__ = [
    "JSONExporter",
    "JSONExportOptions",
    "JSON_EXPORTER_VERSION",
    "DEFAULT_JSON_STREAM",
    "DEFAULT_JSON_INDENT",
    "DEFAULT_JSON_ENSURE_ASCII",
    "DEFAULT_JSON_SORT_KEYS",
    "DEFAULT_JSON_ALLOW_NAN",
    "DEFAULT_JSON_CHECK_CIRCULAR",
    "DEFAULT_JSON_SKIP_KEYS",
    "DEFAULT_JSON_PREFIX",
    "DEFAULT_JSON_SUFFIX",
    "DEFAULT_JSON_AUTO_FLUSH",
]