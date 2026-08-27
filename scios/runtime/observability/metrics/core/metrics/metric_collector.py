"""
SciOS Observability
==================

Metric Collector.

Thread-safe runtime metric collection engine.

Responsibilities
----------------
- Collect runtime metrics
- Aggregate metric streams
- Batch collection
- Snapshot production
- Registry integration
- Filtering
- Collection statistics

The collector performs no metric computation.
Metric computation belongs to Metric implementations.
"""

from __future__ import annotations


# ==========================================================
# Part 2 â€” Imports
# ==========================================================

from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator

from threading import RLock

from typing import Any
from typing import Final
from typing import TypeAlias

from .metric import Metric
from .metric_snapshot import MetricSnapshot
from .metric_registry import MetricRegistry

from copy import deepcopy

# ==========================================================
# Part 3 â€” Public API
# ==========================================================

__all__ = [
    "COLLECTOR_VERSION",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_AUTO_RESET",
    "DEFAULT_THREAD_SAFE",
    "CollectorFilter",
    "MetricSequence",
    "MetricSnapshotSequence",
    "CollectionStatistics",
    "MetricCollector",
]


# ==========================================================
# Part 4 â€” Version / Constants / Type Aliases
# ==========================================================

COLLECTOR_VERSION: Final[str] = "1.0.0"

DEFAULT_BATCH_SIZE: Final[int] = 1024

DEFAULT_AUTO_RESET: Final[bool] = False

DEFAULT_THREAD_SAFE: Final[bool] = True


CollectorFilter: TypeAlias = Callable[[Metric], bool]

MetricSequence: TypeAlias = list[Metric]

MetricSnapshotSequence: TypeAlias = list[MetricSnapshot]

CollectionStatistics: TypeAlias = dict[str, Any]
# ==========================================================
# Part 5 â€” CollectorEvent
# ==========================================================

from enum import Enum
from enum import auto


class CollectorEvent(Enum):
    """
    Collector lifecycle events.
    """

    CREATED = auto()
    REGISTRY_ATTACHED = auto()
    REGISTRY_DETACHED = auto()
    COLLECT_STARTED = auto()
    COLLECT_FINISHED = auto()
    SNAPSHOT_CREATED = auto()
    CLEARED = auto()


# ==========================================================
# Part 6 â€” MetricCollector
# ==========================================================


class MetricCollector:
    """
    Thread-safe runtime metric collector.
    """

    def __init__(
        self,
        *,
        registry: MetricRegistry | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        auto_reset: bool = DEFAULT_AUTO_RESET,
        thread_safe: bool = DEFAULT_THREAD_SAFE,
    ) -> None:

        self._registry = registry

        self._batch_size = max(1, int(batch_size))

        self._auto_reset = bool(auto_reset)

        self._thread_safe = bool(thread_safe)

        self._lock = RLock()

        self._revision = 0

        self._statistics: CollectionStatistics = {}

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def registry(
        self,
    ) -> MetricRegistry | None:
        return self._registry

    @property
    def batch_size(
        self,
    ) -> int:
        return self._batch_size

    @property
    def auto_reset(
        self,
    ) -> bool:
        return self._auto_reset

    @property
    def thread_safe(
        self,
    ) -> bool:
        return self._thread_safe

    @property
    def revision(
        self,
    ) -> int:
        return self._revision


# ==========================================================
# Part 7 â€” Registry API
# ==========================================================

    def attach_registry(
        self,
        registry: MetricRegistry,
    ) -> None:

        self._registry = registry
        self._revision += 1

    def detach_registry(
        self,
    ) -> MetricRegistry | None:

        registry = self._registry
        self._registry = None
        self._revision += 1
        return registry

    def has_registry(
        self,
    ) -> bool:

        return self._registry is not None

    def registry_or_raise(
        self,
    ) -> MetricRegistry:

        if self._registry is None:
            raise RuntimeError(
                "MetricCollector has no attached registry."
            )

        return self._registry
    # ======================================================
    # Part 8 â€” Lookup API
    # ======================================================

    def register(
        self,
        metric: Metric,
    ) -> Metric:
        """
        Register a metric in the attached registry.

        The collector delegates ownership and duplicate detection
        to MetricRegistry.
        """

        if metric is None:
            raise ValueError(
                "metric must not be None."
            )

        registry = self.registry_or_raise()

        with self._lock:
            registry.register(metric)
            self._revision += 1

        return metric

    def remove(
        self,
        name: str,
    ) -> Metric | None:
        """
        Remove a metric by name.

        Returns the removed metric, or None if it does not exist.
        """

        registry = self.registry_or_raise()

        with self._lock:
            metric = registry.get(name)

            if metric is None:
                return None

            registry.remove(name)
            self._revision += 1

            return metric

    def get(
        self,
        name: str,
        default: Metric | None = None,
    ) -> Metric | None:
        """
        Return metric by name.
        """

        registry = self.registry

        if registry is None:
            return default

        return registry.get(
            name,
            default,
        )

    def require(
        self,
        name: str,
    ) -> Metric:
        """
        Return metric or raise KeyError.
        """

        registry = self.registry_or_raise()

        return registry.require(
            name,
        )

    def find(
        self,
        predicate: CollectorFilter,
    ) -> MetricSequence:
        """
        Find metrics matching predicate.
        """

        registry = self.registry

        if registry is None:
            return []

        return [
            metric
            for metric in registry.values()
            if predicate(metric)
        ]

    def names(
        self,
    ) -> list[str]:
        """
        Return registered metric names.
        """

        registry = self.registry

        if registry is None:
            return []

        return list(
            registry.names()
        )

    def ids(
        self,
    ) -> list[str]:
        """
        Return registered metric ids.
        """

        registry = self.registry

        if registry is None:
            return []

        return [
            str(metric.id)
            for metric in registry.values()
        ]


    # ======================================================
    # Part 9 â€” Iteration API
    # ======================================================

    def metrics(
        self,
    ) -> Iterator[Metric]:
        """
        Iterate over metrics.
        """

        registry = self.registry

        if registry is None:
            return iter(())

        return iter(
            registry.values()
        )

    def values(
        self,
    ) -> MetricSequence:
        """
        Return metrics.
        """

        return list(
            self.metrics()
        )

    def items(
        self,
    ) -> list[tuple[str, Metric]]:
        """
        Return (name, metric) pairs.
        """

        registry = self.registry

        if registry is None:
            return []

        return list(
            registry.items()
        )

    def clear(
        self,
    ) -> None:
        """
        Clear attached registry.
        """

        registry = self.registry

        if registry is None:
            return

        registry.clear()

        self._revision += 1


    # ======================================================
    # Part 10 â€” Snapshot API
    # ======================================================

    def snapshot(
        self,
    ) -> MetricSnapshotSequence:
        """
        Snapshot all metrics.
        """

        return [
            metric.snapshot()
            for metric in self.metrics()
        ]

    def restore(
        self,
        snapshots: Iterable[MetricSnapshot],
    ) -> None:
        """
        Restore metrics from snapshots.
        """

        registry = self.registry_or_raise()

        for snapshot in snapshots:

            metric = registry.get(
                snapshot.descriptor.name,
            )

            if metric is not None:
                metric.restore(
                    snapshot,
                )

        self._revision += 1

    def copy(
        self,
    ) -> "MetricCollector":
        """
        Shallow collector copy.
        """

        clone = MetricCollector(
            registry=self._registry,
            batch_size=self._batch_size,
            auto_reset=self._auto_reset,
            thread_safe=self._thread_safe,
        )

        clone._revision = self._revision

        clone._statistics = dict(
            self._statistics,
        )

        return clone

    def clone(
        self,
    ) -> "MetricCollector":
        """
        Deep collector clone.
        """

        return deepcopy(
            self,
        )
    # ======================================================
    # Part 11 â€” Statistics
    # ======================================================

    def size(
        self,
    ) -> int:
        """
        Return number of registered metrics.
        """

        registry = self.registry

        return 0 if registry is None else len(registry)

    def empty(
        self,
    ) -> bool:
        """
        Return True if collector has no metrics.
        """

        return self.size() == 0

    def summary(
        self,
    ) -> CollectionStatistics:
        """
        Collector summary.
        """

        return {
            "version": COLLECTOR_VERSION,
            "registry_attached": self.has_registry(),
            "metric_count": self.size(),
            "batch_size": self._batch_size,
            "auto_reset": self._auto_reset,
            "thread_safe": self._thread_safe,
            "revision": self._revision,
            "statistics": dict(self._statistics),
        }


    # ======================================================
    # Part 12 â€” Validation
    # ======================================================

    def validate(
        self,
    ) -> None:
        """
        Validate collector configuration.
        """

        if self._batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        if self._registry is not None:
            validator = getattr(
                self._registry,
                "validate",
                None,
            )

            if callable(validator):
                validator()

    def is_valid(
        self,
    ) -> bool:
        """
        Return True if collector is valid.
        """

        try:
            self.validate()
            return True
        except Exception:
            return False


    # ======================================================
    # Part 13 â€” Python Protocols
    # ======================================================

    def __len__(
        self,
    ) -> int:

        return self.size()

    def __iter__(
        self,
    ) -> Iterator[Metric]:

        return self.metrics()

    def __contains__(
        self,
        item: object,
    ) -> bool:

        if isinstance(item, str):
            return self.get(item) is not None

        if isinstance(item, Metric):
            return any(
                metric.id == item.id
                for metric in self.metrics()
            )

        return False

    def __getitem__(
        self,
        name: str,
    ) -> Metric:

        return self.require(name)

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"metrics={self.size()}, "
            f"batch_size={self._batch_size}, "
            f"revision={self._revision})"
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"MetricCollector("
            f"{self.size()} metrics)"
        )


# ==========================================================
# Part 14 â€” Final Cleanup
# ==========================================================

__all__ = [
    "CollectorEvent",
    "MetricCollector",
    "COLLECTOR_VERSION",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_AUTO_RESET",
    "DEFAULT_THREAD_SAFE",
    "CollectorFilter",
    "MetricSequence",
    "MetricSnapshotSequence",
    "CollectionStatistics",
]