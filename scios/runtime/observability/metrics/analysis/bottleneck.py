"""
SciOS-NG Runtime Metrics Analysis

Bottleneck Detection Engine

SciOS/scios/runtime/observability/metrics/analysis/bottleneck.py
"""

from __future__ import annotations

import threading
import time
import uuid

from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics


# ==========================================================
# MetricBottleneckDetector
# ==========================================================

class MetricBottleneckDetector:
    """
    Runtime Metrics Bottleneck Detection Engine.

    Features
    --------
    - Latency Detection
    - Throughput Analysis
    - Resource Utilization
    - Queue Analysis
    - Contention Detection
    - Saturation Detection
    - Dependency Analysis
    - Pipeline Bottleneck Detection
    - Custom Detection Algorithms
    """

    # ======================================================
    # Part 1. Foundation
    # ======================================================

    def __init__(
        self,
        name: str = "MetricBottleneckDetector",
        description: str = "",
    ) -> None:

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._id = str(uuid.uuid4())

        self._name = name

        self._description = description

        self._version = "0.2.0"

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False

        self._running = False

        # --------------------------------------------------
        # Bottleneck Configuration
        # --------------------------------------------------

        self._config = {

            "latency_threshold": 100.0,

            "throughput_threshold": 1000.0,

            "utilization_threshold": 0.80,

            "queue_threshold": 100,

            "contention_threshold": 0.75,

            "saturation_threshold": 0.90,

            "dependency_depth": 5,

        }

        # --------------------------------------------------
        # Detector Registry
        # --------------------------------------------------

        self._algorithms: dict[
            str,
            dict[str, Any],
        ] = {}

        self._history: list[dict] = []

        self._last_result: dict | None = None

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._started_at = time.perf_counter()

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self._statistics = MetricStatistics()

        self._bottleneck_count = 0

        self._detection_count = 0

        self._error_count = 0

        self._latency = 0.0

        # --------------------------------------------------
        # Events
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable],
        ] = {}

        self._events: list[dict] = []

        # --------------------------------------------------
        # Runtime Objects
        # --------------------------------------------------

        self._snapshot = None

        self._context: dict[
            str,
            Any,
        ] = {}

        self._lock = threading.RLock()

    # ======================================================
    # Identity
    # ======================================================

    @property
    def id(self) -> str:

        return self._id

    @property
    def name(self) -> str:

        return self._name

    @property
    def description(self) -> str:

        return self._description

    @property
    def version(self) -> str:

        return self._version

    # ======================================================
    # Runtime State
    # ======================================================

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

    @property
    def active(self) -> bool:

        return (

            self._enabled
            and
            not self._frozen
            and
            not self._closed

        )

    # ======================================================
    # Bottleneck Configuration
    # ======================================================

    @property
    def config(self) -> dict:

        return dict(
            self._config
        )

    def configure(
        self,
        **kwargs,
    ):
        """
        Update detector configuration.
        """

        with self._lock:

            self._config.update(
                kwargs
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Metadata
    # ======================================================

    @property
    def created_at(self):

        return self._created_at

    @property
    def updated_at(self):

        return self._updated_at

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def statistics(self):

        return self._statistics

    # ======================================================
    # NOTE
    # ======================================================
    # Part 2  : Detection API
    # Part 3  : Detection Algorithms
    # Part 4  : Detector Registry API
    # Part 5  : Lifecycle
    # Part 6  : Runtime Operations
    # Part 7  : Statistics & Diagnostics
    # Part 8  : Serialization
    # Part 9  : Events & Hooks
    # Part 10 : Python Protocols
    # ======================================================
    # ======================================================
    # Part 2. Detection API
    # ======================================================

    def detect(
        self,
        metrics,
        method: str = "latency",
        **kwargs,
    ):
        """
        Detect runtime bottlenecks.

        Parameters
        ----------
        metrics:
            Runtime metrics.

        method:
            Detection algorithm.

        Returns
        -------
        dict
        """

        if not self.active:

            raise RuntimeError(
                "MetricBottleneckDetector is not active."
            )

        entry = self._algorithms.get(
            method
        )

        if entry is None:

            raise KeyError(
                f"Unknown bottleneck algorithm: {method}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Bottleneck algorithm '{method}' is disabled."
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

            self._detection_count += 1

            if isinstance(
                result,
                dict,
            ):

                if result.get(
                    "bottleneck",
                    False,
                ):

                    self._bottleneck_count += 1

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

    def detect_one(
        self,
        metrics,
        method: str = "latency",
        **kwargs,
    ):
        """
        Detect bottleneck from one metric sample.
        """

        return self.detect(

            metrics,

            method=method,

            **kwargs,

        )

    def detect_many(
        self,
        datasets,
        method: str = "latency",
        **kwargs,
    ):
        """
        Detect bottlenecks from multiple datasets.
        """

        results = []

        for metrics in datasets:

            results.append(

                self.detect(

                    metrics,

                    method=method,

                    **kwargs,

                )

            )

        return results

    def detect_batch(
        self,
        batches,
        method: str = "latency",
        **kwargs,
    ):
        """
        Batch bottleneck detection.
        """

        return self.detect_many(

            batches,

            method=method,

            **kwargs,

        )

    # ------------------------------------------------------
    # Aliases
    # ------------------------------------------------------

    run = detect

    execute = detect

    process = detect
    # ======================================================
    # Part 3. Detection Algorithms
    # ======================================================

    def latency(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Detect latency bottlenecks.
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

        return {

            "algorithm": "latency",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "high"

                if value >= threshold

                else

                "normal",

        }

    def throughput(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Detect throughput bottlenecks.
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

        return {

            "algorithm": "throughput",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value <= threshold,

            "severity":

                "high"

                if value <= threshold

                else

                "normal",

        }

    def utilization(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Detect resource utilization bottlenecks.
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

        return {

            "algorithm": "utilization",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "high"

                if value >= threshold

                else

                "normal",

        }

    def queue(
        self,
        metrics,
        *,
        threshold: int | None = None,
    ):
        """
        Detect queue bottlenecks.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "queue_threshold"
            ]

        )

        value = int(

            metrics.get(
                "queue_size",
                0,
            )

        )

        return {

            "algorithm": "queue",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "high"

                if value >= threshold

                else

                "normal",

        }

    def contention(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Detect lock/contention bottlenecks.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "contention_threshold"
            ]

        )

        value = float(

            metrics.get(
                "contention",
                0.0,
            )

        )

        return {

            "algorithm": "contention",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "high"

                if value >= threshold

                else

                "normal",

        }

    def saturation(
        self,
        metrics,
        *,
        threshold: float | None = None,
    ):
        """
        Detect resource saturation.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "saturation_threshold"
            ]

        )

        value = float(

            metrics.get(
                "saturation",
                0.0,
            )

        )

        return {

            "algorithm": "saturation",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "critical"

                if value >= threshold

                else

                "normal",

        }

    def dependency(
        self,
        metrics,
        *,
        threshold: int | None = None,
    ):
        """
        Detect dependency-chain bottlenecks.
        """

        threshold = (

            threshold

            if threshold is not None

            else

            self._config[
                "dependency_depth"
            ]

        )

        value = int(

            metrics.get(
                "dependency_depth",
                0,
            )

        )

        return {

            "algorithm": "dependency",

            "metric": value,

            "threshold": threshold,

            "bottleneck":
                value >= threshold,

            "severity":

                "high"

                if value >= threshold

                else

                "normal",

        }

    def pipeline(
        self,
        metrics,
    ):
        """
        Detect pipeline bottlenecks using all
        built-in detectors.
        """

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

            item

            for item in results

            if item["bottleneck"]

        ]

        return {

            "algorithm": "pipeline",

            "bottleneck":
                bool(bottlenecks),

            "count":
                len(bottlenecks),

            "results":
                results,

        }

    def custom(
        self,
        metrics,
        detector,
        **kwargs,
    ):
        """
        User-defined bottleneck detector.
        """

        if not callable(
            detector
        ):

            raise TypeError(
                "detector must be callable."
            )

        return detector(

            metrics,

            **kwargs,

        )
    # ======================================================
    # Part 4. Detector Registry API
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
        Register a bottleneck detection algorithm.
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
                f"Unknown bottleneck algorithm: {name}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Bottleneck algorithm '{name}' is disabled."
            )

        return entry["callable"](

            metrics,

            **kwargs,

        )

    def register_builtin_algorithms(
        self,
    ):
        """
        Register all built-in detection algorithms.
        """

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
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(
        self,
    ):
        """
        Enable the bottleneck detector.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the bottleneck detector.
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
        Freeze the bottleneck detector.
        """

        with self._lock:

            self._frozen = True

            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(
        self,
    ):
        """
        Unfreeze the bottleneck detector.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the bottleneck detector.
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
        Reopen the bottleneck detector.
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
        Reset runtime statistics while preserving configuration
        and registered algorithms.
        """

        with self._lock:

            self._bottleneck_count = 0

            self._detection_count = 0

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

                "last_result": self._last_result,

                "bottleneck_count":
                    self._bottleneck_count,

                "detection_count":
                    self._detection_count,

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

            self._bottleneck_count = snapshot.get(
                "bottleneck_count",
                0,
            )

            self._detection_count = snapshot.get(
                "detection_count",
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
        Create a cloned detector.
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
        Return a runtime summary.
        """

        return {

            "name": self._name,

            "id": self._id,

            "version": self._version,

            "enabled": self._enabled,

            "running": self._running,

            "bottleneck_count":
                self._bottleneck_count,

            "detection_count":
                self._detection_count,

            "error_count":
                self._error_count,

            "uptime":
                self.uptime,

            "latency":
                self._latency,

            "algorithms":
                len(self._algorithms),

        }

    def report(
        self,
    ) -> dict:
        """
        Generate a diagnostic report.
        """

        return {

            "summary":
                self.summary(),

            "configuration":
                dict(self._config),

            "statistics":
                self._statistics,

            "history_size":
                len(self._history),

            "last_result":
                self._last_result,

        }

    def health(
        self,
    ) -> dict:
        """
        Runtime health information.
        """

        status = "healthy"

        if self._closed:

            status = "closed"

        elif not self._enabled:

            status = "disabled"

        elif self._frozen:

            status = "frozen"

        return {

            "status": status,

            "active": self.active,

            "running": self._running,

            "errors": self._error_count,

            "uptime": self.uptime,

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
    def bottleneck_count(
        self,
    ) -> int:
        """
        Number of detected bottlenecks.
        """

        return self._bottleneck_count

    @property
    def detection_count(
        self,
    ) -> int:
        """
        Number of detections.
        """

        return self._detection_count

    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of runtime errors.
        """

        return self._error_count

    @property
    def uptime(
        self,
    ) -> float:
        """
        Runtime uptime in seconds.
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
        Latest detection latency.
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize detector to dictionary.
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

            "bottleneck_count":
                self._bottleneck_count,

            "detection_count":
                self._detection_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "created_at":
                self._created_at.isoformat(),

            "updated_at":
                self._updated_at.isoformat(),

            "algorithm_names":
                self.algorithm_names(),

            "history":
                list(self._history),

            "last_result":
                self._last_result,

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):
        """
        Restore detector from dictionary.
        """

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

        obj._id = data.get(

            "id",

            obj._id,

        )

        obj._version = data.get(

            "version",

            obj._version,

        )

        obj._enabled = data.get(

            "enabled",

            True,

        )

        obj._frozen = data.get(

            "frozen",

            False,

        )

        obj._closed = data.get(

            "closed",

            False,

        )

        obj._config.update(

            data.get(

                "config",

                {},

            )

        )

        obj._bottleneck_count = data.get(

            "bottleneck_count",

            0,

        )

        obj._detection_count = data.get(

            "detection_count",

            0,

        )

        obj._error_count = data.get(

            "error_count",

            0,

        )

        obj._latency = data.get(

            "latency",

            0.0,

        )

        obj._history = list(

            data.get(

                "history",

                [],

            )

        )

        obj._last_result = data.get(

            "last_result"

        )

        created = data.get(

            "created_at"

        )

        if created:

            obj._created_at = datetime.fromisoformat(

                created

            )

        updated = data.get(

            "updated_at"

        )

        if updated:

            obj._updated_at = datetime.fromisoformat(

                updated

            )

        return obj

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize detector to JSON.
        """

        import json

        return json.dumps(

            self.to_dict(),

            **kwargs,

        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ):
        """
        Restore detector from JSON.
        """

        import json

        return cls.from_dict(

            json.loads(

                text

            )

        )

    def serialize(
        self,
    ) -> dict:
        """
        Alias of to_dict().
        """

        return self.to_dict()

    @classmethod
    def deserialize(
        cls,
        data,
    ):
        """
        Deserialize detector from dictionary or JSON.
        """

        if isinstance(

            data,

            str,

        ):

            return cls.from_json(

                data

            )

        return cls.from_dict(

            data

        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    def before_detect(
        self,
        metrics,
        method: str,
        **kwargs,
    ):
        """
        Hook executed before bottleneck detection.
        """

        self.emit(

            "before_detect",

            metrics=metrics,

            method=method,

            kwargs=kwargs,

        )

        return self

    def after_detect(
        self,
        result,
        method: str,
    ):
        """
        Hook executed after bottleneck detection.
        """

        self.emit(

            "after_detect",

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

            f"detections={self._detection_count}"

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

            f"detections={self._detection_count}, "

            f"bottlenecks={self._bottleneck_count})"

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
        method: str = "latency",
        **kwargs,
    ):
        """
        Callable interface.

        Equivalent to detect().
        """

        return self.detect(

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