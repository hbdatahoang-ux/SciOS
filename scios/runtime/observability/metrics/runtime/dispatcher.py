"""
SciOS Runtime Dispatcher
========================

Runtime metric dispatcher.

Python 3.11+
"""

# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations

import copy
import json
import time

from typing import Any
from typing import TypeAlias

from .collector import RuntimeCollector
from .aggregator import RuntimeAggregator

# ==============================================================================
# Part 2. Constants
# ==============================================================================

DEFAULT_NAME: str = "dispatcher"

DEFAULT_ENABLED: bool = True

DEFAULT_QUEUE_LIMIT: int = 1024

DEFAULT_DISPATCHED: int = 0

DEFAULT_FAILED: int = 0

DEFAULT_RETRIES: int = 3

DEFAULT_BATCH_SIZE: int = 100

DEFAULT_TIMEOUT: float = 5.0


__all__ = [
    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_QUEUE_LIMIT",
    "DEFAULT_DISPATCHED",
    "DEFAULT_FAILED",
    "DEFAULT_RETRIES",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_TIMEOUT",
    "DispatchItem",
    "DispatchQueue",
    "DispatchResult",
    "DispatcherState",
    "DispatcherStats",
    "RuntimeDispatcher",
]


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================

DispatchItem: TypeAlias = dict[str, Any]

DispatchQueue: TypeAlias = list[DispatchItem]

DispatchResult: TypeAlias = dict[str, Any]

DispatcherState: TypeAlias = dict[str, Any]

DispatcherStats: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 4. RuntimeDispatcher
# ==============================================================================


class RuntimeDispatcher:
    """
    Runtime dispatcher.

    Maintains an in-memory dispatch queue between
    RuntimeCollector -> RuntimeAggregator -> exporters.
    """

    __slots__ = (
        "_name",
        "_enabled",
        "_collector",
        "_aggregator",
        "_queue",
        "_dispatched",
        "_failed",
        "_created_at",
        "_last_dispatch",
        "_queue_limit",
        "_batch_size",
        "_timeout",
        "_retries",
    )

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        collector: RuntimeCollector | None = None,
        aggregator: RuntimeAggregator | None = None,
        queue_limit: int = DEFAULT_QUEUE_LIMIT,
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:

        self._name = str(name)
        self._enabled = bool(enabled)

        self._collector = (
            collector
            if collector is not None
            else RuntimeCollector()
        )

        self._aggregator = (
            aggregator
            if aggregator is not None
            else RuntimeAggregator(
                collector=self._collector,
            )
        )

        self._queue: DispatchQueue = []

        self._dispatched = DEFAULT_DISPATCHED
        self._failed = DEFAULT_FAILED

        self._created_at = time.time()
        self._last_dispatch: float | None = None

        self._queue_limit = max(
            1,
            int(queue_limit),
        )

        self._batch_size = max(
            1,
            int(batch_size),
        )

        self._timeout = max(
            0.0,
            float(timeout),
        )

        self._retries = max(
            0,
            int(retries),
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(
        self,
        value: str,
    ) -> None:
        self._name = str(value)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:
        self._enabled = bool(value)

    @property
    def collector(self) -> RuntimeCollector:
        return self._collector

    @collector.setter
    def collector(
        self,
        value: RuntimeCollector,
    ) -> None:
        self._collector = value

    @property
    def aggregator(self) -> RuntimeAggregator:
        return self._aggregator

    @aggregator.setter
    def aggregator(
        self,
        value: RuntimeAggregator,
    ) -> None:
        self._aggregator = value

    @property
    def queue(self) -> DispatchQueue:
        return self._queue

    @property
    def dispatched(self) -> int:
        return self._dispatched

    @property
    def failed(self) -> int:
        return self._failed

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def last_dispatch(self) -> float | None:
        return self._last_dispatch

    @property
    def queue_limit(self) -> int:
        return self._queue_limit

    @queue_limit.setter
    def queue_limit(
        self,
        value: int,
    ) -> None:
        self._queue_limit = max(
            1,
            int(value),
        )

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @batch_size.setter
    def batch_size(
        self,
        value: int,
    ) -> None:
        self._batch_size = max(
            1,
            int(value),
        )

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(
        self,
        value: float,
    ) -> None:
        self._timeout = max(
            0.0,
            float(value),
        )

    @property
    def retries(self) -> int:
        return self._retries

    @retries.setter
    def retries(
        self,
        value: int,
    ) -> None:
        self._retries = max(
            0,
            int(value),
        )

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

    def enable(self) -> "RuntimeDispatcher":
        self._enabled = True
        return self

    def disable(self) -> "RuntimeDispatcher":
        self._enabled = False
        return self

    def clear(self) -> "RuntimeDispatcher":
        self._queue.clear()
        return self

    def reset(self) -> "RuntimeDispatcher":
        self.clear()

        self._dispatched = DEFAULT_DISPATCHED
        self._failed = DEFAULT_FAILED
        self._last_dispatch = None

        return self

    def dispatch(self) -> bool:
        if not self._enabled:
            return False

        if not self._queue:
            return True

        self.dispatch_batch()

        self._last_dispatch = time.time()

        return True


# ==============================================================================
# Part 6. Dispatch API
# ==============================================================================

    def enqueue(
        self,
        item: DispatchItem,
    ) -> bool:

        if len(self._queue) >= self._queue_limit:
            self._failed += 1
            return False

        self._queue.append(dict(item))

        return True

    def enqueue_many(
        self,
        items: DispatchQueue,
    ) -> int:

        added = 0

        for item in items:
            if self.enqueue(item):
                added += 1

        return added

    def dequeue(self) -> DispatchItem | None:

        if not self._queue:
            return None

        return self._queue.pop(0)

    def peek(self) -> DispatchItem | None:

        if not self._queue:
            return None

        return self._queue[0]

    def dispatch_item(
        self,
        item: DispatchItem,
    ) -> bool:

        try:
            self._aggregator.aggregate_sample(item)

            self._dispatched += 1

            return True

        except Exception:

            self._failed += 1

            return False

    def dispatch_batch(self) -> int:

        processed = 0

        while self._queue and processed < self._batch_size:

            item = self.dequeue()

            if item is None:
                break

            self.dispatch_item(item)

            processed += 1

        self._last_dispatch = time.time()

        return processed

    def flush(self) -> int:

        total = 0

        while self._queue:
            total += self.dispatch_batch()

        return total

    def pending(self) -> DispatchQueue:
        return list(self._queue)

    def has_pending(self) -> bool:
        return bool(self._queue)

    def queue_size(self) -> int:
        return len(self._queue)


# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    def success_rate(self) -> float:

        total = self.total_processed()

        if total == 0:
            return 0.0

        return self._dispatched / total

    def failure_rate(self) -> float:

        total = self.total_processed()

        if total == 0:
            return 0.0

        return self._failed / total

    def total_processed(self) -> int:
        return self._dispatched + self._failed

    def statistics(self) -> DispatcherStats:

        return {
            "dispatched": self._dispatched,
            "failed": self._failed,
            "pending": len(self._queue),
            "total": self.total_processed(),
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
        }

    def reset_statistics(self) -> "RuntimeDispatcher":

        self._dispatched = DEFAULT_DISPATCHED
        self._failed = DEFAULT_FAILED

        return self


# ==============================================================================
# Part 8. Operations
# ==============================================================================

    def clone(self) -> "RuntimeDispatcher":
        return copy.deepcopy(self)

    def copy(self) -> "RuntimeDispatcher":
        return self.clone()

    def merge(
        self,
        other: "RuntimeDispatcher",
    ) -> "RuntimeDispatcher":

        self.enqueue_many(other.pending())

        self._dispatched += other.dispatched
        self._failed += other.failed

        return self

    def update(
        self,
        state: DispatcherState,
    ) -> "RuntimeDispatcher":

        for key, value in state.items():

            attribute = f"_{key}"

            if hasattr(self, attribute):
                setattr(self, attribute, value)

        return self

    def snapshot(self) -> DispatcherState:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "queue": copy.deepcopy(self._queue),
            "dispatched": self._dispatched,
            "failed": self._failed,
            "created_at": self._created_at,
            "last_dispatch": self._last_dispatch,
            "queue_limit": self._queue_limit,
            "batch_size": self._batch_size,
            "timeout": self._timeout,
            "retries": self._retries,
        }

    def restore(
        self,
        state: DispatcherState,
    ) -> "RuntimeDispatcher":

        self._name = state["name"]
        self._enabled = state["enabled"]
        self._queue = copy.deepcopy(state["queue"])
        self._dispatched = state["dispatched"]
        self._failed = state["failed"]
        self._created_at = state["created_at"]
        self._last_dispatch = state["last_dispatch"]
        self._queue_limit = state["queue_limit"]
        self._batch_size = state["batch_size"]
        self._timeout = state["timeout"]
        self._retries = state["retries"]

        return self

# ==============================================================================
# Part 9. Validation
# ==============================================================================

    def validate(self) -> bool:

        if self._queue_limit <= 0:
            return False

        if self._batch_size <= 0:
            return False

        if self._timeout < 0:
            return False

        if self._retries < 0:
            return False

        return True

    def normalize(
        self,
        value: Any,
    ) -> Any:

        if isinstance(value, float):

            if value != value:  # NaN
                return 0.0

            if value == float("inf"):
                return 0.0

            if value == float("-inf"):
                return 0.0

        return value


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

    def to_dict(self) -> DispatcherState:
        return self.snapshot()

    @classmethod
    def from_dict(
        cls,
        state: DispatcherState,
    ) -> "RuntimeDispatcher":

        dispatcher = cls()

        dispatcher.restore(state)

        return dispatcher

    def to_tuple(self) -> tuple[Any, ...]:

        return (
            self._name,
            self._enabled,
            copy.deepcopy(self._queue),
            self._dispatched,
            self._failed,
            self._created_at,
            self._last_dispatch,
            self._queue_limit,
            self._batch_size,
            self._timeout,
            self._retries,
        )

    @classmethod
    def from_tuple(
        cls,
        value: tuple[Any, ...],
    ) -> "RuntimeDispatcher":

        (
            name,
            enabled,
            queue,
            dispatched,
            failed,
            created_at,
            last_dispatch,
            queue_limit,
            batch_size,
            timeout,
            retries,
        ) = value

        dispatcher = cls(
            name=name,
            enabled=enabled,
            queue_limit=queue_limit,
            batch_size=batch_size,
            timeout=timeout,
            retries=retries,
        )

        dispatcher._queue = copy.deepcopy(queue)
        dispatcher._dispatched = dispatched
        dispatcher._failed = failed
        dispatcher._created_at = created_at
        dispatcher._last_dispatch = last_dispatch

        return dispatcher

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=2,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "RuntimeDispatcher":

        return cls.from_dict(
            json.loads(payload),
        )


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

    def summary(self) -> dict[str, Any]:

        return {
            "name": self._name,
            "enabled": self._enabled,
            "queue_size": len(self._queue),
            "processed": self.total_processed(),
        }

    def diagnostics(self) -> DispatcherStats:

        diagnostics = self.statistics()

        diagnostics["valid"] = self.validate()

        diagnostics["created_at"] = self._created_at
        diagnostics["last_dispatch"] = self._last_dispatch

        return diagnostics

    def report(self) -> str:

        return json.dumps(
            self.diagnostics(),
            ensure_ascii=False,
            indent=2,
        )

    def status(self) -> dict[str, Any]:

        return {
            "enabled": self._enabled,
            "pending": len(self._queue),
            "healthy": self.validate(),
        }


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

    def __len__(self) -> int:
        return len(self._queue)

    def __contains__(
        self,
        item: Any,
    ) -> bool:
        return item in self._queue

    def __iter__(self):
        return iter(self._queue)

    def __hash__(self) -> int:
        return hash(
            (
                self._name,
                self._created_at,
            )
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            RuntimeDispatcher,
        ):
            return False

        return self.snapshot() == other.snapshot()

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"queue={len(self._queue)}, "
            f"enabled={self._enabled})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> bool:
        return self._enabled                