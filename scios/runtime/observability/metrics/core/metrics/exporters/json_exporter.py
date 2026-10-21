# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

from ..serialization.metric_serializer import MetricSerializer

Serializable: TypeAlias = Any

DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_INDENT: Final[int] = 2

DEFAULT_ENSURE_ASCII: Final[bool] = False

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_ENSURE_ASCII",
    "Serializable",
    "JSONExporter",
]


# ==========================================================
# Part 2. Constructor
# ==========================================================

class JSONExporter:
    """
    Thread-safe JSON exporter for the SciOS Metrics subsystem.
    """

    __slots__ = (
        "_serializer",
        "_version",
        "_encoding",
        "_indent",
        "_ensure_ascii",
        "_lock",
    )

    VERSION: Final[str] = DEFAULT_VERSION

    def __init__(
        self,
        *,
        serializer: MetricSerializer | None = None,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
        indent: int = DEFAULT_INDENT,
        ensure_ascii: bool = DEFAULT_ENSURE_ASCII,
    ) -> None:

        self._serializer = (
            serializer
            if serializer is not None
            else MetricSerializer()
        )

        self._version = version
        self._encoding = encoding
        self._indent = indent
        self._ensure_ascii = ensure_ascii

        self._lock = RLock()

# ==========================================================
# Part 3. Properties
# ==========================================================

    @property
    def serializer(self) -> MetricSerializer:
        """
        Underlying serializer.
        """
        return self._serializer

    @property
    def version(self) -> str:
        """
        Exporter version.
        """
        return self._version

    @property
    def encoding(self) -> str:
        """
        File encoding.
        """
        return self._encoding

    @property
    def indent(self) -> int:
        """
        JSON indentation.
        """
        return self._indent

    @property
    def ensure_ascii(self) -> bool:
        """
        JSON ensure_ascii flag.
        """
        return self._ensure_ascii

    @property
    def lock(self) -> RLock:
        """
        Internal synchronization lock.
        """
        return self._lock


# ==========================================================
# Part 4. Export Helpers
# ==========================================================

    def _metadata(self) -> dict[str, Any]:
        """
        Export metadata.
        """

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
        }

    def _normalize(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Normalize an object into a plain dictionary.
        """

        if isinstance(obj, dict):
            return dict(obj)

        if hasattr(obj, "to_dict"):
            data = obj.to_dict()
            if isinstance(data, dict):
                return dict(data)

        if hasattr(obj, "snapshot"):
            data = obj.snapshot()
            if isinstance(data, dict):
                return dict(data)

        data = self._serializer.to_dict(obj)

        if isinstance(data, dict):

            payload = data.get("data")

            if isinstance(payload, dict):
                return dict(payload)

            return dict(data)

        return {
            "value": data,
        }

    def _export_payload(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Build payload for a single object.
        """

        return {
            **self._metadata(),
            "data": self._normalize(obj),
        }

    def _export_many_payload(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Build payload for multiple objects.
        """

        return {
            **self._metadata(),
            "count": len(objects),
            "items": [
                self._normalize(obj)
                for obj in objects
            ],
        }

    def _json_kwargs(self) -> dict[str, Any]:
        """
        Shared json.dumps() keyword arguments.
        """

        return {
            "indent": self._indent,
            "ensure_ascii": self._ensure_ascii,
            "sort_keys": True,
            "default": str,
        }

# ==========================================================
# Part 5. Export API
# ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Export a single object as normalized dictionary.
        """

        with self._lock:
            return self._normalize(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Export multiple objects as payload.
        """

        with self._lock:
            return self._export_many_payload(objects)

    def export_json(
        self,
        obj: Serializable,
    ) -> str:
        """
        Export a single object to JSON.
        """

        with self._lock:
            return json.dumps(
                self.export(obj),
                **self._json_kwargs(),
            )

    def export_many_json(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> str:
        """
        Export multiple objects to JSON.
        """

        with self._lock:
            return json.dumps(
                self._export_many_payload(objects),
                **self._json_kwargs(),
            )


# ==========================================================
# Part 6. File Export
# ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export payload to JSON file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                json.dumps(
                    self._export_payload(obj),
                    **self._json_kwargs(),
                ),
                encoding=self._encoding,
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:
        """
        Export multiple payloads to JSON file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                json.dumps(
                    self._export_many_payload(objects),
                    **self._json_kwargs(),
                ),
                encoding=self._encoding,
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> dict[str, Any]:
        """
        Load exported JSON payload.
        """

        with self._lock:

            return json.loads(
                Path(path).read_text(
                    encoding=self._encoding,
                )
            )


# ==========================================================
# Part 7. Validation
# ==========================================================

    def validate(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Validate exportability.
        """

        try:
            self._normalize(obj)
            return True
        except Exception:
            return False

    def is_valid(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Alias of validate().
        """

        return self.validate(obj)


# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"version={self._version!r}, "
            f"encoding={self._encoding!r})"
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(version={self._version})"
        )

    def __len__(self) -> int:
        return 1

    def __bool__(self) -> bool:
        return True

    def __copy__(self):
        return self.__class__(
            serializer=self._serializer,
            version=self._version,
            encoding=self._encoding,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
        )

    def __deepcopy__(self, memo):
        return self.__class__(
            serializer=MetricSerializer(),
            version=self._version,
            encoding=self._encoding,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:
        return (
            isinstance(other, JSONExporter)
            and self.version == other.version
            and self.encoding == other.encoding
            and self.indent == other.indent
            and self.ensure_ascii == other.ensure_ascii
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__,
                self.version,
                self.encoding,
                self.indent,
                self.ensure_ascii,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return {
            "_serializer": self._serializer,
            "_version": self._version,
            "_encoding": self._encoding,
            "_indent": self._indent,
            "_ensure_ascii": self._ensure_ascii,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        self._serializer = state["_serializer"]
        self._version = state["_version"]
        self._encoding = state["_encoding"]
        self._indent = state["_indent"]
        self._ensure_ascii = state["_ensure_ascii"]
        self._lock = RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_INDENT",
    "DEFAULT_ENSURE_ASCII",
    "Serializable",
    "JSONExporter",
]                    