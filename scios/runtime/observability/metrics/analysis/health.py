"""
SciOS-NG Runtime Metrics Analysis

Runtime Health Analysis Engine

SciOS/scios/runtime/observability/metrics/analysis/health.py
"""

from __future__ import annotations

import threading
import time
import uuid

from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics


# ==========================================================
# MetricHealthAnalyzer
# ==========================================================

class MetricHealthAnalyzer:
    """
    Runtime Health Analysis Engine.

    Foundation
    ----------
    - Health Registry
    - Algorithm Registry
    - Runtime State
    - Health Configuration
    - Statistics Engine
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        name: str = "MetricHealthAnalyzer",
        description: str = "",
    ) -> None:

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(uuid.uuid4())

        self._name = name

        self._description = description

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._running = False

        # --------------------------------------------------
        # Health Configuration
        # --------------------------------------------------

        self._config = {

            "healthy_score": 90.0,

            "warning_score": 70.0,

            "critical_score": 50.0,

            "latency_threshold": 100.0,

            "throughput_threshold": 100.0,

            "utilization_threshold": 0.85,

            "availability_threshold": 0.99,

            "reliability_threshold": 0.95,

        }

        # --------------------------------------------------
        # Health Registry
        # --------------------------------------------------

        self._algorithms: dict[
            str,
            dict,
        ] = {}

        self._registry = self._algorithms

        self._history: list[dict] = []

        self._last_result = None

        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------

        self._lock = threading.RLock()

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._version = "0.2.0"

        self._started_at = (
            time.perf_counter()
        )

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._statistics = MetricStatistics()

        self._health_count = 0

        self._analysis_count = 0

        self._error_count = 0

        self._latency = 0.0

        self._uptime = 0.0

        # --------------------------------------------------
        # Internal Components
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable],
        ] = {}

        self._events: list[
            dict
        ] = []

        self._snapshot = None

        self._context: dict[
            str,
            Any,
        ] = {}

        # --------------------------------------------------
        # Built-in Algorithms
        # --------------------------------------------------

        self.register_builtin_algorithms()

    # ======================================================
    # Identity
    # ======================================================

    @property
    def id(self):

        return self._id

    @property
    def name(self):

        return self._name

    @property
    def description(self):

        return self._description

    # ======================================================
    # Runtime State
    # ======================================================

    @property
    def enabled(self):

        return self._enabled

    @property
    def disabled(self):

        return not self._enabled

    @property
    def frozen(self):

        return self._frozen

    @property
    def closed(self):

        return self._closed

    @property
    def running(self):

        return self._running

    @property
    def active(self):

        return (

            self._enabled

            and

            not self._frozen

            and

            not self._closed

        )

    # ======================================================
    # Health Configuration
    # ======================================================

    def config(
        self,
        key: str | None = None,
        default=None,
    ):

        if key is None:

            return dict(
                self._config
            )

        return self._config.get(
            key,
            default,
        )

    def configure(
        self,
        **kwargs,
    ):

        with self._lock:

            self._config.update(
                kwargs
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def statistics(self):

        return self._statistics

    @property
    def health_count(self):

        return self._health_count

    @property
    def analysis_count(self):

        return self._analysis_count

    @property
    def error_count(self):

        return self._error_count

    # ======================================================
    # Metadata
    # ======================================================

    @property
    def created_at(self):

        return self._created_at

    @property
    def updated_at(self):

        return self._updated_at

    @property
    def version(self):

        return self._version

    # ======================================================
    # NOTE
    # ======================================================
    # Part 2  : Health Analysis API
    # Part 3  : Health Algorithms
    # Part 4  : Health Registry API
    # Part 5  : Lifecycle
    # Part 6  : Runtime Operations
    # Part 7  : Statistics & Diagnostics
    # Part 8  : Serialization
    # Part 9  : Events & Hooks
    # Part 10 : Python Protocols
    # ======================================================
    # ======================================================
    # Part 2. Health Analysis API
    # ======================================================

    def analyze(
        self,
        metrics,
        method: str = "overall",
        **kwargs,
    ):
        """
        Generic runtime health analysis.
        """

        if not self.active:

            raise RuntimeError(
                "MetricHealthAnalyzer is not active."
            )

        entry = self._algorithms.get(
            method
        )

        if entry is None:

            raise KeyError(
                f"Unknown health algorithm: {method}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Health algorithm '{method}' is disabled."
            )

        self.before_analyze(

            metrics,

            method,

            **kwargs,

        )

        self.before_algorithm(
            method
        )

        start = time.perf_counter()

        self._running = True

        try:

            result = entry["callable"](

                metrics,

                **kwargs,

            )

            self._latency = (

                time.perf_counter()

                -

                start

            )

            self.after_algorithm(

                method,

                result,

            )

            self.after_analyze(

                result,

                method,

            )

            self._analysis_count += 1

            if isinstance(
                result,
                dict,
            ):

                if result.get(
                    "healthy",
                    False,
                ):

                    self._health_count += 1

            self._last_result = result

            self._history.append(
                result
            )

            self._updated_at = datetime.utcnow()

            return result

        except Exception:

            self._error_count += 1

            raise

        finally:

            self._running = False

    def analyze_one(
        self,
        metrics,
        method: str = "overall",
        **kwargs,
    ):
        """
        Analyze one runtime snapshot.
        """

        return self.analyze(

            metrics,

            method=method,

            **kwargs,

        )

    def analyze_many(
        self,
        datasets,
        method: str = "overall",
        **kwargs,
    ):
        """
        Analyze multiple runtime snapshots.
        """

        results = []

        for metrics in datasets:

            results.append(

                self.analyze(

                    metrics,

                    method=method,

                    **kwargs,

                )

            )

        return results

    def analyze_batch(
        self,
        batches,
        method: str = "overall",
        **kwargs,
    ):
        """
        Batch runtime health analysis.
        """

        return self.analyze_many(

            batches,

            method=method,

            **kwargs,

        )

    # ------------------------------------------------------
    # Aliases
    # ------------------------------------------------------

    run = analyze

    execute = analyze

    process = analyze
    # ======================================================
    # Part 3. Health Algorithms
    # ======================================================

    def availability(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Analyze system availability.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "availability_threshold"
            ]

        )

        value = float(

            metrics.get(
                "availability",
                1.0,
            )

        )

        return {

            "algorithm": "availability",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value >= threshold,

            "score":
                min(
                    100.0,
                    value * 100.0,
                ),

        }

    def reliability(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Analyze system reliability.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "reliability_threshold"
            ]

        )

        value = float(

            metrics.get(
                "reliability",
                1.0,
            )

        )

        return {

            "algorithm": "reliability",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value >= threshold,

            "score":
                min(
                    100.0,
                    value * 100.0,
                ),

        }

    def latency(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Analyze latency health.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "latency_threshold"
            ]

        )

        value = float(

            metrics.get(
                "latency",
                0.0,
            )

        )

        score = max(

            0.0,

            100.0

            *

            (

                1.0

                -

                min(
                    value / threshold,
                    1.0,
                )

            ),

        )

        return {

            "algorithm": "latency",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value <= threshold,

            "score": score,

        }

    def throughput(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Analyze throughput health.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "throughput_threshold"
            ]

        )

        value = float(

            metrics.get(
                "throughput",
                0.0,
            )

        )

        score = min(

            100.0,

            (

                value

                /

                threshold

            )

            * 100.0,

        )

        return {

            "algorithm": "throughput",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value >= threshold,

            "score": score,

        }

    def utilization(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Analyze utilization health.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "utilization_threshold"
            ]

        )

        value = float(

            metrics.get(
                "utilization",
                0.0,
            )

        )

        score = max(

            0.0,

            100.0

            *

            (

                1.0

                -

                min(
                    value / threshold,
                    1.0,
                )

            ),

        )

        return {

            "algorithm": "utilization",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value <= threshold,

            "score": score,

        }

    def saturation(
        self,
        metrics,
        *,
        threshold: float = 1.0,
    ):
        """
        Analyze resource saturation.
        """

        value = float(

            metrics.get(
                "saturation",
                0.0,
            )

        )

        score = max(

            0.0,

            100.0

            *

            (

                1.0

                -

                min(
                    value / threshold,
                    1.0,
                )

            ),

        )

        return {

            "algorithm": "saturation",

            "metric": value,

            "threshold": threshold,

            "healthy":
                value <= threshold,

            "score": score,

        }

    def health_score(
        self,
        metrics,
    ):
        """
        Compute overall health score.
        """

        results = [

            self.availability(metrics),

            self.reliability(metrics),

            self.latency(metrics),

            self.throughput(metrics),

            self.utilization(metrics),

            self.saturation(metrics),

        ]

        score = sum(

            item["score"]

            for item in results

        ) / len(results)

        return {

            "algorithm": "health_score",

            "healthy":
                score >= self._config[
                    "warning_score"
                ],

            "score": score,

            "results": results,

        }

    def overall(
        self,
        metrics,
    ):
        """
        Overall runtime health analysis.
        """

        result = self.health_score(
            metrics
        )

        score = result["score"]

        if score >= self._config[
            "healthy_score"
        ]:

            level = "healthy"

        elif score >= self._config[
            "warning_score"
        ]:

            level = "warning"

        else:

            level = "critical"

        result.update(

            {

                "algorithm":
                    "overall",

                "level":
                    level,

            }

        )

        return result

    def custom(
        self,
        metrics,
        analyzer,
        **kwargs,
    ):
        """
        User-defined health analyzer.
        """

        if not callable(
            analyzer
        ):

            raise TypeError(
                "analyzer must be callable."
            )

        return analyzer(

            metrics,

            **kwargs,

        )
    # ======================================================
    # Part 4. Health Registry API
    # ======================================================

    def register_algorithm(
        self,
        name: str,
        algorithm: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a health analysis algorithm.
        """

        if not callable(algorithm):

            raise TypeError(
                "algorithm must be callable."
            )

        with self._lock:

            self._algorithms[name] = {

                "name": name,

                "callable": algorithm,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self

    def remove_algorithm(
        self,
        name: str,
    ):
        """
        Remove a registered algorithm.
        """

        with self._lock:

            self._algorithms.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # ------------------------------------------------------
    # Backward Compatibility
    # ------------------------------------------------------

    unregister_algorithm = remove_algorithm

    def algorithm(
        self,
        name: str,
        default=None,
    ):
        """
        Return algorithm metadata.
        """

        return self._algorithms.get(
            name,
            default,
        )

    def algorithms(
        self,
    ):
        """
        Return all registered algorithms.
        """

        return dict(
            self._algorithms
        )

    def contains_algorithm(
        self,
        name: str,
    ) -> bool:
        """
        Whether an algorithm exists.
        """

        return (

            name

            in

            self._algorithms

        )

    def exists_algorithm(
        self,
        name: str,
    ) -> bool:
        """
        Alias of contains_algorithm().
        """

        return self.contains_algorithm(
            name
        )

    def enable_algorithm(
        self,
        name: str,
    ):
        """
        Enable a registered algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is not None:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_algorithm(
        self,
        name: str,
    ):
        """
        Disable a registered algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is not None:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def algorithm_names(
        self,
    ):
        """
        Return registered algorithm names.
        """

        return list(
            self._algorithms.keys()
        )

    @property
    def algorithm_count(
        self,
    ) -> int:
        """
        Number of registered algorithms.
        """

        return len(
            self._algorithms
        )

    def clear_algorithms(
        self,
    ):
        """
        Remove all registered algorithms.
        """

        with self._lock:

            self._algorithms.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_algorithm(
        self,
        name: str,
        metrics,
        **kwargs,
    ):
        """
        Execute a registered algorithm.
        """

        entry = self._algorithms.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown health algorithm: {name}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Health algorithm '{name}' is disabled."
            )

        return entry["callable"](

            metrics,

            **kwargs,

        )

    def register_builtin_algorithms(
        self,
    ):
        """
        Register all built-in health algorithms.
        """

        self.register_algorithm(
            "availability",
            self.availability,
        )

        self.register_algorithm(
            "reliability",
            self.reliability,
        )

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
            "saturation",
            self.saturation,
        )

        self.register_algorithm(
            "health_score",
            self.health_score,
        )

        self.register_algorithm(
            "overall",
            self.overall,
        )

        self.register_algorithm(
            "custom",
            self.custom,
        )

        return self
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable the health analyzer.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the health analyzer.
        """

        with self._lock:

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def freeze(
        self,
    ):
        """
        Freeze the health analyzer.
        """

        with self._lock:

            self._frozen = True

            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(
        self,
    ):
        """
        Unfreeze the health analyzer.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the health analyzer.
        """

        with self._lock:

            self._closed = True

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def reopen(
        self,
    ):
        """
        Reopen the health analyzer.
        """

        with self._lock:

            self._closed = False

            self._updated_at = datetime.utcnow()

        return self
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(
        self,
    ):
        """
        Reset runtime state while preserving configuration
        and registered algorithms.
        """

        with self._lock:

            self._health_count = 0

            self._analysis_count = 0

            self._error_count = 0

            self._latency = 0.0

            self._running = False

            self._last_result = None

            self._history.clear()

            self._updated_at = datetime.utcnow()

        return self

    def clear(
        self,
    ):
        """
        Clear runtime history.
        """

        with self._lock:

            self._history.clear()

            self._last_result = None

            self._updated_at = datetime.utcnow()

        return self

    def snapshot(
        self,
    ):
        """
        Create a runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                "config": dict(
                    self._config
                ),

                "history": list(
                    self._history
                ),

                "last_result":
                    self._last_result,

                "health_count":
                    self._health_count,

                "analysis_count":
                    self._analysis_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._latency,

                "enabled":
                    self._enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "updated_at":
                    self._updated_at,

            }

            return dict(
                self._snapshot
            )

    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime state from a snapshot.
        """

        if snapshot is None:

            snapshot = self._snapshot

        if snapshot is None:

            return self

        with self._lock:

            self._config = dict(

                snapshot.get(
                    "config",
                    {},
                )

            )

            self._history = list(

                snapshot.get(
                    "history",
                    [],
                )

            )

            self._last_result = snapshot.get(
                "last_result"
            )

            self._health_count = snapshot.get(
                "health_count",
                0,
            )

            self._analysis_count = snapshot.get(
                "analysis_count",
                0,
            )

            self._error_count = snapshot.get(
                "error_count",
                0,
            )

            self._latency = snapshot.get(
                "latency",
                0.0,
            )

            self._enabled = snapshot.get(
                "enabled",
                True,
            )

            self._frozen = snapshot.get(
                "frozen",
                False,
            )

            self._closed = snapshot.get(
                "closed",
                False,
            )

            self._updated_at = datetime.utcnow()

        return self

    def clone(
        self,
    ):
        """
        Create a cloned analyzer.
        """

        cloned = self.__class__(

            name=self._name,

            description=self._description,

        )

        cloned.restore(
            self.snapshot()
        )

        return cloned

    def copy(
        self,
    ):
        """
        Alias of clone().
        """

        return self.clone()
    # ======================================================
    # Part 7. Statistics & Diagnostics
    # ======================================================

    def summary(
        self,
    ) -> dict:
        """
        Return runtime summary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "version": self._version,

            "enabled": self._enabled,

            "running": self._running,

            "health_count":
                self._health_count,

            "analysis_count":
                self._analysis_count,

            "error_count":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

            "algorithms":
                self.algorithm_names(),

        }

    def report(
        self,
    ) -> dict:
        """
        Return detailed runtime report.
        """

        return {

            "summary":
                self.summary(),

            "configuration":
                dict(self._config),

            "history":
                list(self._history),

            "last_result":
                self._last_result,

            "statistics":
                self._statistics,

            "created_at":
                self._created_at,

            "updated_at":
                self._updated_at,

        }

    def health(
        self,
    ) -> dict:
        """
        Runtime health diagnostics.
        """

        if self._closed:

            state = "closed"

        elif self._frozen:

            state = "frozen"

        elif not self._enabled:

            state = "disabled"

        elif self._running:

            state = "running"

        else:

            state = "idle"

        return {

            "healthy":
                self.active,

            "state":
                state,

            "errors":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

        }

    def status(
        self,
    ) -> dict:
        """
        Alias of health().
        """

        return self.health()

    # ======================================================
    # Statistics Properties
    # ======================================================

    @property
    def health_count(
        self,
    ) -> int:
        """
        Number of healthy analyses.
        """

        return self._health_count

    @property
    def analysis_count(
        self,
    ) -> int:
        """
        Total number of analyses.
        """

        return self._analysis_count

    @property
    def error_count(
        self,
    ) -> int:
        """
        Total number of errors.
        """

        return self._error_count

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime (seconds).
        """

        return (

            time.perf_counter()

            -

            self._started_at

        )

    @property
    def latency(
        self,
    ) -> float:
        """
        Last analysis latency (seconds).
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    import json

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize analyzer to a dictionary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "description": self._description,

            "version": self._version,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "config": dict(
                self._config
            ),

            "health_count":
                self._health_count,

            "analysis_count":
                self._analysis_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "created_at":
                self._created_at.isoformat(),

            "updated_at":
                self._updated_at.isoformat(),

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):
        """
        Create an analyzer from a dictionary.
        """

        analyzer = cls(

            name=data.get(
                "name",
                "MetricHealthAnalyzer",
            ),

            description=data.get(
                "description",
                "",
            ),

        )

        analyzer._enabled = data.get(
            "enabled",
            True,
        )

        analyzer._frozen = data.get(
            "frozen",
            False,
        )

        analyzer._closed = data.get(
            "closed",
            False,
        )

        analyzer._config.update(

            data.get(
                "config",
                {},
            )

        )

        analyzer._health_count = data.get(
            "health_count",
            0,
        )

        analyzer._analysis_count = data.get(
            "analysis_count",
            0,
        )

        analyzer._error_count = data.get(
            "error_count",
            0,
        )

        analyzer._latency = data.get(
            "latency",
            0.0,
        )

        return analyzer

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize analyzer to JSON.
        """

        return json.dumps(

            self.to_dict(),

            **kwargs,

        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ):
        """
        Create an analyzer from JSON.
        """

        return cls.from_dict(

            json.loads(data)

        )

    def serialize(
        self,
        **kwargs,
    ) -> str:
        """
        Alias of to_json().
        """

        return self.to_json(
            **kwargs
        )

    @classmethod
    def deserialize(
        cls,
        data: str,
    ):
        """
        Alias of from_json().
        """

        return cls.from_json(
            data
        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    def before_analyze(
        self,
        metrics,
        method: str,
        **kwargs,
    ):
        """
        Hook executed before health analysis.
        """

        self.emit(

            "before_analyze",

            metrics=metrics,

            method=method,

            kwargs=kwargs,

        )

        return self

    def after_analyze(
        self,
        result,
        method: str,
    ):
        """
        Hook executed after health analysis.
        """

        self.emit(

            "after_analyze",

            result=result,

            method=method,

        )

        return self

    def before_algorithm(
        self,
        name: str,
    ):
        """
        Hook executed before algorithm execution.
        """

        self.emit(

            "before_algorithm",

            algorithm=name,

        )

        return self

    def after_algorithm(
        self,
        name: str,
        result=None,
    ):
        """
        Hook executed after algorithm execution.
        """

        self.emit(

            "after_algorithm",

            algorithm=name,

            result=result,

        )

        return self

    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register an event hook.
        """

        if not callable(callback):

            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            self._hooks.setdefault(

                event,

                []

            ).append(

                callback

            )

        return self

    def remove_hook(
        self,
        event: str,
        callback: Callable | None = None,
    ):
        """
        Remove one hook or all hooks for an event.
        """

        with self._lock:

            if event not in self._hooks:

                return self

            if callback is None:

                self._hooks.pop(

                    event,

                    None,

                )

                return self

            try:

                self._hooks[event].remove(
                    callback
                )

            except ValueError:

                pass

            if not self._hooks[event]:

                self._hooks.pop(

                    event,

                    None,

                )

        return self

    def emit(
        self,
        event: str,
        **payload,
    ):
        """
        Emit an event.
        """

        record = {

            "timestamp":
                datetime.utcnow(),

            "event":
                event,

            "payload":
                payload,

        }

        self._events.append(
            record
        )

        for callback in self._hooks.get(
            event,
            [],
        ):

            callback(

                self,

                **payload,

            )

        return self

    def subscribe(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Alias of add_hook().
        """

        return self.add_hook(

            event,

            callback,

        )
    # ======================================================
    # Part 10. Python Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("

            f"name={self._name!r}, "

            f"enabled={self._enabled}, "

            f"algorithms={len(self._algorithms)}, "

            f"analyses={self._analysis_count}, "

            f"healthy={self._health_count}"

            f")"

        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "

            f"(algorithms={len(self._algorithms)}, "

            f"analyses={self._analysis_count}, "

            f"healthy={self._health_count})"

        )

    def __len__(
        self,
    ) -> int:
        """
        Number of registered algorithms.
        """

        return len(
            self._algorithms
        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered algorithms.
        """

        return iter(
            self._algorithms.items()
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an algorithm exists.
        """

        return (

            name

            in

            self._algorithms

        )

    def __call__(
        self,
        metrics,
        method: str = "overall",
        **kwargs,
    ):
        """
        Callable interface.

        Equivalent to analyze().
        """

        return self.analyze(

            metrics,

            method=method,

            **kwargs,

        )

    def __copy__(
        self,
    ):
        """
        Shallow copy.
        """

        return self.clone()

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy.
        """

        clone = self.clone()

        memo[id(self)] = clone

        return clone                                                                