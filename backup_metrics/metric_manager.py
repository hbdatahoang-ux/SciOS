"""
SciOS Observability
==================

Metric Manager.

High-level orchestration layer for the SciOS Observability
Metrics subsystem.

Responsibilities
----------------
- Metric lifecycle management
- Registry coordination
- Collection orchestration
- Snapshot management
- Export / import coordination
- Runtime monitoring
- Thread-safe operations

MetricManager is the primary entry point for the
Metrics Core runtime.

It coordinates:

- MetricRegistry
- MetricCollector
- MetricHooks
- MetricMonitor
- MetricSerializer

while remaining independent from concrete metric
implementations.
"""

from __future__ import annotations


# ==========================================================
# Part 2 — Imports
# ==========================================================

from collections.abc import Iterable
from collections.abc import Iterator

from enum import Enum
from enum import auto

from threading import RLock

from typing import Any
from typing import Final
from typing import TypeAlias

from .metric import Metric
from .metric_collector import MetricCollector
from .metric_hooks import MetricHooks
from .metric_registry import MetricRegistry
from .metric_snapshot import MetricSnapshot


# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "MANAGER_VERSION",
    "DEFAULT_MANAGER_NAME",
    "DEFAULT_NAMESPACE",
    "DEFAULT_AUTO_REGISTER",
    "DEFAULT_AUTO_COLLECT",
    "DEFAULT_THREAD_SAFE",
    "ManagerState",
    "ManagerMode",
    "ManagerEvent",
    "MetricManager",
]


# ==========================================================
# Part 4 — Version / Constants / Type Aliases
# ==========================================================

MANAGER_VERSION: Final[str] = "1.0.0"

DEFAULT_MANAGER_NAME: Final[str] = "manager"

DEFAULT_NAMESPACE: Final[str] = "default"

DEFAULT_AUTO_REGISTER: Final[bool] = True

DEFAULT_AUTO_COLLECT: Final[bool] = True

DEFAULT_THREAD_SAFE: Final[bool] = True


MetricName: TypeAlias = str

MetricID: TypeAlias = str

MetricIterable: TypeAlias = Iterable[Metric]

MetricIterator: TypeAlias = Iterator[Metric]

MetricMap: TypeAlias = dict[str, Metric]

SnapshotMap: TypeAlias = dict[str, MetricSnapshot]

ManagerStatistics: TypeAlias = dict[str, Any]
# ==========================================================
# Part 5 — Manager Enums
# ==========================================================

class ManagerState(Enum):
    """
    Runtime lifecycle state.
    """

    CREATED = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    CLOSED = auto()


class ManagerMode(Enum):
    """
    Manager operating mode.
    """

    MANUAL = auto()
    AUTOMATIC = auto()
    READ_ONLY = auto()
    MAINTENANCE = auto()


class ManagerEvent(Enum):
    """
    Manager events.
    """

    REGISTER = auto()
    UNREGISTER = auto()
    REPLACE = auto()

    COLLECT = auto()
    SNAPSHOT = auto()
    RESTORE = auto()

    START = auto()
    STOP = auto()
    PAUSE = auto()
    RESUME = auto()

    RESET = auto()
    CLEAR = auto()

    EXPORT = auto()
    IMPORT = auto()


# ==========================================================
# Part 6 — MetricManager
# ==========================================================


class MetricManager:
    """
    High-level metrics runtime manager.
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        *,
        registry: MetricRegistry | None = None,
        collector: MetricCollector | None = None,
        hooks: MetricHooks | None = None,
        name: str = DEFAULT_MANAGER_NAME,
        namespace: str = DEFAULT_NAMESPACE,
        mode: ManagerMode = ManagerMode.AUTOMATIC,
    ) -> None:

        self._name = name
        self._namespace = namespace

        self._mode = mode
        self._state = ManagerState.CREATED

        self._registry = (
            registry
            if registry is not None
            else MetricRegistry()
        )

        self._collector = (
            collector
            if collector is not None
            else MetricCollector(
                registry=self._registry,
            )
        )

        self._hooks = (
            hooks
            if hooks is not None
            else MetricHooks()
        )

        self._revision = 0

        self._thread_safe = DEFAULT_THREAD_SAFE

        self._lock = RLock()

        self._state = ManagerState.INITIALIZED

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def state(self) -> ManagerState:
        return self._state

    @property
    def mode(self) -> ManagerMode:
        return self._mode

    @property
    def registry(self) -> MetricRegistry:
        return self._registry

    @property
    def collector(self) -> MetricCollector:
        return self._collector

    @property
    def hooks(self) -> MetricHooks:
        return self._hooks

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def thread_safe(self) -> bool:
        return self._thread_safe

    @property
    def metric_count(self) -> int:
        return len(self._registry)


# ==========================================================
# Part 7 — Registry API
# ==========================================================

    def register(
        self,
        metric: Metric,
    ) -> Metric:

        self._registry.register(metric)

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.REGISTER,
            metric,
        )

        return metric

    def unregister(
        self,
        name: str,
    ) -> Metric | None:

        metric = self._registry.unregister(name)

        if metric is not None:

            self._revision += 1

            self._hooks.emit(
                ManagerEvent.UNREGISTER,
                metric,
            )

        return metric

    def replace(
        self,
        metric: Metric,
    ) -> Metric:

        self._registry.replace(metric)

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.REPLACE,
            metric,
        )

        return metric

    def contains(
        self,
        name: str,
    ) -> bool:

        return self._registry.contains(name)

    def get(
        self,
        name: str,
        default: Metric | None = None,
    ) -> Metric | None:

        metric = self._registry.get(name)

        if metric is None:
            return default

        return metric
# ==========================================================
# Part 8 — Collection API
# ==========================================================

    def collect(
        self,
    ) -> list[MetricSnapshot]:
        """
        Collect snapshots from all registered metrics.
        """

        self._hooks.before_collect()

        snapshots = self._collector.collect()

        self._revision += 1

        self._hooks.after_collect(
            snapshots,
        )

        return snapshots

    def collect_one(
        self,
        name: str,
    ) -> MetricSnapshot:

        return self._collector.collect_one(
            name,
        )

    def collect_all(
        self,
    ) -> list[MetricSnapshot]:

        return self._collector.collect_all()

    def snapshot(
        self,
    ) -> dict[str, MetricSnapshot]:
        """
        Snapshot current registry state.
        """

        return {
            metric.descriptor.name: metric.snapshot()
            for metric in self._registry.values()
        }

    def restore(
        self,
        snapshots: dict[str, MetricSnapshot],
    ) -> None:
        """
        Restore registry from snapshots.
        """

        for name, snapshot in snapshots.items():

            metric = self._registry.get(name)

            if metric is not None:
                metric.restore(snapshot)

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.RESTORE,
            snapshots,
        )


# ==========================================================
# Part 9 — Runtime API
# ==========================================================

    def start(
        self,
    ) -> None:
        """
        Start manager.
        """

        self._state = ManagerState.RUNNING

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.START,
            self,
        )

    def stop(
        self,
    ) -> None:
        """
        Stop manager.
        """

        self._state = ManagerState.STOPPED

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.STOP,
            self,
        )

    def pause(
        self,
    ) -> None:
        """
        Pause manager.
        """

        if self._state is ManagerState.RUNNING:

            self._state = ManagerState.PAUSED

            self._revision += 1

            self._hooks.emit(
                ManagerEvent.PAUSE,
                self,
            )

    def resume(
        self,
    ) -> None:
        """
        Resume manager.
        """

        if self._state is ManagerState.PAUSED:

            self._state = ManagerState.RUNNING

            self._revision += 1

            self._hooks.emit(
                ManagerEvent.RESUME,
                self,
            )

    def reset(
        self,
    ) -> None:
        """
        Reset all registered metrics.
        """

        for metric in self._registry.values():
            metric.reset()

        self._revision = 0

        self._hooks.emit(
            ManagerEvent.RESET,
            self,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove every registered metric.
        """

        self._registry.clear()

        self._revision += 1

        self._hooks.emit(
            ManagerEvent.CLEAR,
            self,
        )
# ==========================================================
# Part 10 — Export API
# ==========================================================

    def export(self) -> dict[str, Any]:
        """
        Export the complete manager state.
        """

        return {
            "name": self._name,
            "namespace": self._namespace,
            "state": self._state.name,
            "mode": self._mode.name,
            "revision": self._revision,
            "metrics": {
                metric.descriptor.name: metric.snapshot().to_dict()
                for metric in self._registry.values()
            },
        }

    def import_snapshot(
        self,
        snapshots: dict[str, MetricSnapshot],
    ) -> None:
        """
        Import snapshots into the registry.
        """

        self.restore(snapshots)

    def serialize(self) -> str:
        """
        Serialize manager state.

        JSON serialization is delegated to MetricSnapshot.
        """

        import json

        return json.dumps(
            self.export(),
            indent=2,
            sort_keys=True,
            default=str,
        )


# ==========================================================
# Part 11 — Statistics
# ==========================================================

    def metric_count(self) -> int:
        """
        Number of registered metrics.
        """

        return len(self._registry)

    def summary(self) -> dict[str, Any]:
        """
        Lightweight runtime summary.
        """

        return {
            "name": self._name,
            "namespace": self._namespace,
            "state": self._state.name,
            "mode": self._mode.name,
            "revision": self._revision,
            "metric_count": len(self._registry),
            "thread_safe": self._thread_safe,
        }

    def diagnostics(self) -> dict[str, Any]:
        """
        Detailed runtime diagnostics.
        """

        return {
            **self.summary(),
            "registry": self._registry.summary(),
            "collector": self._collector.summary(),
            "hooks": self._hooks.summary(),
        }
# ==========================================================
# Part 12 — Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate manager integrity.
        """

        if not isinstance(self._registry, MetricRegistry):
            raise TypeError("Invalid MetricRegistry.")

        if not isinstance(self._collector, MetricCollector):
            raise TypeError("Invalid MetricCollector.")

        if not isinstance(self._hooks, MetricHooks):
            raise TypeError("Invalid MetricHooks.")

        self._registry.validate()
        self._collector.validate()
        self._hooks.validate()

    def is_valid(self) -> bool:
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

    def __len__(self) -> int:
        return len(self._registry)

    def __iter__(self) -> MetricIterator:
        return iter(self._registry)

    def __contains__(self, name: object) -> bool:

        if not isinstance(name, str):
            return False

        return self.contains(name)

    def __getitem__(self, name: str) -> Metric:
        return self._registry.require(name)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"namespace={self._namespace!r}, "
            f"state={self._state.name}, "
            f"mode={self._mode.name}, "
            f"metrics={len(self._registry)}, "
            f"revision={self._revision})"
        )

    def __str__(self) -> str:
        return self._name


# ==========================================================
# Part 14 — Final cleanup
# ==========================================================

__all__ = [
    "MANAGER_VERSION",
    "DEFAULT_MANAGER_NAME",
    "DEFAULT_NAMESPACE",
    "DEFAULT_AUTO_REGISTER",
    "DEFAULT_AUTO_COLLECT",
    "DEFAULT_THREAD_SAFE",
    "ManagerState",
    "ManagerMode",
    "ManagerEvent",
    "MetricManager",
]

# ==========================================================
# End of File
# ==========================================================                        