# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

import json
import time

from typing import Any, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME = "runtime"

DEFAULT_ENABLED = True

DEFAULT_STARTED = False

DEFAULT_RECORD_LIMIT = 1024

DEFAULT_FLUSH_INTERVAL = 60.0

DEFAULT_RECORDED = 0

DEFAULT_DROPPED = 0

__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_STARTED",
    "DEFAULT_RECORD_LIMIT",
    "DEFAULT_FLUSH_INTERVAL",
    "DEFAULT_RECORDED",
    "DEFAULT_DROPPED",
    "MetricRecord",
    "RecordList",
    "RecorderState",
    "RecorderStats",
    "RuntimeRecorder",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

MetricRecord: TypeAlias = dict[str, Any]

RecordList: TypeAlias = list[MetricRecord]

RecorderState: TypeAlias = dict[str, Any]

RecorderStats: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. RuntimeRecorder
# ==============================================================================


class RuntimeRecorder:
    """
    Runtime metrics recorder.
    """

    __slots__ = (
        "_name",
        "_enabled",
        "_started",
        "_record_limit",
        "_flush_interval",
        "_records",
        "_recorded",
        "_dropped",
        "_last_flush",
    )

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        record_limit: int = DEFAULT_RECORD_LIMIT,
        flush_interval: float = DEFAULT_FLUSH_INTERVAL,
    ) -> None:

        self._name = str(name)

        self._enabled = bool(enabled)

        self._started = DEFAULT_STARTED

        self._record_limit = int(record_limit)

        self._flush_interval = float(flush_interval)

        self._records: RecordList = []

        self._recorded = DEFAULT_RECORDED

        self._dropped = DEFAULT_DROPPED

        self._last_flush = time.time()

    @property
    def name(self) -> str:

        return self._name

    @property
    def enabled(self) -> bool:

        return self._enabled

    @property
    def started(self) -> bool:

        return self._started

    @property
    def record_limit(self) -> int:

        return self._record_limit

    @property
    def flush_interval(self) -> float:

        return self._flush_interval

    @property
    def records(self) -> RecordList:

        return list(self._records)

    @property
    def recorded(self) -> int:

        return self._recorded

    @property
    def dropped(self) -> int:

        return self._dropped

    @property
    def size(self) -> int:

        return len(self._records)

    @property
    def utilization(self) -> float:

        if self._record_limit <= 0:
            return 0.0

        return self.size / self._record_limit


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def start(self) -> None:

        self._started = True

    def stop(self) -> None:

        self._started = False

    def enable(self) -> None:

        self._enabled = True

    def disable(self) -> None:

        self._enabled = False

    def clear(self) -> None:

        self._records.clear()

    def reset(self) -> None:

        self._started = DEFAULT_STARTED
        self._enabled = DEFAULT_ENABLED
        self._records.clear()
        self._recorded = DEFAULT_RECORDED
        self._dropped = DEFAULT_DROPPED
        self._last_flush = time.time()

    def flush(self) -> RecordList:

        records = list(self._records)

        self._records.clear()

        self._last_flush = time.time()

        return records


# ==============================================================================
# Part 6. Record API
# ==============================================================================

    def record(
        self,
        record: MetricRecord,
    ) -> bool:

        if len(self._records) >= self._record_limit:

            self._dropped += 1

            return False

        self._records.append(dict(record))

        self._recorded += 1

        return True

    def append(
        self,
        record: MetricRecord,
    ) -> bool:

        return self.record(record)

    def extend(
        self,
        records: RecordList,
    ) -> None:

        for record in records:

            self.record(record)

    def remove(
        self,
        record: MetricRecord,
    ) -> None:

        self._records.remove(record)

    def pop(
        self,
        index: int = -1,
    ) -> MetricRecord:

        return self._records.pop(index)

    def latest(self) -> MetricRecord | None:

        if not self._records:
            return None

        return self._records[-1]

    def first(self) -> MetricRecord | None:

        if not self._records:
            return None

        return self._records[0]

    def records_list(self) -> RecordList:

        return list(self._records)

    def clear_records(self) -> None:

        self._records.clear()

    def has_records(self) -> bool:

        return bool(self._records)

# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    def record_success(self) -> None:

        self._recorded += 1

    def record_drop(self) -> None:

        self._dropped += 1

    @property
    def success_rate(self) -> float:

        total = self._recorded + self._dropped

        if total == 0:
            return 0.0

        return self._recorded / total

    @property
    def drop_rate(self) -> float:

        total = self._recorded + self._dropped

        if total == 0:
            return 0.0

        return self._dropped / total

    def stats(self) -> RecorderStats:

        return {
            "recorded": self._recorded,
            "dropped": self._dropped,
            "success_rate": self.success_rate,
            "drop_rate": self.drop_rate,
        }

    def reset_stats(self) -> None:

        self._recorded = DEFAULT_RECORDED
        self._dropped = DEFAULT_DROPPED


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self) -> "RuntimeRecorder":

        return self.from_dict(
            self.to_dict()
        )

    def copy(self) -> "RuntimeRecorder":

        return self.clone()

    def merge(
        self,
        other: "RuntimeRecorder",
    ) -> "RuntimeRecorder":

        self._records.extend(other.records)

        if len(self._records) > self._record_limit:

            self._records = self._records[: self._record_limit]

        self._recorded = other.recorded
        self._dropped = other.dropped
        self._enabled = other.enabled
        self._started = other.started

        return self

    def update(
        self,
        records: RecordList,
    ) -> "RuntimeRecorder":

        self.extend(records)

        return self

    def snapshot(self) -> RecorderState:

        return self.to_dict()

    def restore(
        self,
        state: RecorderState,
    ) -> None:

        restored = self.from_dict(state)

        self._name = restored._name
        self._enabled = restored._enabled
        self._started = restored._started
        self._record_limit = restored._record_limit
        self._flush_interval = restored._flush_interval
        self._records = restored._records
        self._recorded = restored._recorded
        self._dropped = restored._dropped
        self._last_flush = restored._last_flush


# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(self) -> bool:

        return (
            isinstance(self._name, str)
            and
            bool(self._name.strip())
        )

    def validate_records(self) -> bool:

        return isinstance(
            self._records,
            list,
        )

    def validate_limits(self) -> bool:

        return (
            self._record_limit >= 0
            and
            self._flush_interval >= 0.0
        )

    def validate(self) -> bool:

        return all(
            (
                self.validate_name(),
                self.validate_records(),
                self.validate_limits(),
            )
        )

    def normalize(self) -> "RuntimeRecorder":

        self._name = self._name.strip()

        return self


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> RecorderState:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "started": self._started,
            "record_limit": self._record_limit,
            "flush_interval": self._flush_interval,
            "records": list(self._records),
            "recorded": self._recorded,
            "dropped": self._dropped,
        }

    @classmethod
    def from_dict(
        cls,
        data: RecorderState,
    ) -> "RuntimeRecorder":

        recorder = cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),
            record_limit=data.get(
                "record_limit",
                DEFAULT_RECORD_LIMIT,
            ),
            flush_interval=data.get(
                "flush_interval",
                DEFAULT_FLUSH_INTERVAL,
            ),
        )

        recorder._started = data.get(
            "started",
            DEFAULT_STARTED,
        )

        recorder._records = list(
            data.get(
                "records",
                [],
            )
        )

        recorder._recorded = data.get(
            "recorded",
            DEFAULT_RECORDED,
        )

        recorder._dropped = data.get(
            "dropped",
            DEFAULT_DROPPED,
        )

        recorder._last_flush = time.time()

        return recorder

    def to_tuple(self) -> tuple[Any, ...]:

        return (
            self._name,
            self._enabled,
            self._started,
            self._record_limit,
            self._flush_interval,
            list(self._records),
            self._recorded,
            self._dropped,
        )

    @classmethod
    def from_tuple(
        cls,
        data: tuple[Any, ...],
    ) -> "RuntimeRecorder":

        recorder = cls(
            name=data[0],
            enabled=data[1],
            record_limit=data[3],
            flush_interval=data[4],
        )

        recorder._started = data[2]
        recorder._records = list(data[5])
        recorder._recorded = data[6]
        recorder._dropped = data[7]

        return recorder

    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
            indent=2,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "RuntimeRecorder":

        return cls.from_dict(
            json.loads(text)
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "started": self._started,
            "size": self.size,
            "recorded": self._recorded,
            "dropped": self._dropped,
        }

    def diagnostics(self) -> dict[str, Any]:

        return {
            **self.summary(),
            "utilization": self.utilization,
            "success_rate": self.success_rate,
            "drop_rate": self.drop_rate,
            "valid": self.validate(),
        }

    def report(self) -> dict[str, Any]:

        return self.diagnostics()

    def status(self) -> str:

        if not self._enabled:
            return "disabled"

        if self._started:
            return "running"

        return "idle"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self) -> int:

        return len(
            self._records
        )

    def __contains__(
        self,
        item: object,
    ) -> bool:

        return item in self._records

    def __iter__(self):

        return iter(
            self._records
        )

    def __hash__(self) -> int:

        return hash(
            (
                self._name,
                self._record_limit,
            )
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            RuntimeRecorder,
        ):
            return False

        return (
            self.to_dict()
            == other.to_dict()
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"size={self.size}, "
            f"enabled={self._enabled})"
        )

    def __str__(self) -> str:

        return self._name

    def __bool__(self) -> bool:

        return self._enabled
                