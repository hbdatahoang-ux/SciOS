# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

import copy
import json
import time

from collections.abc import Iterator
from typing import Any
from typing import TypedDict
from typing import TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME: str = "runtime"

DEFAULT_ENABLED: bool = True

DEFAULT_STARTED: bool = False

DEFAULT_COLLECT_LIMIT: int = 1024

DEFAULT_INTERVAL: float = 1.0

DEFAULT_COLLECTED: int = 0

DEFAULT_FAILED: int = 0

DEFAULT_SUCCESS: int = 0

DEFAULT_FAILURE: int = 0


__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_STARTED",
    "DEFAULT_COLLECT_LIMIT",
    "DEFAULT_INTERVAL",
    "DEFAULT_COLLECTED",
    "DEFAULT_FAILED",
    "DEFAULT_SUCCESS",
    "DEFAULT_FAILURE",
    "MetricSample",
    "SampleList",
    "CollectorState",
    "CollectorStats",
    "RuntimeCollector",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

MetricSample: TypeAlias = dict[str, Any]

SampleList: TypeAlias = list[MetricSample]


class CollectorState(TypedDict):

    name: str

    enabled: bool

    started: bool

    collect_limit: int

    interval: float

    samples: SampleList

    collected: int

    failed: int

    successes: int

    failures: int

    created_at: float

    last_collect: float | None


class CollectorStats(TypedDict):

    collected: int

    failed: int

    successes: int

    failures: int

    success_rate: float

    failure_rate: float

    size: int


# ==============================================================================
# Part 4. RuntimeCollector
# ==============================================================================


class RuntimeCollector:

    __slots__ = (
        "_name",
        "_enabled",
        "_started",
        "_collect_limit",
        "_interval",
        "_samples",
        "_collected",
        "_failed",
        "_successes",
        "_failures",
        "_created_at",
        "_last_collect",
    )

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        started: bool = DEFAULT_STARTED,
        collect_limit: int = DEFAULT_COLLECT_LIMIT,
        interval: float = DEFAULT_INTERVAL,
    ) -> None:

        self._name = str(name)

        self._enabled = bool(enabled)

        self._started = bool(started)

        self._collect_limit = int(collect_limit)

        self._interval = float(interval)

        self._samples: SampleList = []

        self._collected = DEFAULT_COLLECTED

        self._failed = DEFAULT_FAILED

        self._successes = DEFAULT_SUCCESS

        self._failures = DEFAULT_FAILURE

        self._created_at = time.time()

        self._last_collect: float | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

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
    def collect_limit(self) -> int:

        return self._collect_limit

    @property
    def interval(self) -> float:

        return self._interval

    @property
    def samples(self) -> SampleList:

        return copy.deepcopy(self._samples)

    @property
    def collected(self) -> int:

        return self._collected

    @property
    def failed(self) -> int:

        return self._failed

    @property
    def successes(self) -> int:

        return self._successes

    @property
    def failures(self) -> int:

        return self._failures

    @property
    def created_at(self) -> float:

        return self._created_at

    @property
    def last_collect(self) -> float | None:

        return self._last_collect

    @property
    def size(self) -> int:

        return len(self._samples)

    @property
    def utilization(self) -> float:

        if self._collect_limit <= 0:
            return 0.0

        return min(
            1.0,
            self.size / self._collect_limit,
        )

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def start(self):

        self._started = True

        return self


    def stop(self):

        self._started = False

        return self


    def enable(self):

        self._enabled = True

        return self


    def disable(self):

        self._enabled = False

        return self


    def clear(self):

        self._samples.clear()

        self.reset_statistics()

        self._last_collect = None

        return self


    def reset(self):

        self._enabled = DEFAULT_ENABLED

        self._started = DEFAULT_STARTED

        return self.clear()


    def collect(
        self,
        sample: MetricSample | str | None = None,
        value: Any | None = None,
        **metadata: Any,
    ) -> bool:

        self._last_collect = time.time()

        if not self._enabled:

            self.record_failure()

            return False

        if sample is None:

            sample = {
                "timestamp": self._last_collect,
            }

        result = self.add(
            sample,
            value,
            **metadata,
        )

        if result:

            self.record_success()

        else:

            self.record_failure()

        return result


# ==============================================================================
# Part 6. Sample API
# ==============================================================================

    def add(
        self,
        sample: MetricSample | str,
        value: Any | None = None,
        **metadata: Any,
    ) -> bool:

        if self.size >= self._collect_limit:
            return False

        if isinstance(sample, dict):

            item = dict(sample)

        else:

            item = {
                "name": sample,
                "value": value,
            }

            if metadata:
                item.update(metadata)

        self._samples.append(item)

        return True


    def add_many(
        self,
        samples: SampleList,
    ) -> int:

        count = 0

        for sample in samples:

            if self.add(sample):

                count += 1

        return count


    def append(
        self,
        sample: MetricSample | str,
        value: Any | None = None,
        **metadata: Any,
    ) -> bool:

        return self.add(
            sample,
            value,
            **metadata,
        )


    def extend(
        self,
        samples: SampleList,
    ) -> int:

        return self.add_many(samples)


    def remove(
        self,
        sample: MetricSample,
    ) -> bool:

        try:

            self._samples.remove(sample)

            return True

        except ValueError:

            return False


    def pop(
        self,
        index: int = -1,
    ) -> MetricSample | None:

        if not self._samples:

            return None

        return self._samples.pop(index)


    def latest(self) -> MetricSample | None:

        if not self._samples:

            return None

        return self._samples[-1]


    def first(self) -> MetricSample | None:

        if not self._samples:

            return None

        return self._samples[0]


    def get(
        self,
        index: int,
        default: Any = None,
    ) -> Any:

        try:

            return self._samples[index]

        except IndexError:

            return default


    def samples_list(self) -> SampleList:

        return copy.deepcopy(self._samples)


    def clear_samples(self):

        self._samples.clear()

        return self


    def has_samples(self) -> bool:

        return bool(self._samples)


    def sample_count(self) -> int:

        return self.size


# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    def record_success(self):

        self._collected += 1

        self._successes += 1

        return self


    def record_failure(self):

        self._failed += 1

        self._failures += 1

        return self


    def success_rate(self) -> float:

        total = self.total_processed()

        if total == 0:

            return 0.0

        return self._successes / total


    def failure_rate(self) -> float:

        total = self.total_processed()

        if total == 0:

            return 0.0

        return self._failures / total


    def total_processed(self) -> int:

        return self._successes + self._failures


    def statistics(self) -> CollectorStats:

        return {
            "collected": self._collected,
            "failed": self._failed,
            "successes": self._successes,
            "failures": self._failures,
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
            "size": self.size,
        }


    def reset_statistics(self):

        self._collected = DEFAULT_COLLECTED

        self._failed = DEFAULT_FAILED

        self._successes = DEFAULT_SUCCESS

        self._failures = DEFAULT_FAILURE

        return self


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self):

        return self.from_dict(
            self.to_dict(),
        )


    def copy(self):

        return self.clone()


    def merge(
        self,
        other: "RuntimeCollector",
    ):

        self.extend(
            other.samples,
        )

        self._collected += other.collected

        self._failed += other.failed

        self._successes += other.successes

        self._failures += other.failures

        return self


    def update(
        self,
        values: MetricSample | SampleList,
    ):

        if isinstance(values, dict):

            self.add(values)

        else:

            self.extend(values)

        return self


    def snapshot(self) -> CollectorState:

        return self.to_dict()


    def restore(
        self,
        state: CollectorState,
    ):

        restored = self.from_dict(state)

        self._name = restored._name

        self._enabled = restored._enabled

        self._started = restored._started

        self._collect_limit = restored._collect_limit

        self._interval = restored._interval

        self._samples = copy.deepcopy(restored._samples)

        self._collected = restored._collected

        self._failed = restored._failed

        self._successes = restored._successes

        self._failures = restored._failures

        self._created_at = restored._created_at

        self._last_collect = restored._last_collect

        return self

# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate_name(
        self,
        name: str | None = None,
    ) -> bool:

        value = self._name if name is None else name

        return (
            isinstance(value, str)
            and bool(value.strip())
        )


    def validate_samples(
        self,
        samples: SampleList | None = None,
    ) -> bool:

        values = self._samples if samples is None else samples

        return isinstance(values, list)


    def validate_limits(self) -> bool:

        return (
            self._collect_limit > 0
            and self._interval > 0.0
        )


    def validate(self) -> bool:

        return (
            self.validate_name()
            and self.validate_samples()
            and self.validate_limits()
        )


    def normalize(
        self,
        sample: MetricSample | None = None,
    ) -> MetricSample:

        if sample is None:

            return {}

        return dict(sample)


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> CollectorState:

        return {
            "name": self.name,
            "enabled": self.enabled,
            "started": self.started,
            "collect_limit": self.collect_limit,
            "interval": self.interval,
            "samples": copy.deepcopy(self._samples),
            "collected": self.collected,
            "failed": self.failed,
            "successes": self.successes,
            "failures": self.failures,
            "created_at": self.created_at,
            "last_collect": self.last_collect,
        }


    @classmethod
    def from_dict(
        cls,
        data: CollectorState,
    ) -> "RuntimeCollector":

        collector = cls(
            name=data["name"],
            enabled=data["enabled"],
            started=data["started"],
            collect_limit=data["collect_limit"],
            interval=data["interval"],
        )

        collector._samples = copy.deepcopy(
            data["samples"]
        )

        collector._collected = data["collected"]

        collector._failed = data["failed"]

        collector._successes = data["successes"]

        collector._failures = data["failures"]

        collector._created_at = data["created_at"]

        collector._last_collect = data["last_collect"]

        return collector


    def to_tuple(self):

        return (
            self.name,
            self.enabled,
            self.started,
            self.collect_limit,
            self.interval,
            tuple(copy.deepcopy(self._samples)),
            self.collected,
            self.failed,
            self.successes,
            self.failures,
            self.created_at,
            self.last_collect,
        )


    @classmethod
    def from_tuple(
        cls,
        data,
    ) -> "RuntimeCollector":

        collector = cls(
            name=data[0],
            enabled=data[1],
            started=data[2],
            collect_limit=data[3],
            interval=data[4],
        )

        collector._samples = list(data[5])

        collector._collected = data[6]

        collector._failed = data[7]

        collector._successes = data[8]

        collector._failures = data[9]

        collector._created_at = data[10]

        collector._last_collect = data[11]

        return collector


    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
        )


    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "RuntimeCollector":

        return cls.from_dict(
            json.loads(payload),
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self):

        return {
            "name": self.name,
            "size": self.size,
            "collected": self.collected,
            "failed": self.failed,
        }


    def diagnostics(self):

        return {
            "status": self.status(),
            "enabled": self.enabled,
            "started": self.started,
            "utilization": self.utilization,
            "statistics": self.statistics(),
        }


    def report(self):

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }


    def status(self) -> str:

        if not self.enabled:
            return "disabled"

        if self.started:
            return "started"

        return "ready"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self):

        return self.size


    def __contains__(
        self,
        item,
    ):

        return item in self._samples


    def __iter__(self) -> Iterator[MetricSample]:

        return iter(self._samples)


    def __hash__(self):

        return hash(
            (
                self.name,
                self.collect_limit,
                self.interval,
            )
        )


    def __eq__(
        self,
        other,
    ):

        if not isinstance(
            other,
            RuntimeCollector,
        ):
            return False

        return (
            self.to_dict()
            == other.to_dict()
        )


    def __repr__(self):

        return (
            f"RuntimeCollector("
            f"name={self.name!r}, "
            f"size={self.size}, "
            f"enabled={self.enabled})"
        )


    def __str__(self):

        return (
            f"{self.name}"
            f"(samples={self.size})"
        )


    def __bool__(self):

        return self.validate()                