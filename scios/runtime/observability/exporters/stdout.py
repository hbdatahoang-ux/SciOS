"""
SciOS-NG
Runtime Observability

Stdout Exporter

File:
    scios/runtime/observability/exporters/stdout.py

Part 1. Foundation
"""

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import io
import sys
import threading
import time

from dataclasses import dataclass
from typing import Any, Optional, TextIO

from .base import (
    BaseExporter,
    ExportCapability,
    ExportDestination,
    ExportFormat,
    ExportMode,
)

# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_STREAM: TextIO = sys.stdout

DEFAULT_SEPARATOR: str = " "

DEFAULT_PREFIX: str = ""

DEFAULT_SUFFIX: str = "\n"

DEFAULT_AUTO_FLUSH: bool = True

STDOUT_EXPORTER_VERSION: str = "0.1.0"

# ==============================================================================
# Stdout Export Options
# ==============================================================================


@dataclass(slots=True)
class StdoutExportOptions:
    """
    Configuration options for StdoutExporter.
    """

    stream: TextIO = DEFAULT_STREAM

    separator: str = DEFAULT_SEPARATOR

    prefix: str = DEFAULT_PREFIX

    suffix: str = DEFAULT_SUFFIX

    auto_flush: bool = DEFAULT_AUTO_FLUSH


# ==============================================================================
# Stdout Exporter
# ==============================================================================


class StdoutExporter(BaseExporter):
    """
    Export observability records to stdout or a text stream.
    """

    def __init__(
        self,
        name: str = "StdoutExporter",
        *,
        stream: TextIO = DEFAULT_STREAM,
        mode: ExportMode = ExportMode.SYNC,
        options: Optional[StdoutExportOptions] = None,
    ) -> None:

        super().__init__(
            name=name,
            exporter_format=ExportFormat.STDOUT,
            destination=stream,
            mode=mode,
        )

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._name = name

        self._exporter_type = "StdoutExporter"

        self._version = STDOUT_EXPORTER_VERSION

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._stdout = options or StdoutExportOptions(stream=stream)

        self._stream = self._stdout.stream

        self._separator = self._stdout.separator

        self._prefix = self._stdout.prefix

        self._suffix = self._stdout.suffix

        self._auto_flush = self._stdout.auto_flush

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._bytes_written: int = 0

        self._lines_written: int = 0

        self._objects_exported: int = 0

        self._last_output: Optional[str] = None

        self._last_export: Optional[float] = None

        self._lock = threading.RLock()

        self._metadata.update(
            {
                "format": "stdout",
                "stream": type(self._stream).__name__,
            }
        )

        self._capabilities |= (
            ExportCapability.SERIALIZATION
            | ExportCapability.STREAMING
        )
# ==============================================================================
# Part 2. Serialization
# ==============================================================================

    def serialize(
        self,
        record: ExportRecord,
    ) -> str:
        """
        Serialize an ExportRecord into text.
        """

        return self.format(
            {
                "id": record.id,
                "timestamp": record.timestamp,
                "payload": record.payload,
                "metadata": record.metadata,
                "tags": record.tags,
                "source": record.source,
            }
        )

    # ------------------------------------------------------------------

    def deserialize(
        self,
        payload: str,
    ) -> ExportRecord:
        """
        Convert text back into an ExportRecord.

        Since stdout output is plain text, the original object
        cannot always be reconstructed. The text is therefore
        stored in the payload field.
        """

        return ExportRecord(
            payload=payload,
            source="stdout",
        )

    # ------------------------------------------------------------------

    def format(
        self,
        obj: Any,
    ) -> str:
        """
        Format an object into printable text.
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

    # ------------------------------------------------------------------

    def encode(
        self,
        obj: Any,
    ) -> str:
        """
        Encode a Python object as text.
        """

        return self.format(obj)

    # ------------------------------------------------------------------

    def decode(
        self,
        payload: str,
    ) -> str:
        """
        Decode text.

        Plain text requires no decoding.
        """

        return payload

    # ------------------------------------------------------------------

    def validate_output(
        self,
        payload: Any,
    ) -> bool:
        """
        Validate whether the object can be printed.
        """

        try:
            self.format(payload)
            return True

        except Exception:
            return False
# ==============================================================================
# Part 3. Writing API
# ==============================================================================

    def write(
        self,
        payload: str,
    ) -> int:
        """
        Write text to the configured output stream.

        Returns
        -------
        int
            Number of bytes written.
        """

        if self._stream is sys.stdout:
            return self.write_stdout(payload)

        return self.write_stream(payload, self._stream)

    # ------------------------------------------------------------------

    def write_stdout(
        self,
        payload: str,
    ) -> int:
        """
        Write directly to stdout.
        """

        return self.write_stream(
            payload,
            sys.stdout,
        )

    # ------------------------------------------------------------------

    def write_stream(
        self,
        payload: str,
        stream: TextIO,
    ) -> int:
        """
        Write text to a text stream.
        """

        with self._lock:

            stream.write(payload)

            if self._auto_flush:
                stream.flush()

            written = len(payload.encode("utf-8"))

            self._bytes_written += written
            self._lines_written += payload.count("\n")
            self._objects_exported += 1

            self._last_output = payload
            self._last_export = time.time()

            return written

    # ------------------------------------------------------------------

    def writeln(
        self,
        text: Any,
    ) -> int:
        """
        Write one line.
        """

        payload = self.format(text)

        if not payload.endswith("\n"):
            payload += "\n"

        return self.write(payload)

    # ------------------------------------------------------------------

    def flush(self) -> None:
        """
        Flush the configured stream.
        """

        if hasattr(self._stream, "flush"):
            self._stream.flush()

    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Clear runtime state.

        Does not clear terminal output.
        """

        self._bytes_written = 0

        self._lines_written = 0

        self._objects_exported = 0

        self._last_output = None

        self._last_export = None

        self._history.clear()

        self._cache.clear()

    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Close the configured stream.

        Standard streams (stdout/stderr) are never closed.
        """

        if self._stream in (
            sys.stdout,
            sys.stderr,
        ):
            return

        if hasattr(self._stream, "close"):
            self._stream.close()
# ==============================================================================
# Part 4. Export API
# ==============================================================================

    def export(
        self,
        record: ExportRecord,
    ) -> ExportResult:
        """
        Export a single record.
        """

        return super().export(record)

    # ------------------------------------------------------------------

    def export_batch(
        self,
        records: Sequence[ExportRecord],
    ) -> List[ExportResult]:
        """
        Export multiple records.
        """

        return [self.export(record) for record in records]

    # ------------------------------------------------------------------

    def export_record(
        self,
        record: ExportRecord,
    ) -> ExportResult:
        """
        Export an ExportRecord.
        """

        return self.export(record)

    # ------------------------------------------------------------------

    def export_dict(
        self,
        data: Dict[str, Any],
    ) -> ExportResult:
        """
        Export a dictionary.
        """

        return self.export(
            ExportRecord(
                payload=data,
                source="dict",
            )
        )

    # ------------------------------------------------------------------

    def export_list(
        self,
        data: List[Any],
    ) -> ExportResult:
        """
        Export a list.
        """

        return self.export(
            ExportRecord(
                payload=data,
                source="list",
            )
        )

    # ------------------------------------------------------------------

    def export_object(
        self,
        obj: Any,
    ) -> ExportResult:
        """
        Export an arbitrary Python object.
        """

        return self.export(
            ExportRecord(
                payload=obj,
                source=type(obj).__name__,
            )
        )

    # ------------------------------------------------------------------

    def export_text(
        self,
        text: str,
    ) -> ExportResult:
        """
        Export plain text.
        """

        return self.export(
            ExportRecord(
                payload=text,
                source="text",
            )
        )
# ==============================================================================
# Part 5. Configuration
# ==============================================================================

    def set_stream(
        self,
        stream: TextIO,
    ) -> "StdoutExporter":
        """
        Set the output stream.
        """

        if not hasattr(stream, "write"):
            raise TypeError(
                "stream must provide a write() method"
            )

        self._stream = stream
        self._destination = stream

        return self

    # ------------------------------------------------------------------

    def set_separator(
        self,
        separator: str,
    ) -> "StdoutExporter":
        """
        Set the separator used for batch output.
        """

        self._separator = str(separator)

        return self

    # ------------------------------------------------------------------

    def set_prefix(
        self,
        prefix: str,
    ) -> "StdoutExporter":
        """
        Set the output prefix.
        """

        self._prefix = str(prefix)

        return self

    # ------------------------------------------------------------------

    def set_suffix(
        self,
        suffix: str,
    ) -> "StdoutExporter":
        """
        Set the output suffix.
        """

        self._suffix = str(suffix)

        return self

    # ------------------------------------------------------------------

    def set_auto_flush(
        self,
        enabled: bool,
    ) -> "StdoutExporter":
        """
        Enable or disable automatic flushing.
        """

        self._auto_flush = bool(enabled)

        return self

    # ------------------------------------------------------------------

    def options(self) -> Dict[str, Any]:
        """
        Return the current stdout configuration.
        """

        return {
            "stream": type(self._stream).__name__,
            "separator": self._separator,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "auto_flush": self._auto_flush,
        }

    # ------------------------------------------------------------------

    def reset(self) -> "StdoutExporter":
        """
        Restore the default stdout configuration.
        """

        self._stream = DEFAULT_STREAM
        self._destination = DEFAULT_STREAM

        self._separator = DEFAULT_SEPARATOR
        self._prefix = DEFAULT_PREFIX
        self._suffix = DEFAULT_SUFFIX

        self._auto_flush = DEFAULT_AUTO_FLUSH

        return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a runtime snapshot of the stdout exporter.
        """

        state = super().snapshot()

        state["stdout"] = {
            "separator": self._separator,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "auto_flush": self._auto_flush,
            "bytes_written": self._bytes_written,
            "lines_written": self._lines_written,
            "objects_exported": self._objects_exported,
            "last_output": self._last_output,
            "last_export": self._last_export,
            "stream": type(self._stream).__name__,
        }

        return state

    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "StdoutExporter":
        """
        Restore exporter state from snapshot.
        """

        super().restore(snapshot)

        state = snapshot.get("stdout", {})

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

        self._bytes_written = state.get(
            "bytes_written",
            0,
        )

        self._lines_written = state.get(
            "lines_written",
            0,
        )

        self._objects_exported = state.get(
            "objects_exported",
            0,
        )

        self._last_output = state.get(
            "last_output",
        )

        self._last_export = state.get(
            "last_export",
        )

        #
        # Stream objects themselves are not restored.
        # Keep the currently configured stream.
        #

        return self

    # ------------------------------------------------------------------

    def clone(self) -> "StdoutExporter":
        """
        Create a deep clone.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def copy(self) -> "StdoutExporter":
        """
        Create a shallow copy.
        """

        return copy.copy(self)

    # ------------------------------------------------------------------

    def cleanup(self) -> "StdoutExporter":
        """
        Cleanup transient runtime state.
        """

        super().cleanup()

        self._last_output = None

        self._last_export = None

        return self

    # ------------------------------------------------------------------

    def compact(self) -> "StdoutExporter":
        """
        Compact runtime memory usage.
        """

        super().compact()

        #
        # Keep only the latest exported record.
        #

        if len(self._history) > 1:
            self._history[:] = self._history[-1:]

        return self
# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    @property
    def bytes_written(self) -> int:
        """
        Total bytes written to the output stream.
        """

        return self._bytes_written

    # ------------------------------------------------------------------

    @property
    def lines_written(self) -> int:
        """
        Total lines written.
        """

        return self._lines_written

    # ------------------------------------------------------------------

    @property
    def objects_exported(self) -> int:
        """
        Total exported objects.
        """

        return self._objects_exported

    # ------------------------------------------------------------------

    @property
    def average_size(self) -> float:
        """
        Average number of bytes per exported object.
        """

        if self._objects_exported == 0:
            return 0.0

        return (
            self._bytes_written
            / self._objects_exported
        )

    # ------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Return a detailed stdout exporter report.
        """

        report = super().report()

        report["stdout"] = {
            "stream": type(self._stream).__name__,
            "bytes_written": self.bytes_written,
            "lines_written": self.lines_written,
            "objects_exported": self.objects_exported,
            "average_size": self.average_size,
            "last_output": self._last_output,
            "last_export": self._last_export,
            "auto_flush": self._auto_flush,
            "prefix": self._prefix,
            "suffix": self._suffix,
            "separator": self._separator,
        }

        return report

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a concise stdout exporter summary.
        """

        summary = super().summary()

        summary.update(
            {
                "bytes_written": self.bytes_written,
                "lines_written": self.lines_written,
                "objects_exported": self.objects_exported,
                "average_size": round(
                    self.average_size,
                    2,
                ),
            }
        )

        return summary
# ==============================================================================
# Part 8. Validation
# ==============================================================================

    def validate(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the stdout exporter.
        """

        try:
            super().validate(raise_error=True)

            self.validate_stream(raise_error=True)

            self.check_integrity(raise_error=True)

            return True

        except Exception:
            if raise_error:
                raise
            return False

    # ------------------------------------------------------------------

    def validate_stream(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the configured output stream.
        """

        try:

            if self._stream is None:
                raise ValueError(
                    "output stream is None"
                )

            if not hasattr(self._stream, "write"):
                raise TypeError(
                    "stream must implement write()"
                )

            if not callable(self._stream.write):
                raise TypeError(
                    "stream.write is not callable"
                )

            return True

        except Exception:
            if raise_error:
                raise
            return False

    # ------------------------------------------------------------------

    def validate_output(
        self,
        output: str,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate formatted output text.
        """

        try:

            if not isinstance(output, str):
                raise TypeError(
                    "output must be a string"
                )

            return True

        except Exception:
            if raise_error:
                raise
            return False

    # ------------------------------------------------------------------

    def validate_payload(
        self,
        payload: Any,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate whether a payload can be formatted.
        """

        try:

            self.format(payload)

            return True

        except Exception:
            if raise_error:
                raise ValueError(
                    "payload cannot be formatted"
                )

            return False

    # ------------------------------------------------------------------

    def check_integrity(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Check internal stdout exporter integrity.
        """

        try:

            super().check_integrity(raise_error=True)

            if not isinstance(
                self._separator,
                str,
            ):
                raise TypeError(
                    "separator must be a string"
                )

            if not isinstance(
                self._prefix,
                str,
            ):
                raise TypeError(
                    "prefix must be a string"
                )

            if not isinstance(
                self._suffix,
                str,
            ):
                raise TypeError(
                    "suffix must be a string"
                )

            if not isinstance(
                self._auto_flush,
                bool,
            ):
                raise TypeError(
                    "auto_flush must be a boolean"
                )

            return True

        except Exception:
            if raise_error:
                raise
            return False
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================

    def before_format(
        self,
        payload: Any,
    ) -> Any:
        """
        Hook executed before formatting.
        """

        self.emit_event(
            "before_format",
            payload,
        )

        return payload

    # ------------------------------------------------------------------

    def after_format(
        self,
        output: str,
    ) -> str:
        """
        Hook executed after formatting.
        """

        self.emit_event(
            "after_format",
            output,
        )

        return output

    # ------------------------------------------------------------------

    def before_write(
        self,
        output: str,
    ) -> str:
        """
        Hook executed before writing to the output stream.
        """

        self.emit_event(
            "before_write",
            output,
        )

        return output

    # ------------------------------------------------------------------

    def after_write(
        self,
        output: str,
        bytes_written: int,
    ) -> int:
        """
        Hook executed after writing to the output stream.
        """

        self.emit_event(
            "after_write",
            output,
            bytes_written,
        )

        return bytes_written

    # ------------------------------------------------------------------

    def before_export(
        self,
        record: ExportRecord,
    ) -> ExportRecord:
        """
        Hook executed before exporting.
        """

        super().before_export(record)

        self.emit_event(
            "before_stdout_export",
            record,
        )

        return record

    # ------------------------------------------------------------------

    def after_export(
        self,
        record: ExportRecord,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook executed after exporting.
        """

        super().after_export(
            record,
            result,
        )

        self.emit_event(
            "after_stdout_export",
            record,
            result,
        )

        return result

    # ------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Emit a stdout exporter event.

        Delegates to BaseExporter.
        """

        super().emit_event(
            event,
            *args,
            **kwargs,
        )
# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"stream={type(self._stream).__name__!r}, "
            f"auto_flush={self._auto_flush}, "
            f"prefix={self._prefix!r}, "
            f"suffix={self._suffix!r}, "
            f"status={self._status.value!r})"
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name} "
            f"[STDOUT] -> "
            f"{type(self._stream).__name__}"
        )

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of exported objects.
        """

        return self._objects_exported

    # ------------------------------------------------------------------

    def __call__(
        self,
        obj: Any,
    ) -> ExportResult:
        """
        Export an object.
        """

        return self.export_object(obj)

    # ------------------------------------------------------------------

    def __copy__(self) -> "StdoutExporter":
        """
        Create a shallow copy.
        """

        return self.copy()

    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "StdoutExporter":
        """
        Create a deep copy.
        """

        return self.clone()                                                                                    