"""
SciOS Observability
==================

Metric Registry.

Central runtime registry responsible for managing all metrics
within the SciOS Observability subsystem.

Responsibilities
----------------
- Metric registration
- Metric lookup
- Runtime indexing
- Snapshot support
- Validation
- Thread-safe access

The registry does not perform aggregation or collection.
Those responsibilities belong to MetricCollector and
MetricManager.
"""

from __future__ import annotations


# ==========================================================
# Part 2 — Imports
# ==========================================================

from copy import deepcopy

from threading import RLock

from typing import Any
from typing import Final
from typing import TypeAlias
from typing import Iterator
from typing import Iterable
from typing import MutableMapping

from uuid import UUID

from .metric import Metric
from .metric_snapshot import MetricSnapshot


# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "REGISTRY_VERSION",
    "DEFAULT_REGISTRY_NAME",
    "DEFAULT_REGISTRY_CAPACITY",
    "MetricKey",
    "MetricMap",
    "MetricRegistry",
]


# ==========================================================
# Part 4 — Version / Constants / Type Aliases
# ==========================================================

REGISTRY_VERSION: Final[str] = "1.0.0"

DEFAULT_REGISTRY_NAME: Final[str] = "default"

DEFAULT_REGISTRY_CAPACITY: Final[int] = 100000

DEFAULT_THREAD_SAFE: Final[bool] = True

DEFAULT_AUTO_REPLACE: Final[bool] = False

DEFAULT_ALLOW_DUPLICATE_NAMES: Final[bool] = False


MetricKey: TypeAlias = str | UUID

MetricMap: TypeAlias = MutableMapping[str, Metric]

MetricIterator: TypeAlias = Iterator[Metric]

MetricIterable: TypeAlias = Iterable[Metric]

MetricSnapshotMap: TypeAlias = dict[str, MetricSnapshot]

MetricStatistics: TypeAlias = dict[str, Any]
# ==========================================================
# Part 5 — RegistryEvent
# ==========================================================

from enum import Enum
from enum import auto


class RegistryEvent(Enum):
    """
    Registry lifecycle events.
    """

    REGISTER = auto()

    UNREGISTER = auto()

    REPLACE = auto()

    CLEAR = auto()

    RESTORE = auto()

    RESET = auto()


# ==========================================================
# Part 6 — MetricRegistry
# ==========================================================


class MetricRegistry:
    """
    Thread-safe runtime metric registry.
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        *,
        name: str = DEFAULT_REGISTRY_NAME,
        capacity: int = DEFAULT_REGISTRY_CAPACITY,
        thread_safe: bool = DEFAULT_THREAD_SAFE,
        auto_replace: bool = DEFAULT_AUTO_REPLACE,
        allow_duplicate_names: bool = DEFAULT_ALLOW_DUPLICATE_NAMES,
    ) -> None:

        self._name: str = name

        self._capacity: int = max(
            1,
            int(capacity),
        )

        self._thread_safe: bool = bool(
            thread_safe,
        )

        self._auto_replace: bool = bool(
            auto_replace,
        )

        self._allow_duplicate_names: bool = bool(
            allow_duplicate_names,
        )

        self._metrics: MetricMap = {}

        self._revision: int = 0

        self._lock = RLock()

    # ======================================================
    # Properties
    # ======================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def thread_safe(self) -> bool:
        return self._thread_safe

    @property
    def auto_replace(self) -> bool:
        return self._auto_replace

    @property
    def allow_duplicate_names(self) -> bool:
        return self._allow_duplicate_names

    @property
    def metrics(self) -> MetricMap:
        """
        Read-only registry mapping.
        """
        return self._metrics.copy()


# ==========================================================
# Part 7 — Registration API
# ==========================================================

    def register(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Register a metric.
        """

        key = metric.descriptor.name

        with self._lock:

            if (
                not self._allow_duplicate_names
                and key in self._metrics
            ):
                if self._auto_replace:
                    self.replace(metric)
                    return metric

                raise KeyError(
                    f"Metric '{key}' already exists."
                )

            if len(self._metrics) >= self._capacity:
                raise RuntimeError(
                    "Registry capacity exceeded."
                )

            self._metrics[key] = metric

            self._revision += 1

        return metric

    def unregister(
        self,
        key: MetricKey,
    ) -> Metric:
        """
        Remove metric from registry.
        """

        name = str(key)

        with self._lock:

            metric = self._metrics.pop(name)

            self._revision += 1

            return metric

    def replace(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Replace existing metric.
        """

        key = metric.descriptor.name

        with self._lock:

            self._metrics[key] = metric

            self._revision += 1

        return metric

    def contains(
        self,
        key: MetricKey,
    ) -> bool:
        """
        Check registry membership.
        """

        return str(key) in self._metrics
# ==========================================================
# Part 8 — Lookup API
# ==========================================================

    def get(
        self,
        key: MetricKey,
        default: Metric | None = None,
    ) -> Metric | None:
        """
        Return metric or default.
        """
        return self._metrics.get(
            str(key),
            default,
        )

    def require(
        self,
        key: MetricKey,
    ) -> Metric:
        """
        Return metric.

        Raises
        ------
        KeyError
            If metric does not exist.
        """
        metric = self.get(key)

        if metric is None:
            raise KeyError(
                f"Metric '{key}' not found."
            )

        return metric

    def find(
        self,
        predicate,
    ) -> list[Metric]:
        """
        Find metrics satisfying predicate.
        """
        return [
            metric
            for metric in self._metrics.values()
            if predicate(metric)
        ]

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Registered metric names.
        """
        return tuple(
            self._metrics.keys()
        )

    def ids(
        self,
    ) -> tuple[MetricID, ...]:
        """
        Registered metric ids.
        """
        return tuple(
            metric.id
            for metric in self._metrics.values()
        )


# ==========================================================
# Part 9 — Iteration API
# ==========================================================

    def metrics(
        self,
    ) -> tuple[Metric, ...]:
        """
        All registered metrics.
        """
        return tuple(
            self._metrics.values()
        )

    def values(
        self,
    ) -> tuple[Metric, ...]:
        """
        Alias of metrics().
        """
        return self.metrics()

    def items(
        self,
    ) -> tuple[tuple[str, Metric], ...]:
        """
        Registry items.
        """
        return tuple(
            self._metrics.items()
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all metrics.
        """
        with self._lock:

            self._metrics.clear()

            self._revision += 1


# ==========================================================
# Part 10 — Snapshot API
# ==========================================================

    def snapshot(
        self,
    ) -> MetricSnapshotMap:
        """
        Create registry snapshot.
        """
        return {
            name: metric.snapshot()
            for name, metric in self._metrics.items()
        }

    def restore(
        self,
        snapshot: MetricSnapshotMap,
    ) -> None:
        """
        Restore registry from snapshot.
        """
        with self._lock:

            for name, state in snapshot.items():

                if name in self._metrics:

                    self._metrics[name].restore(
                        state,
                    )

            self._revision += 1

    def copy(
        self,
    ) -> "MetricRegistry":
        """
        Shallow registry copy.
        """
        registry = self.__class__(
            name=self._name,
            capacity=self._capacity,
            thread_safe=self._thread_safe,
            auto_replace=self._auto_replace,
            allow_duplicate_names=self._allow_duplicate_names,
        )

        registry._metrics = self._metrics.copy()
        registry._revision = self._revision

        return registry

    def clone(
        self,
    ) -> "MetricRegistry":
        """
        Deep registry clone.
        """
        registry = self.__class__(
            name=self._name,
            capacity=self._capacity,
            thread_safe=self._thread_safe,
            auto_replace=self._auto_replace,
            allow_duplicate_names=self._allow_duplicate_names,
        )

        registry._metrics = {
            name: metric.clone()
            for name, metric in self._metrics.items()
        }

        registry._revision = self._revision

        return registry
# ==========================================================
# Part 11 — Statistics
# ==========================================================

    def size(
        self,
    ) -> int:
        """
        Number of registered metrics.
        """
        return len(self._metrics)

    def empty(
        self,
    ) -> bool:
        """
        Whether the registry is empty.
        """
        return not self._metrics

    def summary(
        self,
    ) -> MetricStatistics:
        """
        Registry summary.
        """
        return {
            "name": self._name,
            "version": REGISTRY_VERSION,
            "size": self.size(),
            "capacity": self._capacity,
            "revision": self._revision,
            "thread_safe": self._thread_safe,
            "auto_replace": self._auto_replace,
            "allow_duplicate_names": self._allow_duplicate_names,
            "empty": self.empty(),
        }


# ==========================================================
# Part 12 — Validation
# ==========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate registry integrity.
        """
        if self._capacity <= 0:
            raise ValueError(
                "Registry capacity must be positive."
            )

        if len(self._metrics) > self._capacity:
            raise RuntimeError(
                "Registry exceeds configured capacity."
            )

        for name, metric in self._metrics.items():

            if not isinstance(name, str):
                raise TypeError(
                    "Registry keys must be strings."
                )

            if not isinstance(metric, Metric):
                raise TypeError(
                    f"'{name}' is not a Metric instance."
                )

    def is_valid(
        self,
    ) -> bool:
        """
        Safe validation.
        """
        try:
            self.validate()
            return True
        except Exception:
            return False


# ==========================================================
# Part 13 — Python Protocols
# ==========================================================

    def __len__(
        self,
    ) -> int:
        return self.size()

    def __iter__(
        self,
    ) -> MetricIterator:
        return iter(
            self._metrics.values()
        )

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return (
            isinstance(key, (str, UUID))
            and str(key) in self._metrics
        )

    def __getitem__(
        self,
        key: MetricKey,
    ) -> Metric:
        return self.require(key)

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"size={self.size()}, "
            f"capacity={self._capacity}, "
            f"revision={self._revision})"
        )

    def __str__(
        self,
    ) -> str:
        return (
            f"{self._name}"
            f" ({self.size()} metrics)"
        )


# ==========================================================
# Part 14 — Final cleanup
# ==========================================================

__all__ = [
    "REGISTRY_VERSION",
    "DEFAULT_REGISTRY_NAME",
    "DEFAULT_REGISTRY_CAPACITY",
    "MetricKey",
    "MetricMap",
    "MetricIterator",
    "MetricIterable",
    "MetricSnapshotMap",
    "MetricStatistics",
    "RegistryEvent",
    "MetricRegistry",
]                