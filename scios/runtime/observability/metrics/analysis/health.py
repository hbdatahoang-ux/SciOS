"""
SciOS-NG Runtime Metrics Analysis
Metric Health Analyzer
"""

from __future__ import annotations

import copy
import json
import threading
import time
import uuid
from typing import Any, Callable, Iterable, Mapping


# ============================================================================
# Helpers
# ============================================================================


class _LatencyValue(float):
    """
    Float-compatible latency statistic that is also callable.

    The public contract intentionally allows:

        analyzer.latency == 0.0

    and:

        analyzer.latency({"latency": 20.0})

    This avoids the historical collision between the latency statistic
    property and the built-in latency analysis algorithm.
    """

    def __new__(
        cls,
        value: float,
        analyzer: "MetricHealthAnalyzer",
    ) -> "_LatencyValue":
        obj = float.__new__(cls, value)
        obj._analyzer = analyzer
        return obj

    def __call__(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._analyzer._algorithm_latency(
            metrics or {},
            **kwargs,
        )


# ============================================================================
# MetricHealthAnalyzer
# ============================================================================


class MetricHealthAnalyzer:
    """
    Runtime health analyzer for SciOS metrics.

    The class deliberately exposes both:

    * runtime statistics
    * registered analysis algorithms

    Algorithms are ordinary callables and are available both through the
    registry and as convenient public methods.
    """

    VERSION = "1.0.0"

    DEFAULT_CONFIG: dict[str, Any] = {
        "healthy_score": 90.0,
        "warning_score": 70.0,
        "availability_threshold": 0.99,
        "reliability_threshold": 0.95,
        "latency_threshold": 100.0,
        "throughput_threshold": 100.0,
        "utilization_threshold": 0.85,
        "saturation_threshold": 1.0,
    }

    BUILTIN_ALGORITHMS = (
        "availability",
        "reliability",
        "latency",
        "throughput",
        "utilization",
        "saturation",
        "health_score",
        "overall",
        "custom",
    )

    # ----------------------------------------------------------------------
    # Construction
    # ----------------------------------------------------------------------

    def __init__(
        self,
        name: str = "MetricHealthAnalyzer",
        description: str = "",
        *,
        config: Mapping[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.id = str(uuid.uuid4())
        self.version = self.VERSION

        self.enabled = True
        self.frozen = False
        self.closed = False
        self.running = False

        self._config: dict[str, Any] = copy.deepcopy(
            self.DEFAULT_CONFIG
        )

        if config:
            self._config.update(copy.deepcopy(dict(config)))

        self._algorithms: dict[str, dict[str, Any]] = {}
        self._hooks: dict[str, list[Callable[..., Any]]] = {}
        self._events: list[dict[str, Any]] = []

        self._context: dict[str, Any] = {}

        self._health_count = 0
        self._analysis_count = 0
        self._error_count = 0
        self._latency = 0.0

        self._history: list[dict[str, Any]] = []
        self._last_result: dict[str, Any] | None = None
        self._snapshot: dict[str, Any] | None = None

        self._created_at = time.time()
        self._updated_at = self._created_at

        self._health_cache: dict[str, Any] | None = None

        self._lock = threading.RLock()

        self._register_builtin_algorithms()

    # ----------------------------------------------------------------------
    # Basic runtime properties
    # ----------------------------------------------------------------------

    @property
    def disabled(self) -> bool:
        return not self.enabled

    @property
    def active(self) -> bool:
        return (
            self.enabled
            and not self.frozen
            and not self.closed
        )

    @property
    def health_count(self) -> int:
        return self._health_count

    @property
    def analysis_count(self) -> int:
        return self._analysis_count

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def latency(self) -> _LatencyValue:
        """
        Runtime analysis latency.

        The returned value behaves like a float while remaining callable
        as the built-in latency algorithm.
        """
        return _LatencyValue(
            self._latency,
            self,
        )

    @property
    def uptime(self) -> float:
        return max(
            0.0,
            time.time() - self._created_at,
        )

    @property
    def updated_at(self) -> float:
        return self._updated_at

    # ----------------------------------------------------------------------
    # Internal state helpers
    # ----------------------------------------------------------------------

    def _touch(self) -> None:
        self._updated_at = time.time()
        self._health_cache = None

    def _invalidate_health(self) -> None:
        self._health_cache = None

    def _require_active(self) -> None:
        if not self.active:
            raise RuntimeError(
                "MetricHealthAnalyzer is not active"
            )

    # ----------------------------------------------------------------------
    # Configuration
    # ----------------------------------------------------------------------

    def config(
        self,
        key: str | None = None,
        default: Any = None,
    ) -> Any:
        if key is None:
            return copy.deepcopy(self._config)

        return self._config.get(
            key,
            default,
        )

    def configure(
        self,
        **kwargs: Any,
    ) -> "MetricHealthAnalyzer":
        with self._lock:
            self._config.update(
                copy.deepcopy(kwargs)
            )
            self._touch()

        return self

    # ----------------------------------------------------------------------
    # Algorithm registry
    # ----------------------------------------------------------------------

    def _register_builtin_algorithms(self) -> None:
        self._algorithms = {
            "availability": {
                "name": "availability",
                "callable": self._algorithm_availability,
                "enabled": True,
                "builtin": True,
            },
            "reliability": {
                "name": "reliability",
                "callable": self._algorithm_reliability,
                "enabled": True,
                "builtin": True,
            },
            "latency": {
                "name": "latency",
                "callable": self._algorithm_latency,
                "enabled": True,
                "builtin": True,
            },
            "throughput": {
                "name": "throughput",
                "callable": self._algorithm_throughput,
                "enabled": True,
                "builtin": True,
            },
            "utilization": {
                "name": "utilization",
                "callable": self._algorithm_utilization,
                "enabled": True,
                "builtin": True,
            },
            "saturation": {
                "name": "saturation",
                "callable": self._algorithm_saturation,
                "enabled": True,
                "builtin": True,
            },
            "health_score": {
                "name": "health_score",
                "callable": self._algorithm_health_score,
                "enabled": True,
                "builtin": True,
            },
            "overall": {
                "name": "overall",
                "callable": self._algorithm_overall,
                "enabled": True,
                "builtin": True,
            },
            "custom": {
                "name": "custom",
                "callable": self._algorithm_custom,
                "enabled": True,
                "builtin": True,
            },
        }

    def register_algorithm(
        self,
        name: str,
        algorithm: Callable[..., Any],
        *,
        enabled: bool = True,
        **metadata: Any,
    ) -> "MetricHealthAnalyzer":
        if not callable(algorithm):
            raise TypeError(
                "algorithm must be callable"
            )

        if not isinstance(name, str) or not name:
            raise ValueError(
                "algorithm name must be a non-empty string"
            )

        with self._lock:
            entry = {
                "name": name,
                "callable": algorithm,
                "enabled": bool(enabled),
                "builtin": False,
            }

            entry.update(
                copy.deepcopy(metadata)
            )

            self._algorithms[name] = entry
            self._touch()

        return self

    def unregister_algorithm(
        self,
        name: str,
    ) -> "MetricHealthAnalyzer":
        return self.remove_algorithm(name)

    def remove_algorithm(
        self,
        name: str,
    ) -> "MetricHealthAnalyzer":
        with self._lock:
            self._algorithms.pop(
                name,
                None,
            )
            self._touch()

        return self

    def clear_algorithms(
        self,
    ) -> "MetricHealthAnalyzer":
        with self._lock:
            self._algorithms.clear()
            self._touch()

        return self

    def algorithm(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        entry = self._algorithms.get(name)

        if entry is None:
            return default

        return {
            key: value
            for key, value in entry.items()
        }

    def algorithms(self) -> dict[str, dict[str, Any]]:
        return {
            name: dict(entry)
            for name, entry in self._algorithms.items()
        }

    def algorithm_names(self) -> list[str]:
        return list(self._algorithms.keys())

    @property
    def algorithm_count(self) -> int:
        return len(self._algorithms)

    def contains_algorithm(
        self,
        name: str,
    ) -> bool:
        return name in self._algorithms

    def exists_algorithm(
        self,
        name: str,
    ) -> bool:
        return self.contains_algorithm(name)

    def enable_algorithm(
        self,
        name: str,
    ) -> "MetricHealthAnalyzer":
        entry = self._algorithms.get(name)

        if entry is None:
            raise KeyError(
                f"Unknown health algorithm: {name}"
            )

        entry["enabled"] = True
        self._touch()

        return self

    def disable_algorithm(
        self,
        name: str,
    ) -> "MetricHealthAnalyzer":
        entry = self._algorithms.get(name)

        if entry is None:
            raise KeyError(
                f"Unknown health algorithm: {name}"
            )

        entry["enabled"] = False
        self._touch()

        return self

    # ----------------------------------------------------------------------
    # Algorithm execution
    # ----------------------------------------------------------------------

    def execute_algorithm(
        self,
        name: str,
        metrics: Mapping[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        entry = self._algorithms.get(name)

        if entry is None:
            raise KeyError(
                f"Unknown health algorithm: {name}"
            )

        if not entry["enabled"]:
            raise RuntimeError(
                f"Health algorithm '{name}' is disabled"
            )

        algorithm = entry["callable"]

        self.emit(
            "before_algorithm",
            algorithm=name,
            metrics=metrics,
        )

        result = algorithm(
            metrics,
            **kwargs,
        )

        self.emit(
            "after_algorithm",
            algorithm=name,
            result=result,
        )

        return result

    # ----------------------------------------------------------------------
    # Main analysis API
    # ----------------------------------------------------------------------

    def analyze(
        self,
        metrics: Mapping[str, Any],
        *,
        method: str = "overall",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Analyze a single metric mapping.

        Contract:
        - Every accepted analysis increments ``analysis_count`` exactly once.
        - A healthy result increments ``health_count`` exactly once.
        - An execution failure increments ``error_count`` exactly once.
        - The exact result object returned by the algorithm is returned to
          the caller and stored as ``last_result``.
        - History stores independent deep copies of successful results.
        - Runtime state is finalized in ``finally``.
        """
        self._require_active()

        started = time.perf_counter()
        self._running = True
        self._analysis_count += 1

        self.emit(
            "before_analyze",
            metrics=metrics,
            method=method,
        )

        try:
            result = self.execute_algorithm(
                method,
                metrics,
                **kwargs,
            )

            # Count successful healthy analyses only.
            if result.get("healthy") is True:
                self._health_count += 1

            # Preserve the exact algorithm result object.
            self._last_result = result

            # History must never share mutable state with the caller/result.
            self._history.append(copy.deepcopy(result))

            self.emit(
                "after_analyze",
                method=method,
                result=result,
            )

            return result

        except Exception:
            self._error_count += 1
            raise

        finally:
            self._latency = time.perf_counter() - started
            self._running = False
            self._updated_at = time.time()

            # Any new analysis invalidates cached runtime health.
            self._health_cache = None

    def analyze_one(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Analyze one metric mapping using the overall algorithm.

        ``None`` is normalized to an empty mapping.
        """
        return self.analyze(
            {} if metrics is None else metrics,
            method="overall",
            **kwargs,
        )

    def analyze_many(
        self,
        metrics_list: Iterable[Mapping[str, Any]],
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple metric mappings sequentially.

        Each item is processed through ``analyze()``, so all counters,
        history, events, errors, and lifecycle semantics remain centralized.
        """
        return [
            self.analyze(
                metrics,
                **kwargs,
            )
            for metrics in metrics_list
        ]

    def analyze_batch(
        self,
        metrics_list: Iterable[Mapping[str, Any]],
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Compatibility alias for ``analyze_many()``.
        """
        return self.analyze_many(
            metrics_list,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    # Intentional API aliases
    # ----------------------------------------------------------------------

    run = analyze
    execute = analyze
    process = analyze

    # ----------------------------------------------------------------------
    # Metric normalization
    # ----------------------------------------------------------------------

    @staticmethod
    def _number(
        metrics: Mapping[str, Any],
        key: str,
        default: float,
    ) -> float:
        value = metrics.get(key, default)

        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def _result(
        algorithm: str,
        metric: float,
        threshold: float,
        healthy: bool,
        score: float,
    ) -> dict[str, Any]:
        return {
            "algorithm": algorithm,
            "metric": float(metric),
            "threshold": float(threshold),
            "healthy": bool(healthy),
            "score": float(
                max(0.0, min(100.0, score))
            ),
        }

    # ----------------------------------------------------------------------
    # Built-in algorithms
    # ----------------------------------------------------------------------

    def _algorithm_availability(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "availability",
            1.0,
        )

        threshold = float(
            self.config(
                "availability_threshold"
            )
        )

        score = metric * 100.0
        healthy = metric >= threshold

        return self._result(
            "availability",
            metric,
            threshold,
            healthy,
            score,
        )

    def availability(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_availability(
            metrics or {},
            **kwargs,
        )

    def _algorithm_reliability(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "reliability",
            1.0,
        )

        threshold = float(
            self.config(
                "reliability_threshold"
            )
        )

        score = metric * 100.0
        healthy = metric >= threshold

        return self._result(
            "reliability",
            metric,
            threshold,
            healthy,
            score,
        )

    def reliability(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_reliability(
            metrics or {},
            **kwargs,
        )

    def _algorithm_latency(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "latency",
            0.0,
        )

        threshold = float(
            self.config(
                "latency_threshold"
            )
        )

        if threshold <= 0.0:
            score = 0.0
        else:
            score = max(
                0.0,
                100.0 * (
                    1.0 - metric / threshold
                ),
            )

        healthy = metric <= threshold

        return self._result(
            "latency",
            metric,
            threshold,
            healthy,
            score,
        )

    def _algorithm_throughput(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "throughput",
            0.0,
        )

        threshold = float(
            self.config(
                "throughput_threshold"
            )
        )

        if threshold <= 0.0:
            score = 100.0
        else:
            score = min(
                100.0,
                max(
                    0.0,
                    100.0 * metric / threshold,
                ),
            )

        healthy = metric >= threshold

        return self._result(
            "throughput",
            metric,
            threshold,
            healthy,
            score,
        )

    def throughput(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_throughput(
            metrics or {},
            **kwargs,
        )

    def _algorithm_utilization(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "utilization",
            0.0,
        )

        threshold = float(
            self.config(
                "utilization_threshold"
            )
        )

        if threshold <= 0.0:
            score = 0.0
        else:
            score = max(
                0.0,
                100.0 * (
                    1.0 - metric / threshold
                ),
            )

        healthy = metric <= threshold

        return self._result(
            "utilization",
            metric,
            threshold,
            healthy,
            score,
        )

    def utilization(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_utilization(
            metrics or {},
            **kwargs,
        )

    def _algorithm_saturation(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        metric = self._number(
            metrics,
            "saturation",
            0.0,
        )

        threshold = float(
            self.config(
                "saturation_threshold"
            )
        )

        if threshold <= 0.0:
            score = 0.0
        else:
            score = max(
                0.0,
                100.0 * (
                    1.0 - metric / threshold
                ),
            )

        healthy = metric <= threshold

        return self._result(
            "saturation",
            metric,
            threshold,
            healthy,
            score,
        )

    def saturation(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_saturation(
            metrics or {},
            **kwargs,
        )

    # ----------------------------------------------------------------------
    # Composite algorithms
    # ----------------------------------------------------------------------

    def _algorithm_health_score(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        results = [
            self._algorithm_availability(metrics),
            self._algorithm_reliability(metrics),
            self._algorithm_latency(metrics),
            self._algorithm_throughput(metrics),
            self._algorithm_utilization(metrics),
            self._algorithm_saturation(metrics),
        ]

        score = (
            sum(
                item["score"]
                for item in results
            )
            / len(results)
        )

        healthy = (
            score
            >= float(
                self.config("healthy_score")
            )
        )

        return {
            "algorithm": "health_score",
            "metric": float(score),
            "threshold": float(
                self.config("healthy_score")
            ),
            "healthy": healthy,
            "score": float(score),
            "results": results,
        }

    def health_score(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_health_score(
            metrics or {},
            **kwargs,
        )

    def _algorithm_overall(
        self,
        metrics: Mapping[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        score_result = self._algorithm_health_score(
            metrics
        )

        score = float(
            score_result["score"]
        )

        healthy_threshold = float(
            self.config("healthy_score")
        )
        warning_threshold = float(
            self.config("warning_score")
        )

        results = score_result["results"]

        # Overall health is determined by the health state of
        # every evaluated component, not by the aggregate score.
        healthy = all(
            bool(item.get("healthy", False))
            for item in results
        )

        if healthy:
            level = "healthy"
        elif score >= warning_threshold:
            level = "warning"
        else:
            level = "critical"

        return {
            "algorithm": "overall",
            "metric": score,
            "score": score,
            "healthy": healthy,
            "level": level,
            "threshold": healthy_threshold,
            "results": results,
        }

    def overall(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_overall(
            metrics or {},
            **kwargs,
        )

    def _algorithm_custom(
        self,
        metrics: Mapping[str, Any],
        analyzer: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not callable(analyzer):
            raise TypeError(
                "analyzer must be callable"
            )

        return analyzer(
            metrics,
            **kwargs,
        )

    def custom(
        self,
        metrics: Mapping[str, Any] | None = None,
        analyzer: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._algorithm_custom(
            metrics or {},
            analyzer,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    # Lifecycle
    # ----------------------------------------------------------------------

    def enable(self) -> "MetricHealthAnalyzer":
        self.enabled = True
        self.frozen = False
        self._touch()
        return self

    def disable(self) -> "MetricHealthAnalyzer":
        self.enabled = False
        self.running = False
        self._touch()
        return self

    def freeze(self) -> "MetricHealthAnalyzer":
        self.frozen = True
        self.running = False
        self._touch()
        return self

    def unfreeze(self) -> "MetricHealthAnalyzer":
        self.frozen = False
        self._touch()
        return self

    def close(self) -> "MetricHealthAnalyzer":
        self.closed = True
        self.running = False
        self._touch()
        return self

    def reopen(self) -> "MetricHealthAnalyzer":
        self.closed = False
        self._touch()
        return self

    # ----------------------------------------------------------------------
    # Reset / clear
    # ----------------------------------------------------------------------

    def reset(self) -> "MetricHealthAnalyzer":
        with self._lock:
            self._health_count = 0
            self._analysis_count = 0
            self._error_count = 0
            self._latency = 0.0
            self.running = False

            self._last_result = None
            self._history.clear()

            self._touch()

        return self

    def clear(self) -> "MetricHealthAnalyzer":
        with self._lock:
            self._history.clear()
            self._last_result = None
            self._touch()

        return self

    def clear_history(self) -> "MetricHealthAnalyzer":
        return self.clear()

    # ----------------------------------------------------------------------
    # Snapshot / restore
    # ----------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        snapshot = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "config": copy.deepcopy(
                self._config
            ),
            "health_count": self._health_count,
            "analysis_count": self._analysis_count,
            "error_count": self._error_count,
            "latency": self._latency,
            "history": copy.deepcopy(
                self._history
            ),
            "last_result": copy.deepcopy(
                self._last_result
            ),
        }

        self._snapshot = copy.deepcopy(
            snapshot
        )

        return copy.deepcopy(snapshot)

    def restore(
        self,
        snapshot: Mapping[str, Any] | None = None,
    ) -> "MetricHealthAnalyzer":
        if snapshot is None:
            snapshot = self._snapshot

        if snapshot is None:
            return self

        with self._lock:
            if "config" in snapshot:
                self._config = copy.deepcopy(
                    snapshot["config"]
                )

            self.enabled = bool(
                snapshot.get(
                    "enabled",
                    self.enabled,
                )
            )

            self.frozen = bool(
                snapshot.get(
                    "frozen",
                    self.frozen,
                )
            )

            self.closed = bool(
                snapshot.get(
                    "closed",
                    self.closed,
                )
            )

            self._health_count = int(
                snapshot.get(
                    "health_count",
                    0,
                )
            )

            self._analysis_count = int(
                snapshot.get(
                    "analysis_count",
                    0,
                )
            )

            self._error_count = int(
                snapshot.get(
                    "error_count",
                    0,
                )
            )

            self._latency = float(
                snapshot.get(
                    "latency",
                    0.0,
                )
            )

            self._history = copy.deepcopy(
                snapshot.get(
                    "history",
                    [],
                )
            )

            self._last_result = copy.deepcopy(
                snapshot.get(
                    "last_result"
                )
            )

            self._touch()

        return self

    # ----------------------------------------------------------------------
    # Clone / copy protocol
    # ----------------------------------------------------------------------

    def clone(self) -> "MetricHealthAnalyzer":
        cloned = self.__class__(
            name=self.name,
            description=self.description,
            config=self._config,
        )

        cloned.id = self.id
        cloned.version = self.version

        cloned.enabled = self.enabled
        cloned.frozen = self.frozen
        cloned.closed = self.closed
        cloned.running = False

        cloned._health_count = self._health_count
        cloned._analysis_count = self._analysis_count
        cloned._error_count = self._error_count
        cloned._latency = self._latency

        cloned._history = copy.deepcopy(
            self._history
        )

        cloned._last_result = copy.deepcopy(
            self._last_result
        )

        cloned._snapshot = copy.deepcopy(
            self._snapshot
        )

        cloned._context = copy.deepcopy(
            self._context
        )

        cloned._events = copy.deepcopy(
            self._events
        )

        cloned._created_at = self._created_at
        cloned._updated_at = self._updated_at

        # Preserve registered algorithms.
        # Built-in bound methods must belong to the clone.
        builtin_names = set(
            self.BUILTIN_ALGORITHMS
        )

        for name, entry in self._algorithms.items():
            if name in builtin_names:
                builtin_callable = getattr(
                    cloned,
                    f"_algorithm_{name}",
                    None,
                )

                if builtin_callable is not None:
                    cloned._algorithms[name][
                        "enabled"
                    ] = entry["enabled"]

                    for key, value in entry.items():
                        if key not in {
                            "name",
                            "callable",
                            "enabled",
                            "builtin",
                        }:
                            cloned._algorithms[name][
                                key
                            ] = copy.deepcopy(value)
            else:
                cloned._algorithms[name] = {
                    key: (
                        value
                        if key == "callable"
                        else copy.deepcopy(value)
                    )
                    for key, value in entry.items()
                }

        return cloned

    def copy(self) -> "MetricHealthAnalyzer":
        return self.clone()

    def __copy__(self) -> "MetricHealthAnalyzer":
        return self.clone()

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricHealthAnalyzer":
        cloned = self.clone()
        memo[id(self)] = cloned
        return cloned

    # ----------------------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        algorithms = {}

        for name, entry in self._algorithms.items():
            algorithms[name] = {
                key: value
                for key, value in entry.items()
                if key != "callable"
            }

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "config": copy.deepcopy(
                self._config
            ),
            "health_count": self._health_count,
            "analysis_count": self._analysis_count,
            "error_count": self._error_count,
            "latency": self._latency,
            "history": copy.deepcopy(
                self._history
            ),
            "last_result": copy.deepcopy(
                self._last_result
            ),
            "algorithms": algorithms,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricHealthAnalyzer":
        restored = cls(
            name=str(
                data.get(
                    "name",
                    "MetricHealthAnalyzer",
                )
            ),
            description=str(
                data.get(
                    "description",
                    "",
                )
            ),
            config=data.get(
                "config",
                {},
            ),
        )

        # Deserialization deliberately creates a NEW identity.
        restored.enabled = bool(
            data.get(
                "enabled",
                True,
            )
        )

        restored.frozen = bool(
            data.get(
                "frozen",
                False,
            )
        )

        restored.closed = bool(
            data.get(
                "closed",
                False,
            )
        )

        restored._health_count = int(
            data.get(
                "health_count",
                0,
            )
        )

        restored._analysis_count = int(
            data.get(
                "analysis_count",
                0,
            )
        )

        restored._error_count = int(
            data.get(
                "error_count",
                0,
            )
        )

        restored._latency = float(
            data.get(
                "latency",
                0.0,
            )
        )

        restored._history = copy.deepcopy(
            data.get(
                "history",
                [],
            )
        )

        restored._last_result = copy.deepcopy(
            data.get(
                "last_result"
            )
        )

        serialized_algorithms = data.get(
            "algorithms",
            {},
        )

        for name, entry in serialized_algorithms.items():
            if name in restored._algorithms:
                restored._algorithms[name][
                    "enabled"
                ] = bool(
                    entry.get(
                        "enabled",
                        True,
                    )
                )

        restored._touch()

        return restored

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            default=str,
        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> "MetricHealthAnalyzer":
        return cls.from_dict(
            json.loads(data)
        )

    def serialize(self) -> str:
        return self.to_json()

    @classmethod
    def deserialize(
        cls,
        data: str,
    ) -> "MetricHealthAnalyzer":
        return cls.from_json(data)

    # ----------------------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """
        Return a stable diagnostic snapshot.

        The result is cached so:

            analyzer.status() == analyzer.health()

        remains deterministic even though uptime is time-dependent.
        """
        if self._health_cache is None:
            if self.closed:
                state = "closed"
                healthy = False
            elif self.frozen:
                state = "frozen"
                healthy = False
            elif self.disabled:
                state = "disabled"
                healthy = False
            elif self.running:
                state = "running"
                healthy = True
            else:
                state = "idle"
                healthy = True

            self._health_cache = {
                "id": self.id,
                "name": self.name,
                "version": self.version,
                "state": state,
                "healthy": healthy,
                "enabled": self.enabled,
                "disabled": self.disabled,
                "frozen": self.frozen,
                "closed": self.closed,
                "running": self.running,
                "active": self.active,
                "errors": self._error_count,
                "health_count": self._health_count,
                "analysis_count": self._analysis_count,
                "uptime": self.uptime,
            }

        return copy.deepcopy(
            self._health_cache
        )

    def status(self) -> dict[str, Any]:
        return self.health()

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "health_count": self._health_count,
            "analysis_count": self._analysis_count,
            "error_count": self._error_count,
            "latency": self._latency,
            "uptime": self.uptime,
            "algorithms": self.algorithm_names(),
            "active": self.active,
        }

    def report(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "configuration": self.config(),
            "history": copy.deepcopy(
                self._history
            ),
            "last_result": copy.deepcopy(
                self._last_result
            ),
            "statistics": {
                "health_count": self._health_count,
                "analysis_count": self._analysis_count,
                "error_count": self._error_count,
                "latency": self._latency,
            },
        }

    # ----------------------------------------------------------------------
    # Events / hooks
    # ----------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> "MetricHealthAnalyzer":
        if not callable(callback):
            raise TypeError(
                "callback must be callable"
            )

        self._hooks.setdefault(
            event,
            [],
        ).append(callback)

        return self

    def subscribe(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> "MetricHealthAnalyzer":
        return self.add_hook(
            event,
            callback,
        )

    def remove_hook(
        self,
        event: str,
        callback: Callable[..., Any] | None = None,
    ) -> "MetricHealthAnalyzer":
        callbacks = self._hooks.get(event)

        if not callbacks:
            return self

        if callback is None:
            callbacks.clear()
        else:
            self._hooks[event] = [
                item
                for item in callbacks
                if item is not callback
            ]

        return self

    def emit(
        self,
        event: str,
        **payload: Any,
    ) -> "MetricHealthAnalyzer":
        record = {
            "event": event,
            "payload": copy.deepcopy(
                payload
            ),
            "timestamp": time.time(),
        }

        self._events.append(record)

        callbacks = list(
            self._hooks.get(
                event,
                [],
            )
        )

        for callback in callbacks:
            try:
                callback(
                    self,
                    **payload,
                )
            except Exception:
                # Hook failures are intentionally isolated from runtime
                # analysis. Observability hooks must never break execution.
                continue

        return self

    # ----------------------------------------------------------------------
    # Python protocols
    # ----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"enabled={self.enabled!r}, "
            f"algorithms={self.algorithm_count}, "
            f"analyses={self.analysis_count}, "
            f"healthy={self.health_count}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"{self.name}("
            f"algorithms={self.algorithm_count}, "
            f"analyses={self.analysis_count}, "
            f"healthy={self.health_count}"
            f")"
        )

    def __len__(self) -> int:
        return self.algorithm_count

    def __iter__(self):
        return iter(
            self.algorithms().items()
        )

    def __contains__(
        self,
        name: object,
    ) -> bool:
        return name in self._algorithms

    def __call__(
        self,
        metrics: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.analyze(
            metrics,
            **kwargs,
        )