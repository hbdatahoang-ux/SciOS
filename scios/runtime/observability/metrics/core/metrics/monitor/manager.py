# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import json
import threading

from copy import copy, deepcopy
from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypeAlias

__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_METADATA",
    "DEFAULT_TIMESTAMP",
    "DEFAULT_ENABLED",
    "DEFAULT_LOCK",
    "DEFAULT_CAPACITY",
    "ManagerItem",
    "ManagerData",
    "ManagerStatus",
    "ManagerMode",
    "MetadataType",
    "MetricManager",
]

DEFAULT_NAME: str = "manager"
DEFAULT_VERSION: str = "1.0.0"
DEFAULT_METADATA: dict[str, Any] = {}
DEFAULT_TIMESTAMP: datetime | None = None
DEFAULT_ENABLED: bool = True
DEFAULT_LOCK = threading.RLock
DEFAULT_CAPACITY: int = 1024


# ==========================================================
# Part 2. Enums & Type Aliases
# ==========================================================

ManagerItem: TypeAlias = Any
ManagerData: TypeAlias = dict[str, ManagerItem]
MetadataType: TypeAlias = dict[str, Any]


class ManagerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"


class ManagerMode(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"


# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricManager:
    __slots__ = (
        "_name",
        "_timestamp",
        "_version",
        "_metadata",
        "_items",
        "_status",
        "_mode",
        "_enabled",
        "_capacity",
        "_lock",
    )

    _name: str
    _timestamp: datetime
    _version: str
    _metadata: MetadataType
    _items: ManagerData
    _status: ManagerStatus
    _mode: ManagerMode
    _enabled: bool
    _capacity: int
    _lock: Any

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        timestamp: datetime | None = DEFAULT_TIMESTAMP,
        version: str = DEFAULT_VERSION,
        metadata: MetadataType | None = None,
        items: ManagerData | None = None,
        status: ManagerStatus = ManagerStatus.IDLE,
        mode: ManagerMode | str = ManagerMode.AUTO,
        enabled: bool = DEFAULT_ENABLED,
        capacity: int = DEFAULT_CAPACITY,
    ) -> None:

        self._name = str(name)
        self._timestamp = timestamp or datetime.now(UTC)
        self._version = str(version)

        self._metadata = dict(metadata or {})
        self._items = dict(items or {})

        self._status = (
            status
            if isinstance(status, ManagerStatus)
            else ManagerStatus(str(status).lower())
        )

        self._mode = (
            mode
            if isinstance(mode, ManagerMode)
            else ManagerMode(str(mode).lower())
        )

        self._enabled = bool(enabled)
        self._capacity = int(capacity)

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
    def items(self) -> ManagerData:
        return self._items

    @property
    def status(self) -> ManagerStatus:
        return self._status

    @property
    def mode(self) -> ManagerMode:
        return self._mode

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def lock(self):
        return self._lock

# ==========================================================
# Part 5. Manager API
# ==========================================================

    def start(self) -> "MetricManager":
        with self._lock:
            self._status = ManagerStatus.RUNNING
            self._timestamp = datetime.now(UTC)
        return self

    def stop(self) -> "MetricManager":
        with self._lock:
            self._status = ManagerStatus.STOPPED
            self._timestamp = datetime.now(UTC)
        return self

    def reset(self) -> "MetricManager":
        with self._lock:
            self._items.clear()
            self._metadata.clear()
            self._status = ManagerStatus.IDLE
            self._mode = ManagerMode.AUTO
            self._enabled = DEFAULT_ENABLED
            self._capacity = DEFAULT_CAPACITY
            self._timestamp = datetime.now(UTC)
        return self

    def clear(self) -> "MetricManager":
        with self._lock:
            self._items.clear()
            self._timestamp = datetime.now(UTC)
        return self

    def enable(self) -> "MetricManager":
        with self._lock:
            self._enabled = True
        return self

    def disable(self) -> "MetricManager":
        with self._lock:
            self._enabled = False
        return self

    def touch(self) -> "MetricManager":
        with self._lock:
            self._timestamp = datetime.now(UTC)
        return self


# ==========================================================
# Part 6. Item API
# ==========================================================

    def add(self, key: str, value: ManagerItem) -> "MetricManager":
        with self._lock:
            if len(self._items) >= self._capacity and key not in self._items:
                raise OverflowError("Manager capacity exceeded.")
            self._items[str(key)] = value
        return self

    def update(self, key: str, value: ManagerItem) -> "MetricManager":
        with self._lock:
            self._items[str(key)] = value
        return self

    def remove(self, key: str) -> ManagerItem | None:
        with self._lock:
            return self._items.pop(str(key), None)

    def get(self, key: str, default: Any = None) -> Any:
        return self._items.get(str(key), default)

    def contains(self, key: str) -> bool:
        return str(key) in self._items

    def count(self) -> int:
        return len(self._items)

    def keys(self):
        return tuple(self._items.keys())


# ==========================================================
# Part 7. Metadata API
# ==========================================================

    def set_metadata(self, key: str, value: Any) -> "MetricManager":
        with self._lock:
            self._metadata[str(key)] = value
        return self

    def update_metadata(self, values: MetadataType) -> "MetricManager":
        with self._lock:
            self._metadata.update(dict(values))
        return self

    def clear_metadata(self) -> "MetricManager":
        with self._lock:
            self._metadata.clear()
        return self


# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": dict(self._metadata),
            "items": dict(self._items),
            "status": self._status.value,
            "mode": self._mode.value,
            "enabled": self._enabled,
            "capacity": self._capacity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricManager":
        return cls(
            name=data.get("name", DEFAULT_NAME),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else None,
            version=data.get("version", DEFAULT_VERSION),
            metadata=data.get("metadata", {}),
            items=data.get("items", {}),
            status=ManagerStatus(data.get("status", ManagerStatus.IDLE)),
            mode=ManagerMode(data.get("mode", ManagerMode.AUTO)),
            enabled=data.get("enabled", DEFAULT_ENABLED),
            capacity=data.get("capacity", DEFAULT_CAPACITY),
        )

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), default=str, **kwargs)

    @classmethod
    def from_json(cls, value: str) -> "MetricManager":
        return cls.from_dict(json.loads(value))

# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self) -> None:
        if not self._name:
            raise ValueError("Manager name cannot be empty.")
        if self._capacity < 0:
            raise ValueError("Capacity must be >= 0.")
        if len(self._items) > self._capacity:
            raise ValueError("Capacity exceeded.")

    def is_valid(self) -> bool:
        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 10. Snapshot API
# ==========================================================

    def copy(self) -> "MetricManager":
        return copy(self)

    def deepcopy(self) -> "MetricManager":
        return deepcopy(self)

    def clone(self) -> "MetricManager":
        return type(self).from_dict(self.to_dict())


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"(name={self._name!r}, items={len(self._items)})"
        )

    def __str__(self) -> str:
        return f"{self._name} [{self._status.value}]"

    def __bool__(self) -> bool:
        return self._enabled

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: object) -> bool:
        return str(key) in self._items

    def __getitem__(self, key: str) -> ManagerItem:
        return self._items[key]

    def __setitem__(self, key: str, value: ManagerItem) -> None:
        self.update(key, value)

    def __iter__(self):
        return iter(self._items)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricManager):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._version,
                self._status,
                self._mode,
                self._enabled,
                self._capacity,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        return self.to_dict()

    def __setstate__(self, state: dict[str, Any]) -> None:
        obj = type(self).from_dict(state)

        self._name = obj._name
        self._timestamp = obj._timestamp
        self._version = obj._version
        self._metadata = dict(obj._metadata)
        self._items = dict(obj._items)
        self._status = obj._status
        self._mode = obj._mode
        self._enabled = obj._enabled
        self._capacity = obj._capacity
        self._lock = threading.RLock()


# ==========================================================
# Part 12. Diagnostics API
# ==========================================================

    def summary(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "status": self._status.value,
            "enabled": self._enabled,
            "count": len(self._items),
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "capacity": self._capacity,
            "mode": self._mode.value,
            "version": self._version,
            "timestamp": self._timestamp.isoformat(),
            "valid": self.is_valid(),
        }

    def manager_report(self) -> dict[str, Any]:
        return {
            "manager": self.to_dict(),
            "diagnostics": self.diagnostics(),
        }

    def overall_status(self) -> str:
        if not self._enabled:
            return "disabled"
        if not self.is_valid():
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
    "DEFAULT_ENABLED",
    "DEFAULT_LOCK",
    "DEFAULT_CAPACITY",
    "ManagerItem",
    "ManagerData",
    "ManagerStatus",
    "ManagerMode",
    "MetadataType",
    "MetricManager",
]                