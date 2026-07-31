"""
SciOS Observability
==================

Metric Monitor.

Runtime monitoring component for the SciOS Observability Metrics
subsystem.

Responsibilities
----------------
- Monitor metric runtime health
- Detect abnormal metric states
- Produce diagnostics
- Maintain monitoring lifecycle
- Runtime status reporting

This module performs monitoring only.

It does not collect, aggregate, or export metrics.
"""

from __future__ import annotations

# ==========================================================
# Part 2 — Imports
# ==========================================================

from collections.abc import Iterator
from datetime import datetime
from datetime import timezone
from enum import Enum
from enum import auto
from threading import RLock
from typing import Any
from typing import Final
from typing import TypeAlias

from .metric import Metric
from .metric_snapshot import MetricSnapshot
from .metric_state import MetricHealth
from .metric_state import MetricStatus

# ==========================================================
# Part 3 — Public API
# ==========================================================

__all__ = [
    "MONITOR_VERSION",
    "DEFAULT_MONITOR_NAME",
    "DEFAULT_NAMESPACE",
    "DEFAULT_THREAD_SAFE",
    "DEFAULT_AUTO_START",
    "MonitorName",
    "MonitorID",
    "MonitorTimestamp",
    "MonitorData",
]

# ==========================================================
# Part 4 — Version / Constants / Type Aliases
# ==========================================================

MONITOR_VERSION: Final[str] = "1.0.0"

DEFAULT_MONITOR_NAME: Final[str] = "monitor"

DEFAULT_NAMESPACE: Final[str] = "default"

DEFAULT_THREAD_SAFE: Final[bool] = True

DEFAULT_AUTO_START: Final[bool] = False

DEFAULT_HISTORY_LIMIT: Final[int] = 1024

DEFAULT_REFRESH_INTERVAL: Final[float] = 1.0

DEFAULT_HEALTH_LEVEL: Final[MetricHealth] = MetricHealth.UNKNOWN

DEFAULT_STATUS: Final[MetricStatus] = MetricStatus.CREATED

MonitorName: TypeAlias = str

MonitorID: TypeAlias = str

MonitorTimestamp: TypeAlias = datetime

MonitorData: TypeAlias = dict[str, Any]
# ==========================================================
# Part 5 — Runtime Enums
# ==========================================================

class MonitorState(Enum):
    """
    Runtime state of the monitor.
    """

    CREATED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    CLOSED = auto()


class MonitorEvent(Enum):
    """
    Monitor lifecycle events.
    """

    START = auto()
    STOP = auto()
    PAUSE = auto()
    RESUME = auto()

    MONITOR = auto()
    MONITOR_ONE = auto()

    WARNING = auto()
    ALERT = auto()

    RESET = auto()
    CLEAR = auto()


class HealthLevel(Enum):
    """
    Overall monitoring health.
    """

    UNKNOWN = auto()
    HEALTHY = auto()
    WARNING = auto()
    CRITICAL = auto()


# ==========================================================
# Part 6 — MetricMonitor
# ==========================================================

class MetricMonitor:
    """
    Runtime metric monitor.
    """

    # ------------------------------------------------------
    # Constructor
    # ------------------------------------------------------

    def __init__(
        self,
        *,
        name: MonitorName = DEFAULT_MONITOR_NAME,
        namespace: str = DEFAULT_NAMESPACE,
        thread_safe: bool = DEFAULT_THREAD_SAFE,
        auto_start: bool = DEFAULT_AUTO_START,
    ) -> None:

        self._name = name
        self._namespace = namespace

        self._state = (
            MonitorState.RUNNING
            if auto_start
            else MonitorState.CREATED
        )

        self._health = HealthLevel.UNKNOWN

        self._status = DEFAULT_STATUS

        self._thread_safe = thread_safe

        self._created_at = datetime.now(timezone.utc)

        self._started_at: MonitorTimestamp | None = (
            self._created_at
            if auto_start
            else None
        )

        self._stopped_at: MonitorTimestamp | None = None

        self._revision = 0

        self._history: list[MonitorData] = []

        self._lock = RLock()

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def name(self) -> MonitorName:
        return self._name

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def state(self) -> MonitorState:
        return self._state

    @property
    def health(self) -> HealthLevel:
        return self._health

    @property
    def status(self) -> MetricStatus:
        return self._status

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def created_at(self) -> MonitorTimestamp:
        return self._created_at

    @property
    def started_at(self) -> MonitorTimestamp | None:
        return self._started_at

    @property
    def stopped_at(self) -> MonitorTimestamp | None:
        return self._stopped_at

    @property
    def history(self) -> tuple[MonitorData, ...]:
        return tuple(self._history)

    @property
    def thread_safe(self) -> bool:
        return self._thread_safe


# ==========================================================
# Part 7 — Monitoring API
# ==========================================================

    def start(self) -> None:

        self._state = MonitorState.RUNNING
        self._started_at = datetime.now(timezone.utc)
        self._status = MetricStatus.ACTIVE
        self._revision += 1

    def stop(self) -> None:

        self._state = MonitorState.STOPPED
        self._stopped_at = datetime.now(timezone.utc)
        self._status = MetricStatus.IDLE
        self._revision += 1

    def pause(self) -> None:

        self._state = MonitorState.PAUSED
        self._revision += 1

    def resume(self) -> None:

        self._state = MonitorState.RUNNING
        self._revision += 1

    def monitor(
        self,
        metrics: Iterator[Metric],
    ) -> list[MonitorData]:
        """
        Monitor an iterable of metrics.
        """

        results: list[MonitorData] = []

        for metric in metrics:
            results.append(self.monitor_one(metric))

        return results

    def monitor_one(
        self,
        metric: Metric,
    ) -> MonitorData:
        """
        Monitor a single metric.
        """

        snapshot: MetricSnapshot = metric.snapshot()

        result: MonitorData = {
            "name": snapshot.descriptor.name,
            "revision": snapshot.revision,
            "state": snapshot.state.name,
            "enabled": snapshot.enabled,
            "frozen": snapshot.frozen,
            "closed": snapshot.closed,
            "timestamp": datetime.now(timezone.utc),
        }

        self._history.append(result)

        if len(self._history) > DEFAULT_HISTORY_LIMIT:
            self._history.pop(0)

        self._revision += 1

        return result
# ==========================================================
# Part 8 — Health API
# ==========================================================

    def health(self) -> HealthLevel:
        """
        Current monitor health.
        """

        return self._health

    def status(self) -> MetricStatus:
        """
        Current runtime status.
        """

        return self._status

    def warnings(self) -> list[MonitorData]:
        """
        Return warning records.
        """

        return [
            item
            for item in self._history
            if item.get("level") == "warning"
        ]

    def alerts(self) -> list[MonitorData]:
        """
        Return critical alert records.
        """

        return [
            item
            for item in self._history
            if item.get("level") == "critical"
        ]

    def clear_alerts(self) -> None:
        """
        Remove warning/alert records.
        """

        self._history = [
            item
            for item in self._history
            if item.get("level")
            not in {"warning", "critical"}
        ]

        self._revision += 1


# ==========================================================
# Part 9 — Runtime API
# ==========================================================

    def touch(self) -> None:
        """
        Increment runtime revision.
        """

        self._revision += 1

    def reset(self) -> None:
        """
        Reset monitor runtime state.
        """

        self._revision = 0

        self._health = HealthLevel.UNKNOWN

        self._status = MetricStatus.IDLE

        self._state = MonitorState.CREATED

        self._history.clear()

        self._started_at = None

        self._stopped_at = None

    def clear(self) -> None:
        """
        Clear monitoring history.
        """

        self._history.clear()

        self._revision += 1

    def snapshot(self) -> MonitorData:
        """
        Runtime snapshot.
        """

        return {
            "name": self._name,
            "namespace": self._namespace,
            "state": self._state.name,
            "health": self._health.name,
            "status": self._status.name,
            "revision": self._revision,
            "created_at": self._created_at,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
            "history": list(self._history),
        }

    def restore(
        self,
        snapshot: MonitorData,
    ) -> None:
        """
        Restore runtime snapshot.
        """

        self._state = MonitorState[
            snapshot["state"]
        ]

        self._health = HealthLevel[
            snapshot["health"]
        ]

        self._status = MetricStatus[
            snapshot["status"]
        ]

        self._revision = snapshot["revision"]

        self._created_at = snapshot["created_at"]

        self._started_at = snapshot["started_at"]

        self._stopped_at = snapshot["stopped_at"]

        self._history = list(
            snapshot["history"]
        )


# ==========================================================
# Part 10 — Statistics
# ==========================================================

    def uptime(self) -> float:
        """
        Running time in seconds.
        """

        if self._started_at is None:
            return 0.0

        end = (
            self._stopped_at
            or datetime.now(timezone.utc)
        )

        return (
            end - self._started_at
        ).total_seconds()

    def monitor_count(self) -> int:
        """
        Number of monitored records.
        """

        return len(self._history)

    def summary(self) -> MonitorData:
        """
        Runtime summary.
        """

        return {
            "name": self._name,
            "state": self._state.name,
            "health": self._health.name,
            "status": self._status.name,
            "revision": self._revision,
            "records": len(self._history),
            "uptime": self.uptime(),
        }

    def diagnostics(self) -> MonitorData:
        """
        Detailed diagnostics.
        """

        return {
            **self.summary(),
            "thread_safe": self._thread_safe,
            "created_at": self._created_at,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
            "history_limit": DEFAULT_HISTORY_LIMIT,
        }
# ==========================================================
# Part 11 — Validation
# ==========================================================

    def validate(self) -> None:
        """
        Validate monitor integrity.
        """

        if not isinstance(self._name, str):
            raise TypeError("Monitor name must be a string.")

        if not isinstance(self._namespace, str):
            raise TypeError("Namespace must be a string.")

        if not isinstance(self._state, MonitorState):
            raise TypeError("Invalid monitor state.")

        if not isinstance(self._health, HealthLevel):
            raise TypeError("Invalid health level.")

        if not isinstance(self._status, MetricStatus):
            raise TypeError("Invalid metric status.")

        if not isinstance(self._revision, int):
            raise TypeError("Revision must be an integer.")

        if self._revision < 0:
            raise ValueError("Revision cannot be negative.")

        if not isinstance(self._history, list):
            raise TypeError("History must be a list.")

        if len(self._history) > DEFAULT_HISTORY_LIMIT:
            raise ValueError("History exceeds configured limit.")

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
# Part 12 — Python Protocols
# ==========================================================

    def __len__(self) -> int:
        return len(self._history)

    def __iter__(self) -> Iterator[MonitorData]:
        return iter(self._history)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"state={self._state.name}, "
            f"health={self._health.name}, "
            f"status={self._status.name}, "
            f"records={len(self._history)}, "
            f"revision={self._revision})"
        )

    def __str__(self) -> str:
        return self._name


# ==========================================================
# Part 13 — Final cleanup
# ==========================================================

__all__ = [
    "MONITOR_VERSION",
    "DEFAULT_MONITOR_NAME",
    "DEFAULT_NAMESPACE",
    "DEFAULT_THREAD_SAFE",
    "DEFAULT_AUTO_START",
    "DEFAULT_HISTORY_LIMIT",
    "DEFAULT_REFRESH_INTERVAL",
    "DEFAULT_HEALTH_LEVEL",
    "DEFAULT_STATUS",
    "MonitorName",
    "MonitorID",
    "MonitorTimestamp",
    "MonitorData",
    "MonitorState",
    "MonitorEvent",
    "HealthLevel",
    "MetricMonitor",
]

# ==========================================================
# End of File
# ==========================================================                