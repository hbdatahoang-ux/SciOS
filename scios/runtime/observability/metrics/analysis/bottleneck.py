"""
Metric Bottleneck Detection
===========================

SciOS-NG Runtime Metrics Analysis

This module provides a deterministic, stateful bottleneck detector for
runtime metrics.

Design contract
---------------
* Built-in algorithms are available as methods.
* The algorithm registry starts empty.
* Built-in algorithms are explicitly registered through
  ``register_builtin_algorithms()``.
* ``pipeline()`` is independent of the registry.
* ``detect()`` executes algorithms through the registry.
* Runtime state, statistics, history, hooks, snapshots, cloning and
  serialization are supported.
"""

from __future__ import annotations

import copy
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping


# ============================================================================
# Types
# ============================================================================

AlgorithmCallable = Callable[..., Mapping[str, Any]]
HookCallable = Callable[..., Any]


# ============================================================================
# MetricBottleneckDetector
# ============================================================================


class MetricBottleneckDetector:
    """
    Stateful runtime metric bottleneck detector.

    The detector exposes seven canonical built-in detection algorithms:

    * latency
    * throughput
    * utilization
    * queue
    * contention
    * saturation
    * dependency

    Additional composite/helper algorithms:

    * pipeline
    * custom

    The registry is intentionally empty after construction. Call
    ``register_builtin_algorithms()`` when registry-based execution is
    required.
    """

    VERSION = "0.2.0"

    DEFAULT_CONFIG = {
        "latency_threshold": 100.0,
        "throughput_threshold": 1000.0,
        "utilization_threshold": 0.80,
        "queue_threshold": 100,
        "contention_threshold": 0.75,
        "saturation_threshold": 0.90,
        "dependency_depth": 5,
    }

    BUILTIN_ALGORITHM_NAMES = (
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
        "pipeline",
        "custom",
    )

    PIPELINE_ALGORITHM_NAMES = (
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
    )

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "MetricBottleneckDetector",
        description: str = "",
        *,
        config: Mapping[str, Any] | None = None,
    ) -> None:
        self.name = str(name)
        self.description = str(description)
        self.version = self.VERSION

        self.id = str(uuid.uuid4())

        now = self._now_iso()
        self.created_at = now
        self.updated_at = now

        self._enabled = True
        self._frozen = False
        self._closed = False
        self._running = False

        self._config = copy.deepcopy(self.DEFAULT_CONFIG)

        if config is not None:
            self._config.update(dict(config))

        self._algorithms: dict[str, dict[str, Any]] = {}

        self._detection_count = 0
        self._bottleneck_count = 0
        self._error_count = 0

        self._latest_latency = 0.0
        self._history: list[dict[str, Any]] = []
        self._last_result: dict[str, Any] | None = None

        self._hooks: dict[str, list[HookCallable]] = {}
        self._events: list[dict[str, Any]] = []

        self._started_monotonic = time.monotonic()

    # ==================================================================
    # Time helpers
    # ==================================================================

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _touch(self) -> None:
        self.updated_at = self._now_iso()

    # ==================================================================
    # Identity
    # ==================================================================

    @property
    def active(self) -> bool:
        return (
            self._enabled
            and not self._frozen
            and not self._closed
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def disabled(self) -> bool:
        return not self._enabled

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def running(self) -> bool:
        return self._running

    # ==================================================================
    # Runtime lifecycle
    # ==================================================================

    def enable(self) -> MetricBottleneckDetector:
        self._enabled = True
        self._touch()
        return self

    def disable(self) -> MetricBottleneckDetector:
        self._enabled = False
        self._running = False
        self._touch()
        return self

    def freeze(self) -> MetricBottleneckDetector:
        self._frozen = True
        self._running = False
        self._touch()
        return self

    def unfreeze(self) -> MetricBottleneckDetector:
        self._frozen = False
        self._touch()
        return self

    def close(self) -> MetricBottleneckDetector:
        self._closed = True
        self._running = False
        self._touch()
        return self

    def reopen(self) -> MetricBottleneckDetector:
        self._closed = False
        self._touch()
        return self

    def _require_active(self) -> None:
        if not self.active:
            raise RuntimeError(
                "MetricBottleneckDetector is not active"
            )

    # ==================================================================
    # Configuration
    # ==================================================================

    @property
    def config(self) -> dict[str, Any]:
        return copy.deepcopy(self._config)

    def configure(
        self,
        **kwargs: Any,
    ) -> MetricBottleneckDetector:
        unknown = set(kwargs) - set(self.DEFAULT_CONFIG)

        if unknown:
            names = ", ".join(sorted(unknown))
            raise KeyError(
                f"Unknown bottleneck configuration: {names}"
            )

        self._config.update(kwargs)
        self._touch()
        return self

    # ==================================================================
    # Statistics
    # ==================================================================

    @property
    def detection_count(self) -> int:
        return self._detection_count

    @property
    def bottleneck_count(self) -> int:
        return self._bottleneck_count

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def latest_latency(self) -> float:
        return self._latest_latency

    @property
    def latency_value(self) -> float:
        return self._latest_latency

    @property
    def history_size(self) -> int:
        return len(self._history)

    @property
    def last_result(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._last_result)

    @property
    def statistics(self) -> dict[str, Any]:
        return {
            "detection_count": self._detection_count,
            "bottleneck_count": self._bottleneck_count,
            "error_count": self._error_count,
            "latency": self._latest_latency,
            "history_size": len(self._history),
        }

    # ==================================================================
    # Generic metric helpers
    # ==================================================================

    def _metric(
        self,
        metrics: Mapping[str, Any],
        name: str,
        default: float = 0.0,
    ) -> float:
        value = metrics.get(name, default)

        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def _severity(
        bottleneck: bool,
        *,
        critical: bool = False,
    ) -> str:
        if not bottleneck:
            return "normal"

        return "critical" if critical else "high"

    def _result(
        self,
        algorithm: str,
        metric: float,
        threshold: float,
        bottleneck: bool,
        *,
        critical: bool = False,
    ) -> dict[str, Any]:
        return {
            "algorithm": algorithm,
            "metric": metric,
            "threshold": threshold,
            "bottleneck": bool(bottleneck),
            "severity": self._severity(
                bottleneck,
                critical=critical,
            ),
        }

    # ==================================================================
    # Part 1. Built-in Algorithms
    # ==================================================================

    def latency(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "latency")
        limit = (
            self._config["latency_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "latency",
            value,
            limit,
            value >= limit,
        )

    def throughput(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "throughput")
        limit = (
            self._config["throughput_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "throughput",
            value,
            limit,
            value <= limit,
        )

    def utilization(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "utilization")
        limit = (
            self._config["utilization_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "utilization",
            value,
            limit,
            value >= limit,
        )

    def queue(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        if "queue" in metrics:
            value = self._metric(metrics, "queue")
        else:
            value = self._metric(metrics, "queue_size")

        limit = (
            self._config["queue_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "queue",
            value,
            limit,
            value >= limit,
        )

    def contention(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "contention")
        limit = (
            self._config["contention_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "contention",
            value,
            limit,
            value >= limit,
        )

    def saturation(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "saturation")
        limit = (
            self._config["saturation_threshold"]
            if threshold is None
            else threshold
        )

        return self._result(
            "saturation",
            value,
            limit,
            value >= limit,
            critical=True,
        )

    def dependency(
        self,
        metrics: Mapping[str, Any],
        *,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        value = self._metric(metrics, "dependency_depth")
        limit = (
            self._config["dependency_depth"]
            if threshold is None
            else threshold
        )

        return self._result(
            "dependency",
            value,
            limit,
            value >= limit,
        )

    # ==================================================================
    # Part 2. Pipeline
    # ==================================================================

    def pipeline(
        self,
        metrics: Mapping[str, Any],
    ) -> dict[str, Any]:
        results = [
            self.latency(metrics),
            self.throughput(metrics),
            self.utilization(metrics),
            self.queue(metrics),
            self.contention(metrics),
            self.saturation(metrics),
            self.dependency(metrics),
        ]

        bottlenecks = [
            result
            for result in results
            if result["bottleneck"]
        ]

        return {
            "algorithm": "pipeline",
            "bottleneck": bool(bottlenecks),
            "count": len(bottlenecks),
            "results": results,
        }

    # ==================================================================
    # Part 3. Custom Detection
    # ==================================================================

    def custom(
        self,
        metrics: Mapping[str, Any],
        detector: AlgorithmCallable,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        if not callable(detector):
            raise TypeError("detector must be callable")

        return detector(metrics, **kwargs)

    # ==================================================================
    # Part 4. Registry
    # ==================================================================

    def register_algorithm(
        self,
        name: str,
        algorithm: AlgorithmCallable,
        *,
        enabled: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> MetricBottleneckDetector:
        if not callable(algorithm):
            raise TypeError("algorithm must be callable")

        key = str(name)

        self._algorithms[key] = {
            "name": key,
            "callable": algorithm,
            "enabled": bool(enabled),
            "metadata": copy.deepcopy(
                dict(metadata or {})
            ),
        }

        self._touch()
        return self

    def remove_algorithm(
        self,
        name: str,
    ) -> MetricBottleneckDetector:
        self._algorithms.pop(str(name), None)
        self._touch()
        return self

    def unregister_algorithm(
        self,
        name: str,
    ) -> MetricBottleneckDetector:
        return self.remove_algorithm(name)

    def algorithms(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self._algorithms)

    def algorithm_names(self) -> list[str]:
        return list(self._algorithms.keys())

    @property
    def algorithm_count(self) -> int:
        return len(self._algorithms)

    def contains_algorithm(self, name: str) -> bool:
        return str(name) in self._algorithms

    def exists_algorithm(self, name: str) -> bool:
        return self.contains_algorithm(name)

    def algorithm(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        entry = self._algorithms.get(str(name))

        if entry is None:
            return default

        return copy.deepcopy(entry)

    def enable_algorithm(
        self,
        name: str,
    ) -> MetricBottleneckDetector:
        entry = self._algorithms.get(str(name))

        if entry is not None:
            entry["enabled"] = True
            self._touch()

        return self

    def disable_algorithm(
        self,
        name: str,
    ) -> MetricBottleneckDetector:
        entry = self._algorithms.get(str(name))

        if entry is not None:
            entry["enabled"] = False
            self._touch()

        return self

    # ==================================================================
    # Part 5. Built-in Registry
    # ==================================================================

    def register_builtin_algorithms(
        self,
    ) -> MetricBottleneckDetector:
        self.register_algorithm(
            "latency",
            self.latency,
        )
        self.register_algorithm(
            "throughput",
            self.throughput,
        )
        self.register_algorithm(
            "utilization",
            self.utilization,
        )
        self.register_algorithm(
            "queue",
            self.queue,
        )
        self.register_algorithm(
            "contention",
            self.contention,
        )
        self.register_algorithm(
            "saturation",
            self.saturation,
        )
        self.register_algorithm(
            "dependency",
            self.dependency,
        )
        self.register_algorithm(
            "pipeline",
            self.pipeline,
        )
        self.register_algorithm(
            "custom",
            self.custom,
        )

        return self

    # ==================================================================
    # Part 6. Registry Execution
    # ==================================================================

    def execute_algorithm(
        self,
        name: str,
        metrics: Mapping[str, Any],
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        key = str(name)

        entry = self._algorithms.get(key)

        if entry is None:
            raise KeyError(
                f"Unknown bottleneck algorithm: {key}"
            )

        if not entry["enabled"]:
            raise RuntimeError(
                f"Bottleneck algorithm '{key}' is disabled"
            )

        self.before_algorithm(key)

        try:
            result = entry["callable"](
                metrics,
                **kwargs,
            )
        finally:
            # after_algorithm intentionally receives only a result
            # when execution succeeds.
            pass

        self.after_algorithm(
            key,
            result,
        )

        return result

    # ==================================================================
    # Part 7. Detection API
    # ==================================================================

    def detect(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        self._require_active()

        self.before_detect(
            metrics,
            method,
            **kwargs,
        )

        self._running = True
        started = time.perf_counter()

        try:
            result = self.execute_algorithm(
                method,
                metrics,
                **kwargs,
            )

            elapsed = time.perf_counter() - started
            self._latest_latency = float(elapsed)

            self._detection_count += 1

            if bool(result.get("bottleneck", False)):
                self._bottleneck_count += 1

            normalized = copy.deepcopy(
                dict(result)
            )

            self._last_result = normalized
            self._history.append(
                copy.deepcopy(normalized)
            )

            self.after_detect(
                normalized,
                method,
            )

            self._touch()

            return normalized

        except Exception:
            elapsed = time.perf_counter() - started
            self._latest_latency = float(elapsed)
            self._error_count += 1
            self._touch()
            raise

        finally:
            self._running = False

    def detect_many(
        self,
        metrics_list: Iterable[Mapping[str, Any]],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> list[Mapping[str, Any]]:
        return [
            self.detect(
                metrics,
                method=method,
                **kwargs,
            )
            for metrics in metrics_list
        ]

    def detect_batch(
        self,
        metrics_list: Iterable[Mapping[str, Any]],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> list[Mapping[str, Any]]:
        return self.detect_many(
            metrics_list,
            method=method,
            **kwargs,
        )

    def detect_one(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return self.detect(
            metrics,
            method=method,
            **kwargs,
        )

    def run(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return self.detect(
            metrics,
            method=method,
            **kwargs,
        )

    def execute(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return self.detect(
            metrics,
            method=method,
            **kwargs,
        )

    def process(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return self.detect(
            metrics,
            method=method,
            **kwargs,
        )

    def __call__(
        self,
        metrics: Mapping[str, Any],
        method: str = "pipeline",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return self.detect(
            metrics,
            method=method,
            **kwargs,
        )

    # ==================================================================
    # Part 8. Reset / Clear
    # ==================================================================

    def clear(self) -> MetricBottleneckDetector:
        self._history.clear()
        self._last_result = None
        self._touch()
        return self

    def reset(self) -> MetricBottleneckDetector:
        self._detection_count = 0
        self._bottleneck_count = 0
        self._error_count = 0

        self._latest_latency = 0.0
        self._history.clear()
        self._last_result = None
        self._running = False

        self._touch()
        return self

    # ==================================================================
    # Part 9. Snapshot / Restore
    # ==================================================================

    def snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "running": self.running,
            "config": self.config,
            "detection_count": self.detection_count,
            "bottleneck_count": self.bottleneck_count,
            "error_count": self.error_count,
            "latency": self.latest_latency,
            "history": copy.deepcopy(self._history),
            "last_result": copy.deepcopy(self._last_result),
            "algorithm_names": self.algorithm_names(),
        }

    def restore(
        self,
        snapshot: Mapping[str, Any] | None = None,
    ) -> MetricBottleneckDetector:
        if snapshot is None:
            return self

        data = dict(snapshot)

        if "name" in data:
            self.name = str(data["name"])

        if "description" in data:
            self.description = str(
                data["description"]
            )

        if "version" in data:
            self.version = str(data["version"])

        if "id" in data:
            self.id = str(data["id"])

        if "created_at" in data:
            self.created_at = str(
                data["created_at"]
            )

        if "updated_at" in data:
            self.updated_at = str(
                data["updated_at"]
            )

        if "enabled" in data:
            self._enabled = bool(
                data["enabled"]
            )

        if "frozen" in data:
            self._frozen = bool(
                data["frozen"]
            )

        if "closed" in data:
            self._closed = bool(
                data["closed"]
            )

        self._running = False

        if "config" in data:
            self._config = copy.deepcopy(
                dict(data["config"])
            )

        self._detection_count = int(
            data.get(
                "detection_count",
                0,
            )
        )

        self._bottleneck_count = int(
            data.get(
                "bottleneck_count",
                0,
            )
        )

        self._error_count = int(
            data.get(
                "error_count",
                0,
            )
        )

        self._latest_latency = float(
            data.get(
                "latency",
                data.get(
                    "latest_latency",
                    0.0,
                ),
            )
        )

        self._history = copy.deepcopy(
            data.get(
                "history",
                [],
            )
        )

        self._last_result = copy.deepcopy(
            data.get(
                "last_result",
                None,
            )
        )

        # IMPORTANT:
        # Do not call _touch() during restore.
        #
        # restore() is a state-reconstruction operation and must
        # preserve the exact created_at / updated_at values from
        # the snapshot.

        # Preserve an already existing registry.
        #
        # If the receiver has no registry but the snapshot declares
        # builtin algorithms, reconstruct them.
        if (
            not self._algorithms
            and data.get("algorithm_names")
        ):
            names = set(
                data["algorithm_names"]
            )

            if names.intersection(
                self.BUILTIN_ALGORITHM_NAMES
            ):
                self.register_builtin_algorithms()

        return self

    # ==================================================================
    # Part 10. Clone / Copy
    # ==================================================================

    def clone(self) -> MetricBottleneckDetector:
        cloned = MetricBottleneckDetector(
            name=self.name,
            description=self.description,
        )

        cloned.version = self.version

        cloned._enabled = self._enabled
        cloned._frozen = self._frozen
        cloned._closed = self._closed
        cloned._running = False

        cloned._config = copy.deepcopy(
            self._config
        )

        cloned._detection_count = (
            self._detection_count
        )
        cloned._bottleneck_count = (
            self._bottleneck_count
        )
        cloned._error_count = (
            self._error_count
        )

        cloned._latest_latency = (
            self._latest_latency
        )

        cloned._history = copy.deepcopy(
            self._history
        )

        cloned._last_result = copy.deepcopy(
            self._last_result
        )

        cloned.created_at = self.created_at
        cloned.updated_at = self.updated_at

        cloned._hooks = copy.deepcopy(
            self._hooks
        )

        cloned._events = copy.deepcopy(
            self._events
        )

        # Preserve callable references but never share registry mappings.
        cloned._algorithms = {}

        for name, entry in self._algorithms.items():
            cloned._algorithms[name] = {
                "name": entry["name"],
                "callable": entry["callable"],
                "enabled": entry["enabled"],
                "metadata": copy.deepcopy(
                    entry["metadata"]
                ),
            }

        return cloned

    def copy(self) -> MetricBottleneckDetector:
        return self.clone()

    def __copy__(self) -> MetricBottleneckDetector:
        return self.clone()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> MetricBottleneckDetector:
        del memo
        return self.clone()

    # ==================================================================
    # Part 11. Diagnostics
    # ==================================================================

    @property
    def uptime(self) -> float:
        return max(
            0.0,
            time.monotonic()
            - self._started_monotonic,
        )

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "version": self.version,
            "enabled": self.enabled,
            "running": self.running,
            "bottleneck_count": self.bottleneck_count,
            "detection_count": self.detection_count,
            "error_count": self.error_count,
            "latency": self.latest_latency,
            "algorithms": self.algorithm_count,
            "uptime": self.uptime,
        }

    def health(self) -> dict[str, Any]:
        if self.closed:
            status = "closed"
        elif self.disabled:
            status = "disabled"
        elif self.frozen:
            status = "frozen"
        elif self.error_count > 0:
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "active": self.active,
            "running": self.running,
            "errors": self.error_count,
            "uptime": self.uptime,
        }

    def status(self) -> dict[str, Any]:
        return self.health()

    def report(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "configuration": self.config,
            "statistics": self.statistics,
            "history_size": self.history_size,
            "last_result": self.last_result,
        }

    # ==================================================================
    # Part 12. Serialization
    # ==================================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "running": self.running,
            "config": self.config,
            "bottleneck_count": self.bottleneck_count,
            "detection_count": self.detection_count,
            "error_count": self.error_count,
            "latency": self.latest_latency,
            "algorithm_names": self.algorithm_names(),
            "history": copy.deepcopy(
                self._history
            ),
            "last_result": copy.deepcopy(
                self._last_result
            ),
        }

    def serialize(self) -> dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> MetricBottleneckDetector:
        obj = cls(
            name=data.get(
                "name",
                "MetricBottleneckDetector",
            ),
            description=data.get(
                "description",
                "",
            ),
        )

        obj.restore(data)

        return obj

    def to_json(
        self,
        **kwargs: Any,
    ) -> str:
        return json.dumps(
            self.to_dict(),
            **kwargs,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> MetricBottleneckDetector:
        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        data = json.loads(text)

        if not isinstance(data, Mapping):
            raise TypeError(
                "JSON payload must decode to an object"
            )

        return cls.from_dict(data)

    @classmethod
    def deserialize(
        cls,
        data: Mapping[str, Any] | str,
    ) -> MetricBottleneckDetector:
        if isinstance(data, str):
            return cls.from_json(data)

        return cls.from_dict(data)

    # ==================================================================
    # Part 13. Events / Hooks
    # ==================================================================

    def add_hook(
        self,
        event: str,
        callback: HookCallable,
    ) -> MetricBottleneckDetector:
        if not callable(callback):
            raise TypeError(
                "callback must be callable"
            )

        self._hooks.setdefault(
            str(event),
            [],
        ).append(callback)

        return self

    def subscribe(
        self,
        event: str,
        callback: HookCallable,
    ) -> MetricBottleneckDetector:
        return self.add_hook(
            event,
            callback,
        )

    def remove_hook(
        self,
        event: str,
        callback: HookCallable | None = None,
    ) -> MetricBottleneckDetector:
        key = str(event)

        if key not in self._hooks:
            return self

        if callback is None:
            self._hooks.pop(key, None)
            return self

        callbacks = self._hooks[key]

        self._hooks[key] = [
            item
            for item in callbacks
            if item is not callback
        ]

        if not self._hooks[key]:
            self._hooks.pop(key, None)

        return self

    def emit(
        self,
        event: str,
        **payload: Any,
    ) -> MetricBottleneckDetector:
        key = str(event)

        record = {
            "event": key,
            "payload": copy.deepcopy(payload),
            "timestamp": self._now_iso(),
        }

        self._events.append(record)

        callbacks = list(
            self._hooks.get(
                key,
                [],
            )
        )

        for callback in callbacks:
            callback(
                self,
                **payload,
            )

        return self

    def before_detect(
        self,
        metrics: Mapping[str, Any],
        method: str,
        **kwargs: Any,
    ) -> MetricBottleneckDetector:
        self.emit(
            "before_detect",
            metrics=copy.deepcopy(
                dict(metrics)
            ),
            method=method,
            kwargs=copy.deepcopy(kwargs),
        )

        return self

    def after_detect(
        self,
        result: Mapping[str, Any],
        method: str,
    ) -> MetricBottleneckDetector:
        self.emit(
            "after_detect",
            result=copy.deepcopy(
                dict(result)
            ),
            method=method,
        )

        return self

    def before_algorithm(
        self,
        algorithm: str,
    ) -> MetricBottleneckDetector:
        self.emit(
            "before_algorithm",
            algorithm=algorithm,
        )

        return self

    def after_algorithm(
        self,
        algorithm: str,
        result: Mapping[str, Any],
    ) -> MetricBottleneckDetector:
        self.emit(
            "after_algorithm",
            algorithm=algorithm,
            result=copy.deepcopy(
                dict(result)
            ),
        )

        return self

    # ==================================================================
    # Part 14. Python Protocols
    # ==================================================================

    def __len__(self) -> int:
        return self.algorithm_count

    def __iter__(self):
        return iter(
            self._algorithms.items()
        )

    def __contains__(
        self,
        name: object,
    ) -> bool:
        return name in self._algorithms

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"algorithms={self.algorithm_count}, "
            f"detections={self.detection_count}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"algorithms={self.algorithm_count}, "
            f"detections={self.detection_count}, "
            f"bottlenecks={self.bottleneck_count}"
            f")"
        )


__all__ = [
    "AlgorithmCallable",
    "HookCallable",
    "MetricBottleneckDetector",
]