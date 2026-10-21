# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy
import json

from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)


Serializable: TypeAlias = Any


DEFAULT_VERSION: Final[str] = "1.0"
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_DETERMINISTIC: Final[bool] = True
DEFAULT_PRESERVE_PROTO_FIELD_NAME: Final[bool] = True


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_DETERMINISTIC",
    "DEFAULT_PRESERVE_PROTO_FIELD_NAME",
    "Serializable",
    "ProtobufExporter",
]


class ProtobufExporter:
    """
    Google Protocol Buffers exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_deterministic",
        "_preserve_proto_field_name",
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
        deterministic: bool = DEFAULT_DETERMINISTIC,
        preserve_proto_field_name: bool = DEFAULT_PRESERVE_PROTO_FIELD_NAME,
        serializer: MetricSerializer | None = None,
    ) -> None:
        """
        Create protobuf exporter.
        """

        self._version = version
        self._encoding = encoding
        self._deterministic = deterministic
        self._preserve_proto_field_name = preserve_proto_field_name

        self._serializer = (
            serializer
            if serializer is not None
            else MetricSerializer()
        )

        self._lock = RLock()

    # ==========================================================
    # Part 3. Properties
    # ==========================================================

    @property
    def version(self) -> str:
        """Exporter version."""
        return self._version

    @property
    def encoding(self) -> str:
        """Default text encoding."""
        return self._encoding

    @property
    def deterministic(self) -> bool:
        """Deterministic serialization flag."""
        return self._deterministic

    @property
    def preserve_proto_field_name(self) -> bool:
        """Preserve original protobuf field names."""
        return self._preserve_proto_field_name

    @property
    def serializer(self) -> MetricSerializer:
        """Underlying metric serializer."""
        return self._serializer

    @property
    def lock(self) -> RLock:
        """Internal synchronization lock."""
        return self._lock

# ==========================================================
# Part 4. Internal Helpers
# ==========================================================

    def _metadata(self) -> dict[str, Any]:
        """
        Exporter metadata.
        """

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "encoding": self._encoding,
            "deterministic": self._deterministic,
            "preserve_proto_field_name": self._preserve_proto_field_name,
        }

    def _normalize(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Normalize object into plain dictionary.
        """

        if isinstance(obj, dict):
            return dict(obj)

        if hasattr(obj, "to_dict"):
            return dict(obj.to_dict())

        if hasattr(obj, "snapshot"):
            snapshot = obj.snapshot()
            if isinstance(snapshot, dict):
                return dict(snapshot)

        data = self._serializer.to_dict(obj)

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict):
                return dict(data["data"])
            return dict(data)

        return {
            "value": data,
        }

    def _dumps_kwargs(self) -> dict[str, Any]:
        """
        Serialization options.
        """

        return {
            "deterministic": self._deterministic,
            "preserve_proto_field_name": self._preserve_proto_field_name,
        }

    def _export_payload(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Export single payload.
        """

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "data": self._normalize(obj),
        }

    def _export_many_payload(
        self,
        objects: list[Serializable]
        | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Export multiple payloads.
        """

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
        """
        Export single object.
        """

        with self._lock:
            return self._export_payload(obj)

    def export_many(
        self,
        objects: list[Serializable]
        | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Export multiple objects.
        """

        with self._lock:
            return self._export_many_payload(objects)

    def export_protobuf(
        self,
        obj: Serializable,
    ) -> bytes:
        """
        Export one object as protobuf-like binary.
        """

        with self._lock:

            payload = self._normalize(obj)

            return json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=self._deterministic,
            ).encode(self._encoding)

    def export_many_protobuf(
        self,
        objects: list[Serializable]
        | tuple[Serializable, ...],
    ) -> bytes:
        """
        Export multiple objects as protobuf-like binary.
        """

        with self._lock:

            payload = [
                self._normalize(obj)
                for obj in objects
            ]

            return json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=self._deterministic,
            ).encode(self._encoding)


# ==========================================================
# Part 6. File Export
# ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export one object to file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_protobuf(obj)
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable]
        | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:
        """
        Export many objects to file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_many_protobuf(objects)
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> bytes:
        """
        Load raw protobuf bytes.
        """

        with self._lock:

            return Path(path).read_bytes()

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
            f"encoding={self._encoding!r}, "
            f"deterministic={self._deterministic!r}, "
            f"preserve_proto_field_name="
            f"{self._preserve_proto_field_name!r}"
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
            deterministic=self._deterministic,
            preserve_proto_field_name=(
                self._preserve_proto_field_name
            ),
            serializer=self._serializer,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(
                self._version,
                memo,
            ),
            encoding=copy.deepcopy(
                self._encoding,
                memo,
            ),
            deterministic=copy.deepcopy(
                self._deterministic,
                memo,
            ),
            preserve_proto_field_name=copy.deepcopy(
                self._preserve_proto_field_name,
                memo,
            ),
            serializer=copy.deepcopy(
                self._serializer,
                memo,
            ),
        )

        memo[id(self)] = copied

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            ProtobufExporter,
        ):
            return NotImplemented

        return (
            self._version == other._version
            and self._encoding == other._encoding
            and self._deterministic
            == other._deterministic
            and self._preserve_proto_field_name
            == other._preserve_proto_field_name
        )

    def __hash__(self) -> int:

        return hash(
            (
                self._version,
                self._encoding,
                self._deterministic,
                self._preserve_proto_field_name,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "version": self._version,
            "encoding": self._encoding,
            "deterministic": self._deterministic,
            "preserve_proto_field_name": (
                self._preserve_proto_field_name
            ),
            "serializer": self._serializer,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        self._version = state["version"]
        self._encoding = state["encoding"]
        self._deterministic = state["deterministic"]
        self._preserve_proto_field_name = state["preserve_proto_field_name"]
        self._serializer = state["serializer"]
        self._lock = RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_DETERMINISTIC",
    "DEFAULT_PRESERVE_PROTO_FIELD_NAME",
    "Serializable",
    "ProtobufExporter",
]                    