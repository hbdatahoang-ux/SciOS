"""
SciOS-NG
Runtime Observability

JSON Exporter

File:
    scios/runtime/observability/exporters/json.py

Part 1. Foundation
"""

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import json
import threading
import time
import uuid

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

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

DEFAULT_JSON_INDENT: int = 2

DEFAULT_JSON_ENCODING: str = "utf-8"

DEFAULT_JSON_ASCII: bool = False

DEFAULT_JSON_SORT_KEYS: bool = False

DEFAULT_JSON_COMPACT: bool = False

DEFAULT_JSON_APPEND: bool = False

DEFAULT_JSON_FILENAME: str = "metrics.json"

JSON_EXPORTER_VERSION: str = "0.1.0"

# ==============================================================================
# JSON Encoder
# ==============================================================================


class JSONEncoder(json.JSONEncoder):
    """
    Default JSON encoder for SciOS-NG.

    Handles common runtime objects that are not directly
    serializable by the standard json module.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Path):
            return str(obj)

        if isinstance(obj, uuid.UUID):
            return str(obj)

        if hasattr(obj, "__dict__"):
            return obj.__dict__

        return super().default(obj)


# ==============================================================================
# JSON Export Options
# ==============================================================================


@dataclass(slots=True)
class JSONExportOptions:
    """
    Configuration options for JSONExporter.
    """

    indent: int = DEFAULT_JSON_INDENT

    encoding: str = DEFAULT_JSON_ENCODING

    ensure_ascii: bool = DEFAULT_JSON_ASCII

    sort_keys: bool = DEFAULT_JSON_SORT_KEYS

    compact: bool = DEFAULT_JSON_COMPACT

    append: bool = DEFAULT_JSON_APPEND

    encoder: type[json.JSONEncoder] = JSONEncoder


# ==============================================================================
# JSON Exporter
# ==============================================================================


class JSONExporter(BaseExporter):
    """
    JSON implementation of BaseExporter.
    """

    def __init__(
        self,
        name: str = "JSONExporter",
        *,
        destination: ExportDestination = DEFAULT_JSON_FILENAME,
        mode: ExportMode = ExportMode.SYNC,
        options: Optional[JSONExportOptions] = None,
    ) -> None:

        super().__init__(
            name=name,
            exporter_format=ExportFormat.JSON,
            destination=destination,
            mode=mode,
        )

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._name = name

        self._exporter_type = "JSONExporter"

        self._version = JSON_EXPORTER_VERSION

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._json = options or JSONExportOptions()

        self._encoding = self._json.encoding

        self._indent = self._json.indent

        self._ensure_ascii = self._json.ensure_ascii

        self._sort_keys = self._json.sort_keys

        self._compact = self._json.compact

        self._append = self._json.append

        self._encoder = self._json.encoder

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._bytes_written: int = 0

        self._files_written: int = 0

        self._objects_exported: int = 0

        self._last_path: Optional[Union[str, Path]] = None

        self._last_export: Optional[float] = None

        self._lock = threading.RLock()

        self._metadata.update(
            {
                "format": "json",
                "encoding": self._encoding,
            }
        )

        self._capabilities |= (
            ExportCapability.SERIALIZATION
            | ExportCapability.DESERIALIZATION
        )
# ==============================================================================
# Part 2. Serialization
# ==============================================================================

    def serialize(
        self,
        record: ExportRecord,
    ) -> str:
        """
        Serialize an ExportRecord into a JSON string.
        """

        return self.encode(
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
        Deserialize a JSON string into an ExportRecord.
        """

        data = self.decode(payload)

        return ExportRecord(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", time.time()),
            payload=data.get("payload"),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            source=data.get("source", ""),
        )

    # ------------------------------------------------------------------

    def encode(
        self,
        obj: Any,
    ) -> str:
        """
        Encode a Python object as JSON.
        """

        if self._compact:
            indent = None
            separators = (",", ":")
        else:
            indent = self._indent
            separators = None

        return json.dumps(
            obj,
            cls=self._encoder,
            indent=indent,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self._sort_keys,
            separators=separators,
        )

    # ------------------------------------------------------------------

    def decode(
        self,
        payload: str,
    ) -> Any:
        """
        Decode JSON into a Python object.
        """

        return json.loads(payload)

    # ------------------------------------------------------------------

    def pretty(
        self,
        obj: Any,
    ) -> str:
        """
        Return formatted JSON.
        """

        return json.dumps(
            obj,
            cls=self._encoder,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self._sort_keys,
        )

    # ------------------------------------------------------------------

    def compact(
        self,
        obj: Any,
    ) -> str:
        """
        Return compact JSON.
        """

        return json.dumps(
            obj,
            cls=self._encoder,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self._sort_keys,
            separators=(",", ":"),
        )

    # ------------------------------------------------------------------

    def validate_json(
        self,
        payload: str,
    ) -> bool:
        """
        Check whether a string is valid JSON.
        """

        try:
            json.loads(payload)
            return True

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            return False
# ==============================================================================
# Part 3. Writing API
# ==============================================================================

    def write(
        self,
        payload: str,
    ) -> int:
        """
        Write a JSON payload to the configured destination.

        Returns
        -------
        int
            Number of bytes written.
        """

        if hasattr(self._destination, "write"):
            return self.write_stream(payload, self._destination)

        return self.write_file(payload, self._destination)

    # ------------------------------------------------------------------

    def write_file(
        self,
        payload: str,
        path: ExportDestination,
    ) -> int:
        """
        Write JSON payload to a file.
        """

        path = Path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if self._append else "w"

        with path.open(
            mode,
            encoding=self._encoding,
        ) as fp:
            fp.write(payload)

            if self._append:
                fp.write("\n")

        written = len(payload.encode(self._encoding))

        self._bytes_written += written
        self._files_written += 1
        self._last_path = path
        self._last_export = time.time()

        return written

    # ------------------------------------------------------------------

    def write_stream(
        self,
        payload: str,
        stream,
    ) -> int:
        """
        Write JSON payload to a file-like stream.
        """

        stream.write(payload)

        if hasattr(stream, "flush"):
            stream.flush()

        written = len(payload.encode(self._encoding))

        self._bytes_written += written
        self._last_export = time.time()

        return written

    # ------------------------------------------------------------------

    def append(
        self,
        payload: str,
    ) -> int:
        """
        Append JSON payload to the configured destination.
        """

        previous = self._append

        try:
            self._append = True
            return self.write(payload)
        finally:
            self._append = previous

    # ------------------------------------------------------------------

    def overwrite(
        self,
        payload: str,
    ) -> int:
        """
        Overwrite the configured destination.
        """

        previous = self._append

        try:
            self._append = False
            return self.write(payload)
        finally:
            self._append = previous

    # ------------------------------------------------------------------

    def flush(self) -> None:
        """
        Flush the configured stream if supported.

        File writes are flushed automatically by the context manager.
        """

        if hasattr(self._destination, "flush"):
            self._destination.flush()

    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Clear runtime write state.

        This does not remove exported files.
        """

        self._bytes_written = 0
        self._files_written = 0
        self._objects_exported = 0

        self._last_path = None
        self._last_export = None

        self._history.clear()
        self._cache.clear()
# ==============================================================================
# Part 4. Export API
# ==============================================================================

    def export(
        self,
        record: ExportRecord,
    ) -> ExportResult:
        """
        Export a single ExportRecord.
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

    def export_dict(
        self,
        data: Dict[str, Any],
    ) -> ExportResult:
        """
        Export a dictionary as JSON.
        """

        record = ExportRecord(
            payload=data,
            source="dict",
        )

        return self.export(record)

    # ------------------------------------------------------------------

    def export_list(
        self,
        data: List[Any],
    ) -> ExportResult:
        """
        Export a list as JSON.
        """

        record = ExportRecord(
            payload=data,
            source="list",
        )

        return self.export(record)

    # ------------------------------------------------------------------

    def export_object(
        self,
        obj: Any,
    ) -> ExportResult:
        """
        Export an arbitrary Python object.
        """

        record = ExportRecord(
            payload=obj,
            source=type(obj).__name__,
        )

        return self.export(record)

    # ------------------------------------------------------------------

    def export_file(
        self,
        path: ExportDestination,
    ) -> ExportResult:
        """
        Export an existing JSON file.

        The file is validated and then re-exported to the
        current destination.
        """

        path = Path(path)

        with path.open(
            "r",
            encoding=self._encoding,
        ) as fp:
            payload = fp.read()

        if not self.validate_json(payload):
            raise ValueError(
                f"Invalid JSON file: {path}"
            )

        data = self.decode(payload)

        return self.export_object(data)

    # ------------------------------------------------------------------

    def export_string(
        self,
        payload: str,
    ) -> ExportResult:
        """
        Export a JSON string.
        """

        if not self.validate_json(payload):
            raise ValueError(
                "Invalid JSON string."
            )

        data = self.decode(payload)

        return self.export_object(data)
# ==============================================================================
# Part 5. Configuration
# ==============================================================================

    def set_indent(
        self,
        indent: int,
    ) -> "JSONExporter":
        """
        Set JSON indentation.
        """

        if indent < 0:
            raise ValueError("indent must be >= 0")

        self._indent = int(indent)

        return self

    # ------------------------------------------------------------------

    def set_encoding(
        self,
        encoding: str,
    ) -> "JSONExporter":
        """
        Set output encoding.
        """

        if not encoding:
            raise ValueError("encoding cannot be empty")

        self._encoding = encoding

        return self

    # ------------------------------------------------------------------

    def set_ascii(
        self,
        enabled: bool,
    ) -> "JSONExporter":
        """
        Enable or disable ASCII escaping.
        """

        self._ensure_ascii = bool(enabled)

        return self

    # ------------------------------------------------------------------

    def set_sort_keys(
        self,
        enabled: bool,
    ) -> "JSONExporter":
        """
        Enable or disable key sorting.
        """

        self._sort_keys = bool(enabled)

        return self

    # ------------------------------------------------------------------

    def set_compact(
        self,
        enabled: bool,
    ) -> "JSONExporter":
        """
        Enable or disable compact JSON output.
        """

        self._compact = bool(enabled)

        return self

    # ------------------------------------------------------------------

    def options(self) -> Dict[str, Any]:
        """
        Return JSON configuration.
        """

        return {
            "indent": self._indent,
            "encoding": self._encoding,
            "ensure_ascii": self._ensure_ascii,
            "sort_keys": self._sort_keys,
            "compact": self._compact,
            "append": self._append,
            "encoder": self._encoder,
        }

    # ------------------------------------------------------------------

    def reset(self) -> "JSONExporter":
        """
        Restore default JSON configuration.
        """

        self._indent = DEFAULT_JSON_INDENT

        self._encoding = DEFAULT_JSON_ENCODING

        self._ensure_ascii = DEFAULT_JSON_ASCII

        self._sort_keys = DEFAULT_JSON_SORT_KEYS

        self._compact = DEFAULT_JSON_COMPACT

        self._append = DEFAULT_JSON_APPEND

        self._encoder = JSONEncoder

        return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a runtime snapshot of the JSON exporter.
        """

        state = super().snapshot()

        state.update(
            {
                "json": {
                    "indent": self._indent,
                    "encoding": self._encoding,
                    "ensure_ascii": self._ensure_ascii,
                    "sort_keys": self._sort_keys,
                    "compact": self._compact,
                    "append": self._append,
                    "bytes_written": self._bytes_written,
                    "files_written": self._files_written,
                    "objects_exported": self._objects_exported,
                    "last_path": (
                        str(self._last_path)
                        if self._last_path is not None
                        else None
                    ),
                    "last_export": self._last_export,
                }
            }
        )

        return state

    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "JSONExporter":
        """
        Restore exporter state from snapshot.
        """

        super().restore(snapshot)

        state = snapshot.get("json", {})

        self._indent = state.get(
            "indent",
            self._indent,
        )

        self._encoding = state.get(
            "encoding",
            self._encoding,
        )

        self._ensure_ascii = state.get(
            "ensure_ascii",
            self._ensure_ascii,
        )

        self._sort_keys = state.get(
            "sort_keys",
            self._sort_keys,
        )

        self._compact = state.get(
            "compact",
            self._compact,
        )

        self._append = state.get(
            "append",
            self._append,
        )

        self._bytes_written = state.get(
            "bytes_written",
            self._bytes_written,
        )

        self._files_written = state.get(
            "files_written",
            self._files_written,
        )

        self._objects_exported = state.get(
            "objects_exported",
            self._objects_exported,
        )

        last_path = state.get("last_path")

        self._last_path = (
            Path(last_path)
            if last_path
            else None
        )

        self._last_export = state.get(
            "last_export",
            self._last_export,
        )

        return self

    # ------------------------------------------------------------------

    def clone(self) -> "JSONExporter":
        """
        Create a deep clone of this exporter.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def copy(self) -> "JSONExporter":
        """
        Create a shallow copy of this exporter.
        """

        return copy.copy(self)

    # ------------------------------------------------------------------

    def cleanup(self) -> "JSONExporter":
        """
        Cleanup transient runtime resources.
        """

        super().cleanup()

        self._last_export = None

        return self

    # ------------------------------------------------------------------

    def compact(self) -> "JSONExporter":
        """
        Compact runtime memory usage.
        """

        super().compact()

        if len(self._history) > self._batch_size:
            self._history[:] = self._history[-self._batch_size :]

        return self
# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    @property
    def bytes_written(self) -> int:
        """
        Total bytes written.
        """

        return self._bytes_written

    # ------------------------------------------------------------------

    @property
    def files_written(self) -> int:
        """
        Total files written.
        """

        return self._files_written

    # ------------------------------------------------------------------

    @property
    def objects_exported(self) -> int:
        """
        Total exported Python objects.
        """

        return self._objects_exported

    # ------------------------------------------------------------------

    @property
    def average_size(self) -> float:
        """
        Average bytes per export.
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
        Return a complete JSON exporter report.
        """

        report = super().report()

        report["json"] = {
            "encoding": self._encoding,
            "indent": self._indent,
            "compact": self._compact,
            "append": self._append,
            "bytes_written": self.bytes_written,
            "files_written": self.files_written,
            "objects_exported": self.objects_exported,
            "average_size": self.average_size,
            "last_path": (
                str(self._last_path)
                if self._last_path is not None
                else None
            ),
            "last_export": self._last_export,
        }

        return report

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a concise JSON exporter summary.
        """

        summary = super().summary()

        summary.update(
            {
                "bytes_written": self.bytes_written,
                "files_written": self.files_written,
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
        Validate the JSON exporter.
        """

        try:
            super().validate(raise_error=True)

            self.validate_path(raise_error=True)

            self.check_integrity(raise_error=True)

            return True

        except Exception:
            if raise_error:
                raise
            return False

    # ------------------------------------------------------------------

    def validate_path(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate export destination path.
        """

        try:
            if hasattr(self._destination, "write"):
                return True

            path = Path(self._destination)

            if path.exists() and path.is_dir():
                raise ValueError(
                    "destination must be a file, not a directory"
                )

            if path.parent and not path.parent.exists():
                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            return True

        except Exception:
            if raise_error:
                raise
            return False

    # ------------------------------------------------------------------

    def validate_json(
        self,
        payload: str,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate JSON text.
        """

        try:
            json.loads(payload)

            return True

        except Exception:
            if raise_error:
                raise ValueError(
                    "invalid JSON payload"
                )

            return False

    # ------------------------------------------------------------------

    def validate_payload(
        self,
        payload: Any,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate whether an object can be serialized.
        """

        try:
            json.dumps(
                payload,
                cls=self._encoder,
            )

            return True

        except Exception:
            if raise_error:
                raise ValueError(
                    "payload is not JSON serializable"
                )

            return False

    # ------------------------------------------------------------------

    def check_integrity(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Check JSON exporter internal integrity.
        """

        try:
            super().check_integrity(raise_error=True)

            if not isinstance(
                self._encoding,
                str,
            ):
                raise TypeError(
                    "invalid encoding"
                )

            if self._indent < 0:
                raise ValueError(
                    "indent must be >= 0"
                )

            if self._encoder is None:
                raise RuntimeError(
                    "JSON encoder is missing"
                )

            return True

        except Exception:
            if raise_error:
                raise
            return False
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================

    def before_encode(
        self,
        payload: Any,
    ) -> Any:
        """
        Hook executed before JSON encoding.
        """

        self.emit_event(
            "before_encode",
            payload,
        )

        return payload

    # ------------------------------------------------------------------

    def after_encode(
        self,
        payload: str,
    ) -> str:
        """
        Hook executed after JSON encoding.
        """

        self.emit_event(
            "after_encode",
            payload,
        )

        return payload

    # ------------------------------------------------------------------

    def before_write(
        self,
        payload: str,
    ) -> str:
        """
        Hook executed before writing JSON.
        """

        self.emit_event(
            "before_write",
            payload,
        )

        return payload

    # ------------------------------------------------------------------

    def after_write(
        self,
        payload: str,
        bytes_written: int,
    ) -> int:
        """
        Hook executed after writing JSON.
        """

        self.emit_event(
            "after_write",
            payload,
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
            "before_json_export",
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
            "after_json_export",
            record,
            result,
        )

        return result

    # ------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Emit a JSON exporter event.

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
            f"destination={str(self._destination)!r}, "
            f"encoding={self._encoding!r}, "
            f"indent={self._indent}, "
            f"compact={self._compact}, "
            f"status={self._status.value!r})"
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        destination = (
            str(self._destination)
            if self._destination is not None
            else "<memory>"
        )

        return (
            f"{self._name} "
            f"[JSON] -> {destination}"
        )

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of exported objects.
        """

        return self._objects_exported

    # ------------------------------------------------------------------

    def __call__(
        self,
        obj: Any,
    ) -> ExportResult:
        """
        Export an arbitrary Python object.
        """

        return self.export_object(obj)

    # ------------------------------------------------------------------

    def __copy__(self) -> "JSONExporter":
        """
        Shallow copy.
        """

        return self.copy()

    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "JSONExporter":
        """
        Deep copy.
        """

        return self.clone()                                                                                