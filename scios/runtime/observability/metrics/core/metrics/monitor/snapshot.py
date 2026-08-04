# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import json
import threading

from copy import deepcopy
from datetime import UTC
from datetime import datetime
from enum import Enum
from threading import RLock
from typing import Any
from typing import TypeAlias

__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_METADATA",
    "DEFAULT_TIMESTAMP",
    "DEFAULT_LOCK",
    "SnapshotValue",
    "SnapshotData",
    "SnapshotStatus",
    "SnapshotFormat",
    "MetadataType",
    "MetricSnapshot",
]

DEFAULT_NAME: str = ""
DEFAULT_VERSION: str = "1.0.0"
DEFAULT_METADATA: dict[str, Any] = {}
DEFAULT_TIMESTAMP: datetime | None = None
DEFAULT_LOCK = RLock


# ==========================================================
# Part 2. Enums & Type Aliases
# ==========================================================

SnapshotValue: TypeAlias = str | dict[str, Any] | list[Any] | None

SnapshotData: TypeAlias = dict[str, Any]

MetadataType: TypeAlias = dict[str, Any]


class SnapshotStatus(str, Enum):
    EMPTY = "empty"
    CAPTURED = "captured"
    RESTORED = "restored"


class SnapshotFormat(str, Enum):
    DICT = "dict"
    JSON = "json"


# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricSnapshot:
    __slots__ = (
        "_name",
        "_timestamp",
        "_version",
        "_metadata",
        "_data",
        "_status",
        "_format",
        "_readonly",
        "_lock",
    )

    _name: str
    _timestamp: datetime
    _version: str
    _metadata: MetadataType
    _data: SnapshotData
    _status: SnapshotStatus
    _format: SnapshotFormat
    _readonly: bool
    _lock: Any

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        timestamp: datetime | None = DEFAULT_TIMESTAMP,
        version: str = DEFAULT_VERSION,
        metadata: MetadataType | None = None,
        data: SnapshotData | None = None,
        status: SnapshotStatus = SnapshotStatus.EMPTY,
        format: SnapshotFormat = SnapshotFormat.DICT,
        readonly: bool = False,
    ) -> None:

        self._name = str(name)
        self._timestamp = (
            timestamp
            if timestamp is not None
            else datetime.now(UTC)
        )
        self._version = str(version)

        self._metadata = dict(metadata) if metadata is not None else {}
        self._data = dict(data) if data is not None else {}

        self._status = SnapshotStatus(status)
        self._format = SnapshotFormat(format)

        self._readonly = bool(readonly)

        # Always create the public CPython recursive lock
        # (_thread.RLock), never threading._RLock.
        self._lock = threading.RLock()


# ==========================================================
# Part 4. Properties
# ==========================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> MetadataType:
        return self._metadata

    @property
    def data(self) -> SnapshotData:
        return self._data

    @property
    def status(self) -> SnapshotStatus:
        return self._status

    @property
    def format(self) -> SnapshotFormat:
        return self._format

    @property
    def readonly(self) -> bool:
        return self._readonly

    @property
    def lock(self) -> threading._RLock:
        return self._lock

# ==========================================================
# Part 5. Snapshot API
# ==========================================================

    def capture(
        self,
        data: SnapshotData | None = None,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            if data is not None:
                self._data = deepcopy(dict(data))

            self._status = SnapshotStatus.CAPTURED
            self._timestamp = datetime.now(UTC)

    def restore(
        self,
        data: SnapshotData | None = None,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            if data is not None:
                self._data = deepcopy(dict(data))

            self._status = SnapshotStatus.RESTORED
            self._timestamp = datetime.now(UTC)

    def clear(self) -> None:

        with self._lock:
            if self._readonly:
                return

            self._data.clear()
            self._status = SnapshotStatus.EMPTY
            self._timestamp = datetime.now(UTC)

    def reset(self) -> None:

        with self._lock:
            self._name = DEFAULT_NAME
            self._version = DEFAULT_VERSION
            self._metadata.clear()
            self._data.clear()
            self._status = SnapshotStatus.EMPTY
            self._format = SnapshotFormat.DICT
            self._readonly = False
            self._timestamp = datetime.now(UTC)

    def freeze(self) -> None:

        with self._lock:
            self._readonly = True

    def unfreeze(self) -> None:

        with self._lock:
            self._readonly = False

    def touch(self) -> None:

        with self._lock:
            self._timestamp = datetime.now(UTC)


# ==========================================================
# Part 6. Data API
# ==========================================================

    def set_data(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            self._data[str(key)] = value

    def update_data(
        self,
        values: SnapshotData,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            self._data.update(dict(values))

    def merge_data(
        self,
        values: SnapshotData,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            self._data |= dict(values)

    def remove_data(
        self,
        key: str,
    ) -> None:

        with self._lock:
            if self._readonly:
                return

            self._data.pop(str(key), None)

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._data.get(str(key), default)

    def contains(
        self,
        key: str,
    ) -> bool:

        return str(key) in self._data


# ==========================================================
# Part 7. Metadata API
# ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._metadata[str(key)] = value

    def update_metadata(
        self,
        values: MetadataType,
    ) -> None:

        with self._lock:
            self._metadata.update(dict(values))

    def clear_metadata(self) -> None:

        with self._lock:
            self._metadata.clear()


# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": deepcopy(self._metadata),
            "data": deepcopy(self._data),
            "status": self._status.value,
            "format": self._format.value,
            "readonly": self._readonly,
        }

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
    ) -> "MetricSnapshot":

        return cls(
            name=value.get("name", DEFAULT_NAME),
            timestamp=datetime.fromisoformat(value["timestamp"])
            if value.get("timestamp")
            else datetime.now(UTC),
            version=value.get("version", DEFAULT_VERSION),
            metadata=value.get("metadata", {}),
            data=value.get("data", {}),
            status=SnapshotStatus(value.get("status", SnapshotStatus.EMPTY.value)),
            format=SnapshotFormat(value.get("format", SnapshotFormat.DICT.value)),
            readonly=value.get("readonly", False),
        )

    def to_json(self) -> str:

        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "MetricSnapshot":

        return cls.from_dict(json.loads(value))

# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self) -> bool:

        if not isinstance(self._name, str):
            return False

        if not isinstance(self._timestamp, datetime):
            return False

        if not isinstance(self._version, str):
            return False

        if not isinstance(self._metadata, dict):
            return False

        if not isinstance(self._data, dict):
            return False

        if not isinstance(self._status, SnapshotStatus):
            return False

        if not isinstance(self._format, SnapshotFormat):
            return False

        if not isinstance(self._readonly, bool):
            return False

        return True

    def is_valid(self) -> bool:

        return self.validate()


# ==========================================================
# Part 10. Snapshot Clone API
# ==========================================================

    def copy(self) -> "MetricSnapshot":

        return self.__class__.from_dict(self.to_dict())

    def deepcopy(self) -> "MetricSnapshot":

        return self.copy()

    def clone(self) -> "MetricSnapshot":

        return self.copy()


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name={self._name!r}, "
            f"status={self._status.value!r})"
        )

    def __str__(self) -> str:

        return self._name

    def __bool__(self) -> bool:

        return bool(self._data)

    def __len__(self) -> int:

        return len(self._data)

    def __contains__(
        self,
        key: object,
    ) -> bool:

        return str(key) in self._data

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.set_data(key, value)

    def __iter__(self):

        return iter(self._data)

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricSnapshot):
            return False

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:

        return hash(
            (
                self._name,
                self._version,
                self._status,
                self._format,
                self._readonly,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return self.to_dict()

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        obj = self.from_dict(state)

        self._name = obj._name
        self._timestamp = obj._timestamp
        self._version = obj._version

        self._metadata = dict(obj._metadata)
        self._data = dict(obj._data)

        self._status = obj._status
        self._format = obj._format
        self._readonly = obj._readonly

        self._lock = threading._RLock()


# ==========================================================
# Part 12. Diagnostics API
# ==========================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "status": self._status.value,
            "readonly": self._readonly,
            "entries": len(self._data),
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            **self.summary(),
            "valid": self.validate(),
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "format": self._format.value,
        }

    def snapshot_report(self) -> dict[str, Any]:

        return self.to_dict()

    def overall_status(self) -> str:

        if not self.validate():
            return "invalid"

        return self._status.value


# ==========================================================
# Part 13. Public API
# ==========================================================

__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_METADATA",
    "DEFAULT_TIMESTAMP",
    "DEFAULT_LOCK",
    "SnapshotValue",
    "SnapshotData",
    "SnapshotStatus",
    "SnapshotFormat",
    "MetadataType",
    "MetricSnapshot",
]                