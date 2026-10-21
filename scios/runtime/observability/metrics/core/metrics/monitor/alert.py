# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
import threading
from typing import Any, Final, TypeAlias, Union

DEFAULT_ALERT: Final[str] = "none"
DEFAULT_LEVEL: Final[int] = 0
DEFAULT_MESSAGE: Final[str] = ""
DEFAULT_VERSION: Final[str] = "1.0"

AlertValue: TypeAlias = Union[str, "MetricAlert"]
AlertLevel: TypeAlias = int

__all__ = [
    "DEFAULT_ALERT",
    "DEFAULT_LEVEL",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "AlertValue",
    "AlertLevel",
    "MetricAlert",
    "MetricAlertInfo",
]


# ==========================================================
# Part 2. Enums
# ==========================================================


class MetricAlert(str, Enum):
    """
    Alert severity.
    """

    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==========================================================
# Part 3. Constructor
# ==========================================================



class MetricAlertInfo:
    __slots__ = (
        "_alert",
        "_level",
        "_message",
        "_source",
        "_timestamp",
        "_version",
        "_metadata",
        "_active",
        "_acknowledged",
        "_resolved",
        "_lock",
    )

    _alert: MetricAlert
    _level: int
    _message: str
    _source: str
    _timestamp: datetime
    _version: str
    _metadata: dict[str, Any]
    _active: bool
    _acknowledged: bool
    _resolved: bool
    _lock: RLock

    def __init__(
        self,
        alert: AlertValue = DEFAULT_ALERT,
        *,
        level: AlertLevel = DEFAULT_LEVEL,
        message: str = DEFAULT_MESSAGE,
        source: str = "",
        timestamp: datetime | None = None,
        version: str = DEFAULT_VERSION,
        metadata: dict[str, Any] | None = None,
        active: bool = False,
        acknowledged: bool = False,
        resolved: bool = False,
    ) -> None:

        if isinstance(alert, MetricAlert):
            self._alert = alert
        else:
            self._alert = MetricAlert(str(alert))

        self._level = int(level)
        self._message = str(message)
        self._source = str(source)
        self._timestamp = timestamp or datetime.now(UTC)
        self._version = str(version)
        self._metadata = dict(metadata or {})
        self._active = bool(active)
        self._acknowledged = bool(acknowledged)
        self._resolved = bool(resolved)
        self._lock = threading._RLock()


# ==========================================================
# Part 4. Properties
# ==========================================================

    @property
    def alert(self) -> MetricAlert:
        return self._alert

    @property
    def level(self) -> int:
        return self._level

    @property
    def message(self) -> str:
        return self._message

    @property
    def source(self) -> str:
        return self._source

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    @property
    def active(self) -> bool:
        return self._active

    @property
    def acknowledged(self) -> bool:
        return self._acknowledged

    @property
    def resolved(self) -> bool:
        return self._resolved

    @property
    def lock(self) -> threading._RLock:
        return self._lock

# ==========================================================
# Part 5. Alert State API
# ==========================================================

    def trigger(
        self,
        source: str = "",
        message: str = "",
    ) -> None:

        with self._lock:
            self._active = True
            self._resolved = False
            self._acknowledged = False

            self._source = str(source)
            self._message = str(message)

            self._timestamp = datetime.now(UTC)

    def clear(self) -> None:

        with self._lock:
            self._active = False
            self._timestamp = datetime.now(UTC)

    def acknowledge(self) -> None:

        with self._lock:
            self._acknowledged = True
            self._timestamp = datetime.now(UTC)

    def resolve(self) -> None:

        with self._lock:
            self._resolved = True
            self._active = False
            self._timestamp = datetime.now(UTC)

    def reopen(self) -> None:

        with self._lock:
            self._resolved = False
            self._active = True
            self._timestamp = datetime.now(UTC)

    def reset(self) -> None:

        with self._lock:
            self._alert = MetricAlert.NONE
            self._level = DEFAULT_LEVEL
            self._message = DEFAULT_MESSAGE
            self._source = ""
            self._version = DEFAULT_VERSION

            self._metadata.clear()

            self._active = False
            self._acknowledged = False
            self._resolved = False

            self._timestamp = datetime.now(UTC)


# ==========================================================
# Part 6. Alert Level API
# ==========================================================

    def set_info(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._alert = MetricAlert.INFO
            self._level = 1

            if message is not None:
                self._message = str(message)

            self._timestamp = datetime.now(UTC)

    def set_warning(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._alert = MetricAlert.WARNING
            self._level = 2

            if message is not None:
                self._message = str(message)

            self._timestamp = datetime.now(UTC)

    def set_error(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._alert = MetricAlert.ERROR
            self._level = 3

            if message is not None:
                self._message = str(message)

            self._timestamp = datetime.now(UTC)

    def set_critical(
        self,
        message: str | None = None,
    ) -> None:

        with self._lock:
            self._alert = MetricAlert.CRITICAL
            self._level = 4

            if message is not None:
                self._message = str(message)

            self._timestamp = datetime.now(UTC)

    def set_none(self) -> None:

        with self._lock:
            self._alert = MetricAlert.NONE
            self._level = DEFAULT_LEVEL
            self._timestamp = datetime.now(UTC)


# ==========================================================
# Part 7. Query API
# ==========================================================

    def is_active(self) -> bool:

        return self._active

    def is_acknowledged(self) -> bool:

        return self._acknowledged

    def is_resolved(self) -> bool:

        return self._resolved

    def is_info(self) -> bool:

        return self._alert is MetricAlert.INFO

    def is_warning(self) -> bool:

        return self._alert is MetricAlert.WARNING

    def is_error(self) -> bool:

        return self._alert is MetricAlert.ERROR

    def is_critical(self) -> bool:

        return self._alert is MetricAlert.CRITICAL


# ==========================================================
# Part 8. Metadata API
# ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self._metadata[str(key)] = value
            self._timestamp = datetime.now(UTC)

    def update_metadata(
        self,
        values: dict[str, Any],
    ) -> None:

        with self._lock:
            self._metadata.update(values)
            self._timestamp = datetime.now(UTC)

    def clear_metadata(self) -> None:

        with self._lock:
            self._metadata.clear()
            self._timestamp = datetime.now(UTC)

# ==========================================================
# Part 9. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "alert": self._alert.value,
            "level": self._level,
            "message": self._message,
            "source": self._source,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": dict(self._metadata),
            "active": self._active,
            "acknowledged": self._acknowledged,
            "resolved": self._resolved,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricAlertInfo":

        timestamp = data.get("timestamp")

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            alert=data.get("alert", DEFAULT_ALERT),
            level=data.get("level", DEFAULT_LEVEL),
            message=data.get("message", DEFAULT_MESSAGE),
            source=data.get("source", ""),
            timestamp=timestamp,
            version=data.get("version", DEFAULT_VERSION),
            metadata=data.get("metadata", {}),
            active=data.get("active", False),
            acknowledged=data.get("acknowledged", False),
            resolved=data.get("resolved", False),
        )

    def to_json(self) -> str:

        import json

        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "MetricAlertInfo":

        import json

        return cls.from_dict(json.loads(value))


# ==========================================================
# Part 10. Validation
# ==========================================================

    def validate(self) -> bool:
        """
        Validate internal state.

        Returns
        -------
        bool
            True if the object is internally consistent.
        """

        if not isinstance(self._alert, MetricAlert):
            return False

        if not isinstance(self._level, int):
            return False

        if self._level < 0:
            return False

        if not isinstance(self._message, str):
            return False

        if not isinstance(self._source, str):
            return False

        if not isinstance(self._version, str):
            return False

        if not isinstance(self._metadata, dict):
            return False

        if not isinstance(self._active, bool):
            return False

        if not isinstance(self._acknowledged, bool):
            return False

        if not isinstance(self._resolved, bool):
            return False

        return True

    def is_valid(self) -> bool:
        """
        Alias of validate().
        """

        return self.validate()


# ==========================================================
# Part 11. Snapshot API
# ==========================================================

    def copy(self) -> "MetricAlertInfo":
        """
        Shallow logical copy.
        """

        return type(self).from_dict(self.to_dict())

    def deepcopy(self) -> "MetricAlertInfo":
        """
        Deep logical copy.
        """

        return type(self).from_dict(self.to_dict())

    def clone(self) -> "MetricAlertInfo":
        """
        Alias of deepcopy().
        """

        return self.deepcopy()


# ==========================================================
# Part 12. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"alert={self._alert.value!r}, "
            f"active={self._active!r})"
        )

    def __str__(self) -> str:
        return self._alert.value

    def __bool__(self) -> bool:
        return self._active

    def __len__(self) -> int:
        return len(self._metadata)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricAlertInfo):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash(
            (
                self._alert,
                self._level,
                self._message,
                self._source,
                self._version,
            )
        )

    def __getstate__(self) -> dict[str, Any]:
        """
        Pickle support.
        """

        return self.to_dict()

    def __setstate__(self, state: dict[str, Any]) -> None:
        """
        Restore state without using __dict__
        because the class uses __slots__.
        """

        obj = type(self).from_dict(state)

        self._alert = obj._alert
        self._level = obj._level
        self._message = obj._message
        self._source = obj._source
        self._timestamp = obj._timestamp
        self._version = obj._version

        self._metadata = dict(obj._metadata)

        self._active = obj._active
        self._acknowledged = obj._acknowledged
        self._resolved = obj._resolved

        self._lock = threading._RLock()


# ==========================================================
# Part 13. Diagnostics API
# ==========================================================

    def summary(self) -> dict[str, Any]:

        return {
            "alert": self._alert.value,
            "active": self._active,
            "acknowledged": self._acknowledged,
            "resolved": self._resolved,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            **self.summary(),
            "level": self._level,
            "message": self._message,
            "source": self._source,
            "metadata": dict(self._metadata),
        }

    def alert_report(self) -> dict[str, Any]:

        return self.diagnostics()

    def overall_status(self) -> str:

        return self._alert.value


# ==========================================================
# Part 14. Public API
# ==========================================================

__all__ = [
    "DEFAULT_ALERT",
    "DEFAULT_LEVEL",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "AlertValue",
    "AlertLevel",
    "MetricAlert",
    "MetricAlertInfo",
]                    