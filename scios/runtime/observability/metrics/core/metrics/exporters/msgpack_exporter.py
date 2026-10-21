# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy
import threading

from pathlib import Path
from typing import Any, Final, TypeAlias

import msgpack

from ..serialization.metric_serializer import MetricSerializer


Serializable: TypeAlias = Any


DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_USE_BIN_TYPE: Final[bool] = True

DEFAULT_STRICT_TYPES: Final[bool] = False


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_USE_BIN_TYPE",
    "DEFAULT_STRICT_TYPES",
    "Serializable",
    "MsgPackExporter",
]


class MsgPackExporter:
    """
    MessagePack metric exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_use_bin_type",
        "_strict_types",
        "_serializer",
        "_lock",
    )

    # ==========================================================
    # Part 2. Constructor
    # ==========================================================

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
        use_bin_type: bool = DEFAULT_USE_BIN_TYPE,
        strict_types: bool = DEFAULT_STRICT_TYPES,
        serializer: MetricSerializer | None = None,
    ) -> None:
        """
        Create MessagePack exporter.
        """

        self._version = version
        self._encoding = encoding
        self._use_bin_type = use_bin_type
        self._strict_types = strict_types

        self._serializer = (
            serializer
            if serializer is not None
            else MetricSerializer()
        )

        self._lock = threading.RLock()

    # ==========================================================
    # Part 3. Properties
    # ==========================================================

    @property
    def version(self) -> str:
        """Exporter version."""
        return self._version

    @property
    def encoding(self) -> str:
        """String encoding."""
        return self._encoding

    @property
    def use_bin_type(self) -> bool:
        """Use MessagePack binary type."""
        return self._use_bin_type

    @property
    def strict_types(self) -> bool:
        """Strict type serialization."""
        return self._strict_types

    @property
    def serializer(self) -> MetricSerializer:
        """Metric serializer."""
        return self._serializer

    @property
    def lock(self) -> threading.RLock:
        """Internal synchronization lock."""
        return self._lock

    # ==========================================================
    # Part 4. Internal Helpers
    # ==========================================================

    def _metadata(self) -> dict[str, Any]:
        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "encoding": self._encoding,
            "use_bin_type": self._use_bin_type,
            "strict_types": self._strict_types,
        }

    def _normalize(
        self,
        obj: Any,
    ) -> dict[str, Any]:
        """
        Normalize object into plain dictionary.
        """

        if isinstance(obj, dict):
            return dict(obj)

        if hasattr(obj, "to_dict"):
            return dict(obj.to_dict())

        if hasattr(obj, "snapshot"):
            snap = obj.snapshot()
            if isinstance(snap, dict):
                return dict(snap)

        data = self._serializer.to_dict(obj)

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict):
                return dict(data["data"])
            return dict(data)

        return {"value": data}

    def _packer_kwargs(self) -> dict[str, Any]:
        return {
            "use_bin_type": self._use_bin_type,
            "strict_types": self._strict_types,
        }

    def _export_payload(
        self,
        obj: Any,
    ) -> dict[str, Any]:

        metric = self._normalize(obj)

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "data": metric,
        }

    def _export_many_payload(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:

        items = [
            self._normalize(obj)
            for obj in objects
        ]

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "count": len(items),
            "items": items,
        }

    # ==========================================================
    # Part 5. Export API
    # ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:

        with self._lock:
            return self._export_payload(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:

        with self._lock:
            return self._export_many_payload(objects)

    def export_msgpack(
        self,
        obj: Serializable,
    ) -> bytes:

        with self._lock:

            metric = self._normalize(obj)

            return msgpack.packb(
                metric,
                **self._packer_kwargs(),
            )

    def export_many_msgpack(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> bytes:

        with self._lock:

            metrics = [
                self._normalize(obj)
                for obj in objects
            ]

            return msgpack.packb(
                metrics,
                **self._packer_kwargs(),
            )

    # ==========================================================
    # Part 6. File Export
    # ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_msgpack(obj)
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_many_msgpack(objects)
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> bytes:
        """
        Load raw MsgPack bytes.
        """

        with self._lock:

            file_path = Path(path)

            return file_path.read_bytes()

    # ==========================================================
    # Part 7. Validation
    # ==========================================================

    def validate(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Validate whether an object can be exported.
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
            f"encoding={self._encoding!r}, "
            f"use_bin_type={self._use_bin_type!r}, "
            f"strict_types={self._strict_types!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(v{self._version})"
        )

    def __len__(self) -> int:

        return 4

    def __bool__(self) -> bool:

        return True

    def __copy__(self):

        return self.__class__(
            version=self._version,
            encoding=self._encoding,
            use_bin_type=self._use_bin_type,
            strict_types=self._strict_types,
            serializer=self._serializer,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(self._version, memo),
            encoding=copy.deepcopy(self._encoding, memo),
            use_bin_type=copy.deepcopy(self._use_bin_type, memo),
            strict_types=copy.deepcopy(self._strict_types, memo),
            serializer=copy.deepcopy(self._serializer, memo),
        )

        memo[id(self)] = copied

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            MsgPackExporter,
        ):
            return NotImplemented

        return (
            self._version == other._version
            and self._encoding == other._encoding
            and self._use_bin_type == other._use_bin_type
            and self._strict_types == other._strict_types
        )

    def __hash__(self) -> int:

        return hash(
            (
                self._version,
                self._encoding,
                self._use_bin_type,
                self._strict_types,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "version": self._version,
            "encoding": self._encoding,
            "use_bin_type": self._use_bin_type,
            "strict_types": self._strict_types,
            "serializer": self._serializer,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._encoding = state["encoding"]
        self._use_bin_type = state["use_bin_type"]
        self._strict_types = state["strict_types"]
        self._serializer = state["serializer"]
        self._lock = threading.RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_USE_BIN_TYPE",
    "DEFAULT_STRICT_TYPES",
    "Serializable",
    "MsgPackExporter",
]                    