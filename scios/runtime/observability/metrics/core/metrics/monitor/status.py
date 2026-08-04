# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from threading import RLock
from typing import Any, Final, TypeAlias, Union


DEFAULT_STATUS: Final[str] = "unknown"
DEFAULT_MESSAGE: Final[str] = ""
DEFAULT_VERSION: Final[str] = "1.0"


# Forward reference until MetricStatus is defined.
StatusValue: TypeAlias = Union[str, "MetricStatus"]


__all__ = [
    "DEFAULT_STATUS",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "StatusValue",
    "MetricStatus",
    "MetricStatusInfo",
]

# ==========================================================
# Part 2. Enums
# ==========================================================


class MetricStatus(str, Enum):
    """
    Enumeration of metric monitoring states.

    Values
    ------
    UNKNOWN
        Status cannot be determined.

    OK
        Metric is healthy.

    WARNING
        Metric is approaching a threshold.

    ERROR
        Metric is unhealthy or has exceeded a threshold.
    """

    UNKNOWN = "unknown"
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"

# ==========================================================
# Part 3. Constructor
# ==========================================================


class MetricStatusInfo:
    """
    Thread-safe metric status container.
    """

    __slots__ = (
        "_status",
        "_message",
        "_timestamp",
        "_version",
        "_metadata",
        "_lock",
    )

    def __init__(
        self,
        status: StatusValue = MetricStatus.UNKNOWN,
        *,
        message: str = DEFAULT_MESSAGE,
        timestamp: datetime | None = None,
        version: str = DEFAULT_VERSION,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self._status: MetricStatus = (
            status
            if isinstance(status, MetricStatus)
            else MetricStatus(str(status))
        )

        self._message: str = str(message)

        self._timestamp: datetime = (
            timestamp
            if timestamp is not None
            else datetime.now(UTC)
        )

        self._version: str = str(version)

        self._metadata: dict[str, Any] = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        self._lock = RLock()


# ==========================================================
# Part 4. Properties
# ==========================================================

    @property
    def status(self) -> MetricStatus:
        return self._status

    @property
    def message(self) -> str:
        return self._message

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    @property
    def lock(self) -> RLock:
        return self._lock

# ==========================================================
# Part 5. State API
# ==========================================================

    def set_ok(
        self,
        message: str = DEFAULT_MESSAGE,
    ) -> "MetricStatusInfo":

        with self._lock:
            self._status = MetricStatus.OK
            self._message = str(message)
            self._timestamp = datetime.now(UTC)

        return self

    def set_warning(
        self,
        message: str = DEFAULT_MESSAGE,
    ) -> "MetricStatusInfo":

        with self._lock:
            self._status = MetricStatus.WARNING
            self._message = str(message)
            self._timestamp = datetime.now(UTC)

        return self

    def set_error(
        self,
        message: str = DEFAULT_MESSAGE,
    ) -> "MetricStatusInfo":

        with self._lock:
            self._status = MetricStatus.ERROR
            self._message = str(message)
            self._timestamp = datetime.now(UTC)

        return self

    def set_unknown(
        self,
        message: str = DEFAULT_MESSAGE,
    ) -> "MetricStatusInfo":

        with self._lock:
            self._status = MetricStatus.UNKNOWN
            self._message = str(message)
            self._timestamp = datetime.now(UTC)

        return self

    def reset(self) -> "MetricStatusInfo":

        with self._lock:
            self._status = MetricStatus.UNKNOWN
            self._message = DEFAULT_MESSAGE
            self._timestamp = datetime.now(UTC)
            self._metadata.clear()

        return self


# ==========================================================
# Part 6. Query API
# ==========================================================

    def is_ok(self) -> bool:
        return self._status is MetricStatus.OK

    def is_warning(self) -> bool:
        return self._status is MetricStatus.WARNING

    def is_error(self) -> bool:
        return self._status is MetricStatus.ERROR

    def is_unknown(self) -> bool:
        return self._status is MetricStatus.UNKNOWN


# ==========================================================
# Part 7. Metadata API
# ==========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> "MetricStatusInfo":

        with self._lock:
            self._metadata[str(key)] = value

        return self

    def update_metadata(
        self,
        metadata: dict[str, Any],
    ) -> "MetricStatusInfo":

        with self._lock:
            self._metadata.update(metadata)

        return self

    def clear_metadata(self) -> "MetricStatusInfo":

        with self._lock:
            self._metadata.clear()

        return self


# ==========================================================
# Part 8. Serialization
# ==========================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "status": self._status.value,
            "message": self._message,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": dict(self._metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricStatusInfo":

        return cls(
            status=data.get("status", DEFAULT_STATUS),
            message=data.get("message", DEFAULT_MESSAGE),
            timestamp=datetime.fromisoformat(
                data["timestamp"],
            ) if data.get("timestamp") else None,
            version=data.get(
                "version",
                DEFAULT_VERSION,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    def to_json(self) -> str:

        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricStatusInfo":

        import json

        return cls.from_dict(
            json.loads(text),
        )

# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate internal state.
        """

        if not isinstance(self._status, MetricStatus):
            raise TypeError("status must be MetricStatus")

        if not isinstance(self._message, str):
            raise TypeError("message must be str")

        if not isinstance(self._timestamp, datetime):
            raise TypeError("timestamp must be datetime")

        if not isinstance(self._version, str):
            raise TypeError("version must be str")

        if not isinstance(self._metadata, dict):
            raise TypeError("metadata must be dict")

    def is_valid(self) -> bool:

        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 10. Snapshot
# ==========================================================

    def copy(self) -> "MetricStatusInfo":

        return self.__copy__()

    def deepcopy(self) -> "MetricStatusInfo":

        return self.__deepcopy__({})

    def clone(self) -> "MetricStatusInfo":

        return self.deepcopy()


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"status={self._status.value!r}, "
            f"message={self._message!r})"
        )

    def __str__(self) -> str:

        return self._status.value

    def __bool__(self) -> bool:

        return self.is_ok()

    def __len__(self) -> int:

        return len(self._metadata)

    def __copy__(self) -> "MetricStatusInfo":

        obj = self.__class__.__new__(self.__class__)
        obj.__setstate__(self.__getstate__())
        return obj

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricStatusInfo":

        import copy

        obj = self.__class__.__new__(self.__class__)
        obj.__setstate__(
            copy.deepcopy(
                self.__getstate__(),
                memo,
            )
        )
        return obj

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, MetricStatusInfo):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:

        return hash(
            (
                self._status,
                self._message,
                self._timestamp,
                self._version,
                tuple(sorted(self._metadata.items())),
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "status": self._status,
            "message": self._message,
            "timestamp": self._timestamp,
            "version": self._version,
            "metadata": dict(self._metadata),
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._status = state["status"]
        self._message = state["message"]
        self._timestamp = state["timestamp"]
        self._version = state["version"]
        self._metadata = dict(state["metadata"])
        self._lock = RLock()


# ==========================================================
# Part 12. Public API
# ==========================================================

__all__ = [
    "DEFAULT_STATUS",
    "DEFAULT_MESSAGE",
    "DEFAULT_VERSION",
    "StatusValue",
    "MetricStatus",
    "MetricStatusInfo",
]                