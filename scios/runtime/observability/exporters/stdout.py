"""
SciOS Runtime Observability
===========================

Stdout Exporter
---------------

Concrete exporter that writes SciOS observability payloads to a
text stream, normally ``sys.stdout``.

This implementation follows the stable generic contract defined by
``exporters.base.Exporter``.

Python 3.11+
"""

from __future__ import annotations

import copy
import io
import sys
import threading
import time

from dataclasses import dataclass
from typing import Any, Optional, TextIO

from .base import (
    ExportFormat,
    ExportPayload,
    ExportResult,
    Exporter,
)


# ==============================================================================
# Part 1. Constants
# ==============================================================================

DEFAULT_STREAM: TextIO = sys.stdout

DEFAULT_SEPARATOR = " "
DEFAULT_PREFIX = ""
DEFAULT_SUFFIX = "\n"
DEFAULT_AUTO_FLUSH = True

STDOUT_EXPORTER_VERSION = "0.1.0"


# ==============================================================================
# Part 2. Options
# ==============================================================================


@dataclass(slots=True)
class StdoutExportOptions:
    """
    Configuration for :class:`StdoutExporter`.
    """

    stream: TextIO = DEFAULT_STREAM
    separator: str = DEFAULT_SEPARATOR
    prefix: str = DEFAULT_PREFIX
    suffix: str = DEFAULT_SUFFIX
    auto_flush: bool = DEFAULT_AUTO_FLUSH

    def validate(self) -> None:
        """Validate stdout configuration."""

        _validate_stream(self.stream)

        if not isinstance(self.separator, str):
            raise TypeError("separator must be a string")

        if not isinstance(self.prefix, str):
            raise TypeError("prefix must be a string")

        if not isinstance(self.suffix, str):
            raise TypeError("suffix must be a string")

        if not isinstance(self.auto_flush, bool):
            raise TypeError("auto_flush must be a bool")


# ==============================================================================
# Part 3. Stream Helpers
# ==============================================================================


def _validate_stream(stream: Any) -> None:
    """
    Validate that an object behaves like a writable text stream.
    """

    if stream is None:
        raise ValueError("stream cannot be None")

    write = getattr(stream, "write", None)

    if not callable(write):
        raise TypeError(
            "stream must provide a callable write() method"
        )


# ==============================================================================
# Part 4. Stdout Exporter
# ==============================================================================


class StdoutExporter(Exporter):
    """
    Export observability payloads to stdout or another text stream.

    ``Exporter.__init__()`` invokes ``self.validate()``.
    Therefore every attribute accessed by the overridden ``validate()``
    must be initialized before calling ``super().__init__()``.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "stdout",
        *,
        stream: Optional[TextIO] = None,
        options: Optional[StdoutExportOptions] = None,
        encoding: str = "utf-8",
        enabled: bool = True,
    ) -> None:

        # ==================================================================
        # 1. Resolve configuration
        # ==================================================================

        if options is not None:
            options.validate()

            configured_stream = options.stream
            separator = options.separator
            prefix = options.prefix
            suffix = options.suffix
            auto_flush = options.auto_flush

        else:
            configured_stream = (
                stream
                if stream is not None
                else DEFAULT_STREAM
            )

            separator = DEFAULT_SEPARATOR
            prefix = DEFAULT_PREFIX
            suffix = DEFAULT_SUFFIX
            auto_flush = DEFAULT_AUTO_FLUSH

        # ==================================================================
        # 2. Initialize subclass state BEFORE base constructor
        #
        # Exporter.__init__() calls self.validate().
        # Therefore validate() must be able to access all of these fields.
        # ==================================================================

        self._stream: TextIO = configured_stream
        self._separator: str = separator
        self._prefix: str = prefix
        self._suffix: str = suffix
        self._auto_flush: bool = auto_flush

        self._bytes_written: int = 0
        self._lines_written: int = 0
        self._objects_exported: int = 0

        self._last_output: Optional[str] = None
        self._last_output_time: Optional[float] = None

        self._stdout_lock = threading.RLock()

        self._version = STDOUT_EXPORTER_VERSION

        # ==================================================================
        # 3. Initialize generic exporter
        # ==================================================================

        super().__init__(
            name=name,
            format=ExportFormat.TEXT,
            encoding=encoding,
            enabled=enabled,
            options={
                "separator": self._separator,
                "prefix": self._prefix,
                "suffix": self._suffix,
                "auto_flush": self._auto_flush,
            },
        )

    # ==========================================================================
    # Part 5. Public Properties
    # ==========================================================================

    @property
    def stream(self) -> TextIO:
        """Return the configured output stream."""

        return self._stream

    @property
    def separator(self) -> str:
        """Return the configured separator."""

        return self._separator

    @property
    def prefix(self) -> str:
        """Return the configured prefix."""

        return self._prefix

    @property
    def suffix(self) -> str:
        """Return the configured suffix."""

        return self._suffix

    @property
    def auto_flush(self) -> bool:
        """Return whether writes are automatically flushed."""

        return self._auto_flush

    @property
    def bytes_written(self) -> int:
        """Return total UTF-8 bytes written."""

        return self._bytes_written

    @property
    def lines_written(self) -> int:
        """Return total newline characters written."""

        return self._lines_written

    @property
    def objects_exported(self) -> int:
        """Return number of objects written to the stream."""

        return self._objects_exported

    @property
    def average_size(self) -> float:
        """Return average UTF-8 byte size per write."""

        if self._objects_exported == 0:
            return 0.0

        return (
            self._bytes_written
            / self._objects_exported
        )

    @property
    def last_output(self) -> Optional[str]:
        """Return the last formatted output."""

        return self._last_output

    @property
    def last_output_time(self) -> Optional[float]:
        """Return timestamp of the last write."""

        return self._last_output_time

    @property
    def version(self) -> str:
        """Return exporter implementation version."""

        return self._version

    # ==========================================================================
    # Part 6. Validation
    # ==========================================================================

    def _validate_stream_object(
        self,
        stream: Any,
    ) -> None:
        """Validate a stream object."""

        _validate_stream(stream)

    def _validate_configuration(self) -> None:
        """Validate stdout-specific configuration."""

        self._validate_stream_object(self._stream)

        if not isinstance(self._separator, str):
            raise TypeError("separator must be a string")

        if not isinstance(self._prefix, str):
            raise TypeError("prefix must be a string")

        if not isinstance(self._suffix, str):
            raise TypeError("suffix must be a string")

        if not isinstance(self._auto_flush, bool):
            raise TypeError("auto_flush must be a bool")

    def validate(self) -> None:
        """
        Validate base and stdout-specific configuration.

        This method is safe during ``Exporter.__init__`` because all
        stdout-specific state is initialized before ``super().__init__``.
        """

        super().validate()
        self._validate_configuration()

    def validate_stream(self) -> bool:
        """Return whether the configured stream is valid."""

        try:
            self._validate_stream_object(self._stream)
        except (TypeError, ValueError):
            return False

        return True

    def validate_output(
        self,
        output: Any,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate formatted output.

        Parameters
        ----------
        output:
            Value that should be written to the stream.

        raise_error:
            If true, raise ``TypeError`` instead of returning false.
        """

        if isinstance(output, str):
            return True

        if raise_error:
            raise TypeError("output must be a string")

        return False

    def validate_payload(
        self,
        payload: ExportPayload | dict[str, Any],
    ) -> bool:
        """
        Validate a stdout payload.

        Mapping payloads are accepted by the base exporter contract.
        """

        try:
            super().validate_payload(payload)
        except (TypeError, ValueError):
            return False

        return True

    # ==========================================================================
    # Part 7. Formatting / Serialization
    # ==========================================================================

    def format_string(self, obj: Any) -> str:
        """
        Format an arbitrary Python object as stdout text.

        ``Exporter.format`` is reserved for the stable
        :class:`ExportFormat` property and therefore must not be
        overridden by a formatting method.
        """

        if isinstance(obj, str):
            text = obj
        else:
            text = repr(obj)

        return (
            f"{self._prefix}"
            f"{text}"
            f"{self._suffix}"
        )


    def serialize(
        self,
        payload: Any,
        *,
        options: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Serialize a value for stdout.

        Parameters
        ----------
        payload:
            Object to serialize.
        options:
            Optional serialization options supplied by the base
            exporter pipeline. Stdout formatting is controlled by
            the exporter instance, so these options are currently
            accepted for interface compatibility but do not override
            exporter state.
        """

        return self.format_string(payload)


    def deserialize(self, payload: str) -> str:
        """
        Return stdout text unchanged.
        """

        if not isinstance(payload, str):
            raise TypeError("payload must be a string")

        return payload


    def encode(self, obj: Any) -> str:
        """
        Encode an object as stdout text.
        """

        return self.format_string(obj)


    def decode(self, payload: str) -> str:
        """
        Decode stdout text.
        """

        return self.deserialize(payload)

    # ==========================================================================
    # Part 8. Low-Level Writing
    # ==========================================================================

    def write_stream(
        self,
        payload: str,
        stream: Optional[TextIO] = None,
    ) -> int:
        """
        Write text to a stream.

        Returns UTF-8 byte count represented by the payload.
        """

        self.validate_output(
            payload,
            raise_error=True,
        )

        target = (
            stream
            if stream is not None
            else self._stream
        )

        self._validate_stream_object(target)

        with self._stdout_lock:
            target.write(payload)

            if self._auto_flush:
                flush = getattr(target, "flush", None)

                if callable(flush):
                    flush()

            byte_count = len(
                payload.encode(self.encoding)
            )

            self._bytes_written += byte_count
            self._lines_written += payload.count("\n")
            self._objects_exported += 1

            self._last_output = payload
            self._last_output_time = time.time()

            return byte_count

    def write(self, payload: str) -> int:
        """Write to the configured stream."""

        return self.write_stream(
            payload,
            self._stream,
        )

    def write_stdout(self, payload: str) -> int:
        """Write directly to current ``sys.stdout``."""

        return self.write_stream(
            payload,
            sys.stdout,
        )

    def writeln(self, value: Any) -> int:
        """Write one logical line."""

        output = self.format_string(value)

        if not output.endswith("\n"):
            output += "\n"

        return self.write(output)

    def flush(self) -> "StdoutExporter":
        """Flush the configured stream."""

        if self.closed:
            return self

        flush = getattr(self._stream, "flush", None)

        if callable(flush):
            flush()

        return self

    # ==========================================================================
    # Part 9. Export Hook
    # ==========================================================================

    def _export(
        self,
        payload: ExportPayload,
        *,
        serialized: Any,
        options: dict[str, Any],
    ) -> Any:
        """
        Write serialized output.

        Base ``Exporter.export()`` owns export statistics.
        Stdout-specific statistics are updated here.
        """

        if not isinstance(serialized, str):
            raise TypeError(
                "StdoutExporter requires string serialization"
            )

        self.write(serialized)

        return serialized

    # ==========================================================================
    # Part 10. Convenience Export API
    # ==========================================================================

    def export_payload(
        self,
        payload: ExportPayload,
    ) -> ExportResult:
        """Export an ExportPayload."""

        return self.export(payload)

    def export_text(
        self,
        text: str,
    ) -> ExportResult:
        """Export plain text without a payload-name prefix."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        output = self.format_string(text)

        return self._export_direct_text(output)

    def _export_direct_text(
        self,
        output: str,
    ) -> ExportResult:
        """
        Export already-formatted text through the base accounting path.

        This is intentionally separate from ``Exporter.export`` because
        ``export_text`` represents raw text rather than an observability
        payload.
        """

        started = time.perf_counter()

        try:
            if self.closed:
                raise RuntimeError(
                    f"exporter '{self.name}' is closed"
                )

            if not self.enabled:
                return ExportResult(
                    success=False,
                    exporter=self.name,
                    count=0,
                    duration=(
                        time.perf_counter()
                        - started
                    ),
                    error="exporter is disabled",
                )

            written = self.write(output)

            # Keep generic exporter accounting consistent with a normal
            # successful export operation.
            self._export_count += 1
            self._success_count += 1
            self._bytes_exported += written
            self._last_export = time.time()
            self._last_error = None

            return ExportResult(
                success=True,
                exporter=self.name,
                count=1,
                bytes_exported=written,
                duration=(
                    time.perf_counter()
                    - started
                ),
                data=output,
            )

        except Exception as exc:
            self._record_error(exc)

            return ExportResult(
                success=False,
                exporter=self.name,
                count=0,
                duration=(
                    time.perf_counter()
                    - started
                ),
                error=str(exc),
            )

    def export_object(
        self,
        obj: Any,
    ) -> ExportResult:
        """Export an arbitrary object."""

        return self.export_text(
            repr(obj)
            if not isinstance(obj, str)
            else obj
        )

    def export_dict(
        self,
        data: dict[str, Any],
    ) -> ExportResult:
        """Export a dictionary as text."""

        return self.export_object(data)

    def export_list(
        self,
        data: list[Any],
    ) -> ExportResult:
        """Export a list as text."""

        return self.export_object(data)

    # ==========================================================================
    # Part 11. Configuration
    # ==========================================================================

    def set_stream(
        self,
        stream: TextIO,
    ) -> "StdoutExporter":
        """Set the output stream."""

        _validate_stream(stream)

        self._stream = stream

        return self

    def set_separator(
        self,
        separator: str,
    ) -> "StdoutExporter":
        """Set the separator."""

        if not isinstance(separator, str):
            raise TypeError(
                "separator must be a string"
            )

        self._separator = separator
        self._sync_base_options()

        return self

    def set_prefix(
        self,
        prefix: str,
    ) -> "StdoutExporter":
        """Set the output prefix."""

        if not isinstance(prefix, str):
            raise TypeError(
                "prefix must be a string"
            )

        self._prefix = prefix
        self._sync_base_options()

        return self

    def set_suffix(
        self,
        suffix: str,
    ) -> "StdoutExporter":
        """Set the output suffix."""

        if not isinstance(suffix, str):
            raise TypeError(
                "suffix must be a string"
            )

        self._suffix = suffix
        self._sync_base_options()

        return self

    def set_auto_flush(
        self,
        enabled: bool,
    ) -> "StdoutExporter":
        """Enable or disable automatic flushing."""

        if not isinstance(enabled, bool):
            raise TypeError(
                "auto_flush must be a bool"
            )

        self._auto_flush = enabled
        self._sync_base_options()

        return self

    def _sync_base_options(self) -> None:
        """Synchronize stdout options into the base exporter."""

        self._options.update(
            {
                "separator": self._separator,
                "prefix": self._prefix,
                "suffix": self._suffix,
                "auto_flush": self._auto_flush,
            }
        )

    def options_dict(self) -> dict[str, Any]:
        """Return stdout-specific configuration."""

        return {
            "stream": type(self._stream).__name__,
            "separator": self._separator,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "auto_flush": self._auto_flush,
        }

    # ==========================================================================
    # Part 12. Statistics
    # ==========================================================================

    def clear_statistics(self) -> "StdoutExporter":
        """Clear stdout-specific statistics."""

        with self._stdout_lock:
            self._bytes_written = 0
            self._lines_written = 0
            self._objects_exported = 0
            self._last_output = None
            self._last_output_time = None

        return self

    def clear(self) -> "StdoutExporter":
        """
        Clear stdout-specific statistics without touching stream content.
        """

        self.clear_statistics()

        return self

    def reset_stdout(self) -> "StdoutExporter":
        """
        Reset stdout-specific configuration and statistics.
        """

        if self.closed:
            raise RuntimeError(
                "cannot reset a closed exporter"
            )

        self._stream = DEFAULT_STREAM
        self._separator = DEFAULT_SEPARATOR
        self._prefix = DEFAULT_PREFIX
        self._suffix = DEFAULT_SUFFIX
        self._auto_flush = DEFAULT_AUTO_FLUSH

        self._sync_base_options()
        self.clear_statistics()

        return self

    # ==========================================================================
    # Part 13. Snapshot / Restore
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a serializable stdout state snapshot.

        The actual stream object is never serialized.
        """

        return {
            "version": self._version,
            "format": self.format.value,
            "stdout": {
                "separator": self._separator,
                "prefix": self._prefix,
                "suffix": self._suffix,
                "auto_flush": self._auto_flush,
                "bytes_written": self._bytes_written,
                "lines_written": self._lines_written,
                "objects_exported": self._objects_exported,
                "last_output": self._last_output,
                "last_output_time": self._last_output_time,
                "stream": type(self._stream).__name__,
            },
        }

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "StdoutExporter":
        """
        Restore stdout state.

        The current stream is intentionally preserved.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        state = snapshot.get("stdout")

        if not isinstance(state, dict):
            raise ValueError(
                "snapshot must contain a 'stdout' mapping"
            )

        self._separator = state.get(
            "separator",
            DEFAULT_SEPARATOR,
        )

        self._prefix = state.get(
            "prefix",
            DEFAULT_PREFIX,
        )

        self._suffix = state.get(
            "suffix",
            DEFAULT_SUFFIX,
        )

        self._auto_flush = state.get(
            "auto_flush",
            DEFAULT_AUTO_FLUSH,
        )

        self._bytes_written = int(
            state.get("bytes_written", 0)
        )

        self._lines_written = int(
            state.get("lines_written", 0)
        )

        self._objects_exported = int(
            state.get("objects_exported", 0)
        )

        self._last_output = state.get(
            "last_output"
        )

        self._last_output_time = state.get(
            "last_output_time"
        )

        self._sync_base_options()

        # IMPORTANT:
        # Do not restore "stream".
        #
        # The current stream belongs to the current exporter instance.
        return self

    # ==========================================================================
    # Part 14. Diagnostics
    # ==========================================================================

    def report(self) -> dict[str, Any]:
        """Return a detailed stdout report."""

        return {
            "name": self.name,
            "format": self.format.value,
            "version": self.version,
            "stdout": {
                "stream": type(self._stream).__name__,
                "bytes_written": self._bytes_written,
                "lines_written": self._lines_written,
                "objects_exported": self._objects_exported,
                "average_size": self.average_size,
                "last_output": self._last_output,
                "last_output_time": self._last_output_time,
                "separator": self._separator,
                "prefix": self._prefix,
                "suffix": self._suffix,
                "auto_flush": self._auto_flush,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        """Return combined base and stdout diagnostics."""

        result = super().diagnostics()

        result["stdout"] = {
            "stream": type(self._stream).__name__,
            "valid_stream": self.validate_stream(),
            "bytes_written": self._bytes_written,
            "lines_written": self._lines_written,
            "objects_exported": self._objects_exported,
            "average_size": self.average_size,
            "last_output": self._last_output,
            "last_output_time": self._last_output_time,
            "separator": self._separator,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "auto_flush": self._auto_flush,
        }

        return result

    # ==========================================================================
    # Part 15. Lifecycle
    # ==========================================================================

    def cleanup(self) -> "StdoutExporter":
        """
        Cleanup transient stdout state.

        Configuration and stream ownership are preserved.
        """

        self._last_output = None
        self._last_output_time = None

        return self

    def close(self) -> "StdoutExporter":
        """
        Close the exporter.

        ``sys.stdout`` and ``sys.stderr`` are never closed.

        Custom streams are closed.
        """

        if self.closed:
            return self

        self.flush()

        target = self._stream

        super().close()

        if target not in (
            sys.stdout,
            sys.stderr,
        ):
            close = getattr(target, "close", None)

            if callable(close):
                close()

        return self

    # ==========================================================================
    # Part 16. Python Protocols
    # ==========================================================================

    def __len__(self) -> int:
        """Return stdout-specific object count."""

        return self._objects_exported

    def __call__(
        self,
        obj: Any,
    ) -> ExportResult:
        """Export an arbitrary object."""

        return self.export_object(obj)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"format={self.format.value!r}, "
            f"stream={type(self._stream).__name__!r}, "
            f"auto_flush={self._auto_flush!r}, "
            f"prefix={self._prefix!r}, "
            f"suffix={self._suffix!r}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"[STDOUT] -> "
            f"{type(self._stream).__name__}"
        )

    def __copy__(self) -> "StdoutExporter":
        return type(self)(
            name=self.name,
            stream=self._stream,
            encoding=self.encoding,
            enabled=self.enabled,
            options=StdoutExportOptions(
                stream=self._stream,
                separator=self._separator,
                prefix=self._prefix,
                suffix=self._suffix,
                auto_flush=self._auto_flush,
            ),
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "StdoutExporter":

        cls = type(self)
        result = cls.__new__(cls)

        memo[id(self)] = result

        for key, value in self.__dict__.items():
            if key == "_stdout_lock":
                setattr(
                    result,
                    key,
                    threading.RLock(),
                )
            elif key == "_stream":
                # Streams are external resources.
                setattr(result, key, value)
            else:
                setattr(
                    result,
                    key,
                    copy.deepcopy(value, memo),
                )

        return result


# ==============================================================================
# Part 17. Public API
# ==============================================================================

__all__ = [
    "DEFAULT_AUTO_FLUSH",
    "DEFAULT_PREFIX",
    "DEFAULT_SEPARATOR",
    "DEFAULT_STREAM",
    "STDOUT_EXPORTER_VERSION",
    "StdoutExportOptions",
    "StdoutExporter",
]