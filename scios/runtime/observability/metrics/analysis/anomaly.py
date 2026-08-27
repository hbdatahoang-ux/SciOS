"""
SciOS-NG Runtime Metrics Analysis
=================================

Anomaly Detection Engine

Path
----
SciOS/scios/runtime/observability/metrics/analysis/anomaly.py

Design goals
------------
- Deterministic anomaly detection API
- Built-in detector registry
- Custom detector support
- Rule management
- Runtime lifecycle management
- Snapshot / restore
- Serialization
- Events and hooks
- Thread-safe runtime state
- Safe copy / deepcopy
- Python 3.11+

The detector is intentionally independent from the Metrics Collector,
Exporter, and Observability Pipeline layers.
"""

from __future__ import annotations

import copy
import json
import threading
import uuid

from datetime import datetime
from typing import Any, Callable, Iterable

from .statistics import MetricStatistics


# ============================================================================
# Types
# ============================================================================

DetectorCallable = Callable[..., dict[str, Any]]
RuleCallable = Callable[..., Any]
HookCallable = Callable[..., Any]


# ============================================================================
# MetricAnomalyDetector
# ============================================================================


class MetricAnomalyDetector:
    """
    Runtime Metrics Anomaly Detection Engine.

    Responsibilities
    ----------------
    - Maintain anomaly detection configuration.
    - Register detection algorithms.
    - Register custom rules.
    - Execute anomaly detection.
    - Maintain runtime statistics.
    - Emit runtime events.
    - Create and restore runtime snapshots.
    - Serialize detector configuration/state.

    Built-in detectors
    ------------------
    - threshold
    - zscore
    - modified_zscore
    - iqr
    - sigma
    - moving_average
    - rolling
    """

    VERSION = "0.2.0"

    DEFAULT_THRESHOLDS: dict[str, float] = {
        "warning": 0.80,
        "critical": 0.95,
        "zscore": 3.0,
        "mad": 3.5,
        "iqr": 1.5,
        "sigma": 3.0,
    }

    BUILTIN_DETECTORS: frozenset[str] = frozenset(
        {
            "threshold",
            "zscore",
            "modified_zscore",
            "iqr",
            "sigma",
            "moving_average",
            "rolling",
        }
    )

    # ========================================================================
    # Constructor
    # ========================================================================

    def __init__(
        self,
        name: str = "MetricAnomalyDetector",
        description: str = "",
    ) -> None:

        # --------------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------------

        self._id = str(uuid.uuid4())
        self._name = str(name)
        self._description = str(description)

        # --------------------------------------------------------------------
        # Runtime state
        # --------------------------------------------------------------------

        self._enabled = True
        self._frozen = False
        self._closed = False

        # --------------------------------------------------------------------
        # Configuration
        # --------------------------------------------------------------------

        self._thresholds: dict[str, float] = dict(
            self.DEFAULT_THRESHOLDS
        )

        # --------------------------------------------------------------------
        # Registries
        # --------------------------------------------------------------------

        self._detectors: dict[str, DetectorCallable] = {}

        self._rules: dict[str, dict[str, Any]] = {}

        # --------------------------------------------------------------------
        # Runtime data
        # --------------------------------------------------------------------

        self._history: list[dict[str, Any]] = []

        self._last_result: dict[str, Any] | None = None

        self._context: dict[str, Any] = {}

        # --------------------------------------------------------------------
        # Synchronization
        # --------------------------------------------------------------------

        self._lock = threading.RLock()

        # --------------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------------

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        self._version = self.VERSION

        # --------------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------------

        self._statistics = MetricStatistics()

        self._detection_count = 0
        self._anomaly_count = 0
        self._false_positive = 0

        self._latency = 0.0
        self._uptime = 0.0

        # --------------------------------------------------------------------
        # Events / hooks
        # --------------------------------------------------------------------

        self._hooks: dict[str, list[HookCallable]] = {}

        self._events: list[dict[str, Any]] = []

        # --------------------------------------------------------------------
        # Snapshot
        # --------------------------------------------------------------------

        self._snapshot: dict[str, Any] | None = None

        # --------------------------------------------------------------------
        # Register built-in detectors
        # --------------------------------------------------------------------

        self._register_builtin_detectors()

    # ========================================================================
    # Internal Helpers
    # ========================================================================

    @staticmethod
    def _now() -> datetime:
        """Return current UTC timestamp."""

        return datetime.utcnow()

    def _touch(self) -> None:
        """Update runtime modification timestamp."""

        self._updated_at = self._now()

    def _require_active(self) -> None:
        """Raise if detector cannot execute."""

        if not self.active:
            raise RuntimeError(
                "MetricAnomalyDetector is not active."
            )

    def _register_builtin_detectors(self) -> None:
        """Register built-in detection algorithms."""

        self._detectors.update(
            {
                "threshold": self.threshold,
                "zscore": self.zscore,
                "modified_zscore": self.modified_zscore,
                "iqr": self.iqr,
                "sigma": self.sigma,
                "moving_average": self.moving_average,
                "rolling": self.rolling,
            }
        )

    # ========================================================================
    # Identity
    # ========================================================================

    @property
    def id(self) -> str:
        """Detector identifier."""

        return self._id

    @property
    def name(self) -> str:
        """Detector name."""

        return self._name

    @property
    def description(self) -> str:
        """Detector description."""

        return self._description

    # ========================================================================
    # Runtime State
    # ========================================================================

    @property
    def enabled(self) -> bool:
        """Whether detector execution is enabled."""

        return self._enabled

    @property
    def disabled(self) -> bool:
        """Whether detector execution is disabled."""

        return not self._enabled

    @property
    def frozen(self) -> bool:
        """Whether detector execution is frozen."""

        return self._frozen

    @property
    def closed(self) -> bool:
        """Whether detector has been permanently closed."""

        return self._closed

    @property
    def active(self) -> bool:
        """Whether detector is ready for runtime execution."""

        return (
            self._enabled
            and not self._frozen
            and not self._closed
        )


    @property
    def last_result(self):
        """Return the most recent detection result."""
        return self._last_result


    def threshold_value(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Return a configured threshold value.

        Parameters
        ----------
        name:
            Threshold name.
        default:
            Value returned when the threshold does not exist.
        """

        if not isinstance(name, str) or not name:
            raise ValueError(
                "threshold name must be a non-empty string."
            )

        with self._lock:
            return self._thresholds.get(
                name,
                default,
            )


    # ========================================================================
    # Threshold Configuration
    # ========================================================================

    def threshold(
        self,
        values,
        threshold: float | None = None,
        *,
        absolute: bool = False,
    ):
        """
        Threshold anomaly detection.

        Compatibility behavior
        -----------------------
        ``detector.threshold("zscore")`` returns a configured threshold.

        ``detector.threshold(values, threshold=...)`` performs
        threshold-based anomaly detection.

        This dual behavior preserves the historical SciOS API while
        eliminating the duplicate ``threshold()`` definition.
        """

        # Compatibility getter.
        if isinstance(values, str) and threshold is None:
            return self._thresholds.get(values)

        if threshold is None:
            threshold = self._thresholds["warning"]

        threshold = float(threshold)

        anomalies: list[dict[str, Any]] = []

        for index, value in enumerate(values):

            target = abs(value) if absolute else value

            if target >= threshold:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "score": target,
                        "method": "threshold",
                    }
                )

        return {
            "method": "threshold",
            "threshold": threshold,
            "absolute": absolute,
            "anomalies": anomalies,
        }

    def get_threshold(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """Compatibility alias for threshold_value()."""

        return self.threshold_value(
            name,
            default,
        )

    def thresholds(self) -> dict[str, float]:
        """Return a copy of threshold configuration."""

        with self._lock:
            return dict(self._thresholds)

    def set_threshold(
        self,
        name: str,
        value: float,
    ) -> MetricAnomalyDetector:

        if not isinstance(name, str) or not name:
            raise ValueError(
                "threshold name must be a non-empty string."
            )

        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "threshold value must be numeric."
            ) from exc

        with self._lock:

            self._thresholds[name] = value
            self._touch()

        return self

    # ========================================================================
    # Detection Registry
    # ========================================================================

    def detector(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """Return registered detector."""

        return self._detectors.get(name, default)

    def detectors(self) -> dict[str, DetectorCallable]:
        """Return a copy of detector registry."""

        with self._lock:
            return dict(self._detectors)

    def register_detector(
        self,
        name: str,
        detector: DetectorCallable,
    ) -> MetricAnomalyDetector:

        if not isinstance(name, str) or not name:
            raise ValueError(
                "detector name must be a non-empty string."
            )

        if not callable(detector):
            raise TypeError(
                "detector must be callable."
            )

        with self._lock:

            self._detectors[name] = detector
            self._touch()

        return self

    def unregister_detector(
        self,
        name: str,
    ) -> MetricAnomalyDetector:
        """
        Unregister a custom detector.

        Built-in detectors are protected and cannot be removed.
        Missing custom detectors are treated as a no-op.
        """

        if not isinstance(name, str) or not name:
            raise ValueError(
                "detector name must be a non-empty string."
            )

        with self._lock:

            if name in self._builtin_detector_names():
                raise ValueError(
                    f"Built-in detector cannot be unregistered: {name!r}"
                )

            self._detectors.pop(
                name,
                None,
            )

            self._touch()

        return self

    def detector_names(self) -> list[str]:
        """Return registered detector names."""

        with self._lock:
            return list(self._detectors.keys())

    # ========================================================================
    # Runtime Statistics
    # ========================================================================

    @property
    def statistics(self) -> MetricStatistics:
        """Underlying statistics engine."""

        return self._statistics

    @property
    def detection_count(self) -> int:
        """Total successful detection executions."""

        return self._detection_count

    @property
    def anomaly_count(self) -> int:
        """Total anomalies detected."""

        return self._anomaly_count

    @property
    def false_positive(self) -> int:
        """Total false positives."""

        return self._false_positive

    @property
    def latency(self) -> float:
        """Average detection latency."""

        return self._latency

    @property
    def uptime(self) -> float:
        """Detector uptime."""

        return self._uptime

    # ========================================================================
    # Metadata
    # ========================================================================

    @property
    def created_at(self) -> datetime:
        """Creation timestamp."""

        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Last update timestamp."""

        return self._updated_at

    @property
    def version(self) -> str:
        """Detector version."""

        return self._version

    # ========================================================================
    # Detection API
    # ========================================================================

    def detect(
        self,
        values,
        method: str = "zscore",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generic anomaly detection entry point.
        """

        self._require_active()

        if not isinstance(method, str) or not method:
            raise ValueError(
                "method must be a non-empty string."
            )

        detector = self._detectors.get(method)

        if detector is None:
            raise KeyError(
                f"Unknown detector: {method}"
            )

        values = list(values)

        self.before_detect(
            values,
            method=method,
            **kwargs,
        )

        started = self._now()

        try:

            result = detector(
                values,
                **kwargs,
            )

            if not isinstance(result, dict):
                raise TypeError(
                    "Detector must return a dictionary."
                )

            anomalies = result.get("anomalies", [])

            if anomalies is None:
                anomalies = []

            elapsed = (
                self._now() - started
            ).total_seconds()

            with self._lock:

                self._detection_count += 1

                self._anomaly_count += len(anomalies)

                self._latency = self._update_average(
                    self._latency,
                    elapsed,
                    self._detection_count,
                )

                self._last_result = copy.deepcopy(result)

                self._history.append(
                    copy.deepcopy(result)
                )

                self._touch()

            self.after_detect(
                result=result,
                method=method,
            )

            return result

        except Exception:

            self.emit(
                "detection_error",
                method=method,
            )

            raise

    @staticmethod
    def _update_average(
        current: float,
        value: float,
        count: int,
    ) -> float:
        """Incrementally update arithmetic average."""

        if count <= 1:
            return float(value)

        return current + (
            (value - current) / count
        )

    def detect_one(
        self,
        value,
        method: str = "threshold",
        **kwargs,
    ):
        """Detect anomaly for a single value."""

        result = self.detect(
            [value],
            method=method,
            **kwargs,
        )

        anomalies = result.get(
            "anomalies",
            [],
        )

        return anomalies[0] if anomalies else None

    def detect_many(
        self,
        values: Iterable[Any],
        method: str = "zscore",
        **kwargs,
    ) -> dict[str, Any]:

        return self.detect(
            list(values),
            method=method,
            **kwargs,
        )

    def detect_batch(
        self,
        batches: Iterable[Iterable[Any]],
        method: str = "zscore",
        **kwargs,
    ) -> list[dict[str, Any]]:

        return [
            self.detect(
                batch,
                method=method,
                **kwargs,
            )
            for batch in batches
        ]

    # ========================================================================
    # Detection Algorithms
    # ========================================================================

    def zscore(
        self,
        values,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        """Classical Z-score anomaly detection."""

        values = list(values)

        if len(values) < 2:
            return {
                "method": "zscore",
                "anomalies": [],
            }

        stats = MetricStatistics(values)

        mean = stats.mean()
        std = stats.std()

        if std == 0:
            return {
                "method": "zscore",
                "mean": mean,
                "std": std,
                "threshold": threshold
                if threshold is not None
                else self._thresholds["zscore"],
                "anomalies": [],
            }

        if threshold is None:
            threshold = self._thresholds["zscore"]

        threshold = float(threshold)

        anomalies = []

        for index, value in enumerate(values):

            score = abs(
                (value - mean) / std
            )

            if score >= threshold:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "zscore": score,
                        "method": "zscore",
                    }
                )

        return {
            "method": "zscore",
            "mean": mean,
            "std": std,
            "threshold": threshold,
            "anomalies": anomalies,
        }

    def modified_zscore(
        self,
        values,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        """Modified Z-score using median absolute deviation."""

        values = list(values)

        if not values:
            return {
                "method": "modified_zscore",
                "anomalies": [],
            }

        stats = MetricStatistics(values)

        median = stats.median()

        deviations = [
            abs(value - median)
            for value in values
        ]

        mad = MetricStatistics(
            deviations
        ).median()

        if mad == 0:
            return {
                "method": "modified_zscore",
                "median": median,
                "mad": mad,
                "threshold": threshold
                if threshold is not None
                else self._thresholds["mad"],
                "anomalies": [],
            }

        if threshold is None:
            threshold = self._thresholds["mad"]

        threshold = float(threshold)

        anomalies = []

        for index, value in enumerate(values):

            score = (
                0.6745
                * (value - median)
                / mad
            )

            if abs(score) >= threshold:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "score": score,
                        "method": "modified_zscore",
                    }
                )

        return {
            "method": "modified_zscore",
            "median": median,
            "mad": mad,
            "threshold": threshold,
            "anomalies": anomalies,
        }

    def iqr(
        self,
        values,
        factor: float | None = None,
    ) -> dict[str, Any]:
        """IQR-based anomaly detection."""

        values = list(values)

        if not values:
            return {
                "method": "iqr",
                "anomalies": [],
            }

        stats = MetricStatistics(values)

        q1 = stats.percentile(25)
        q3 = stats.percentile(75)

        iqr = q3 - q1

        if factor is None:
            factor = self._thresholds["iqr"]

        factor = float(factor)

        lower = q1 - factor * iqr
        upper = q3 + factor * iqr

        anomalies = []

        for index, value in enumerate(values):

            if value < lower or value > upper:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "method": "iqr",
                    }
                )

        return {
            "method": "iqr",
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "factor": factor,
            "lower": lower,
            "upper": upper,
            "anomalies": anomalies,
        }

    def sigma(
        self,
        values,
        sigma: float | None = None,
    ) -> dict[str, Any]:
        """N-sigma anomaly detection."""

        values = list(values)

        if not values:
            return {
                "method": "sigma",
                "anomalies": [],
            }

        stats = MetricStatistics(values)

        mean = stats.mean()
        std = stats.std()

        if sigma is None:
            sigma = self._thresholds["sigma"]

        sigma = float(sigma)

        lower = mean - sigma * std
        upper = mean + sigma * std

        anomalies = []

        for index, value in enumerate(values):

            if value < lower or value > upper:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "method": "sigma",
                    }
                )

        return {
            "method": "sigma",
            "mean": mean,
            "std": std,
            "sigma": sigma,
            "lower": lower,
            "upper": upper,
            "anomalies": anomalies,
        }

    def moving_average(
        self,
        values,
        window: int = 5,
        threshold: float = 2.0,
    ) -> dict[str, Any]:
        """Moving-average deviation detection."""

        values = list(values)

        if window <= 0:
            raise ValueError(
                "window must be greater than zero."
            )

        if len(values) < window:
            return {
                "method": "moving_average",
                "window": window,
                "anomalies": [],
            }

        stats = MetricStatistics(values)

        averages = stats.moving_average(
            window
        )

        anomalies = []

        for i, average in enumerate(averages):

            index = i + window - 1

            value = values[index]

            deviation = abs(
                value - average
            )

            if deviation >= threshold:

                anomalies.append(
                    {
                        "index": index,
                        "value": value,
                        "average": average,
                        "deviation": deviation,
                        "threshold": threshold,
                        "method": "moving_average",
                    }
                )

        return {
            "method": "moving_average",
            "window": window,
            "threshold": threshold,
            "anomalies": anomalies,
        }

    def rolling(
        self,
        values,
        window: int = 10,
        detector: str = "zscore",
    ) -> dict[str, Any]:
        """
        Rolling-window anomaly detection.

        Only registered detectors are allowed.
        """

        values = list(values)

        if window <= 0:
            raise ValueError(
                "window must be greater than zero."
            )

        if window > len(values):
            return {
                "method": "rolling",
                "window": window,
                "detector": detector,
                "anomalies": [],
            }

        if detector == "rolling":
            raise ValueError(
                "rolling detector cannot recursively invoke itself."
            )

        detector_callable = self._detectors.get(detector)

        if detector_callable is None:
            raise ValueError(
                f"Unknown rolling detector: {detector}"
            )

        anomalies = []

        for start in range(
            len(values) - window + 1
        ):

            subset = values[
                start:start + window
            ]

            result = detector_callable(
                subset
            )

            for item in result.get(
                "anomalies",
                [],
            ):

                entry = dict(item)

                entry["index"] = (
                    entry.get("index", 0)
                    + start
                )

                anomalies.append(entry)

        return {
            "method": "rolling",
            "window": window,
            "detector": detector,
            "anomalies": anomalies,
        }

    def custom(
        self,
        values,
        detector: DetectorCallable,
        **kwargs,
    ) -> dict[str, Any]:
        """Execute a user-defined detector."""

        if not callable(detector):
            raise TypeError(
                "detector must be callable."
            )

        result = detector(
            values,
            **kwargs,
        )

        if not isinstance(result, dict):
            raise TypeError(
                "Custom detector must return a dictionary."
            )

        return result

    # ========================================================================
    # Rule Management
    # ========================================================================

    def register_rule(
        self,
        name: str,
        rule: RuleCallable,
        *,
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> MetricAnomalyDetector:

        if not isinstance(name, str) or not name:
            raise ValueError(
                "rule name must be a non-empty string."
            )

        if not callable(rule):
            raise TypeError(
                "rule must be callable."
            )

        with self._lock:

            self._rules[name] = {
                "name": name,
                "callable": rule,
                "enabled": bool(enabled),
                "metadata": dict(metadata or {}),
                "created_at": self._now(),
            }

            self._touch()

        return self

    def remove_rule(
        self,
        name: str,
    ) -> dict[str, Any] | None:

        with self._lock:

            removed = self._rules.pop(
                name,
                None,
            )

            self._touch()

            return removed

    def rule(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """Return registered rule entry."""

        return self._rules.get(
            name,
            default,
        )

    def rules(self) -> dict[str, dict[str, Any]]:
        """Return a shallow copy of rule registry."""

        with self._lock:
            return dict(self._rules)

    def contains_rule(
        self,
        name: str,
    ) -> bool:

        return name in self._rules

    def enable_rule(
        self,
        name: str,
    ) -> MetricAnomalyDetector:

        with self._lock:

            entry = self._rules.get(name)

            if entry is None:
                raise KeyError(
                    f"Unknown rule: {name}"
                )

            entry["enabled"] = True
            self._touch()

        return self

    def disable_rule(
        self,
        name: str,
    ) -> MetricAnomalyDetector:

        with self._lock:

            entry = self._rules.get(name)

            if entry is None:
                raise KeyError(
                    f"Unknown rule: {name}"
                )

            entry["enabled"] = False
            self._touch()

        return self

    def clear_rules(
        self,
    ) -> MetricAnomalyDetector:

        with self._lock:

            self._rules.clear()
            self._touch()

        return self

    def rule_count(self) -> int:
        """Return number of registered rules."""

        return len(self._rules)

    def rule_names(self) -> list[str]:
        """Return registered rule names."""

        return list(self._rules.keys())

    def execute_rule(
        self,
        name: str,
        values,
        **kwargs,
    ):
        """Execute a registered rule."""

        entry = self._rules.get(name)

        if entry is None:
            raise KeyError(
                f"Unknown rule: {name}"
            )

        self.before_rule(
            name,
            values=values,
        )

        if not entry["enabled"]:

            result = {
                "rule": name,
                "enabled": False,
                "anomalies": [],
            }

        else:

            result = entry["callable"](
                values,
                **kwargs,
            )

        self.after_rule(
            name,
            result=result,
        )

        return result

    # ========================================================================
    # Context
    # ========================================================================

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> MetricAnomalyDetector:

        with self._lock:

            self._context[key] = value
            self._touch()

        return self

    def get_context(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._context.get(
            key,
            default,
        )

    def context(self) -> dict[str, Any]:
        """Return a copy of runtime context."""

        with self._lock:
            return copy.deepcopy(
                self._context
            )

    def clear_context(
        self,
    ) -> MetricAnomalyDetector:

        with self._lock:

            self._context.clear()
            self._touch()

        return self

    # ========================================================================
    # Lifecycle
    # ========================================================================

    def enable(self) -> MetricAnomalyDetector:

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot enable a closed detector."
                )

            self._enabled = True
            self._touch()

        return self

    def disable(self) -> MetricAnomalyDetector:

        with self._lock:

            self._enabled = False
            self._touch()

        return self

    def freeze(self) -> MetricAnomalyDetector:

        with self._lock:

            self._frozen = True
            self._touch()

        return self

    def unfreeze(self) -> MetricAnomalyDetector:

        with self._lock:

            if self._closed:
                raise RuntimeError(
                    "Cannot unfreeze a closed detector."
                )

            self._frozen = False
            self._touch()

        return self

    def close(self) -> MetricAnomalyDetector:

        with self._lock:

            if self._closed:
                return self

            self._closed = True
            self._enabled = False
            self._touch()

        return self

    def reopen(self) -> MetricAnomalyDetector:

        with self._lock:

            self._closed = False
            self._enabled = True
            self._frozen = False
            self._touch()

        return self

    # ========================================================================
    # Runtime Operations
    # ========================================================================

    def reset(self) -> MetricAnomalyDetector:
        """
        Reset runtime statistics and detection history.

        Configuration, detectors, rules and lifecycle state are preserved.
        """

        with self._lock:

            self._history.clear()

            self._last_result = None

            self._detection_count = 0
            self._anomaly_count = 0
            self._false_positive = 0

            self._latency = 0.0
            self._uptime = 0.0

            self._statistics = MetricStatistics()

            self._touch()

        return self

    def clear(self) -> MetricAnomalyDetector:
        """
        Clear runtime state.

        Configuration, detectors and rules are preserved.
        """

        with self._lock:

            self.reset()

            self._events.clear()
            self._hooks.clear()
            self._context.clear()

            self._snapshot = None

            self._touch()

        return self

    # ========================================================================
    # Snapshot / Restore
    # ========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Create a deep runtime snapshot.

        Callables are intentionally excluded from the snapshot.
        Registry membership is preserved separately through detector/rule names.
        """

        with self._lock:

            snapshot = {
                "id": self._id,
                "name": self._name,
                "description": self._description,
                "version": self._version,
                "created_at": self._created_at,
                "updated_at": self._updated_at,

                "enabled": self._enabled,
                "frozen": self._frozen,
                "closed": self._closed,

                "thresholds": dict(
                    self._thresholds
                ),

                "history": copy.deepcopy(
                    self._history
                ),

                "last_result": copy.deepcopy(
                    self._last_result
                ),

                "context": copy.deepcopy(
                    self._context
                ),

                "detection_count": self._detection_count,
                "anomaly_count": self._anomaly_count,
                "false_positive": self._false_positive,
                "latency": self._latency,
                "uptime": self._uptime,
            }

            self._snapshot = copy.deepcopy(
                snapshot
            )

            return copy.deepcopy(
                snapshot
            )

    def restore(
        self,
        snapshot: dict[str, Any] | None = None,
    ) -> MetricAnomalyDetector:
        """Restore runtime state from a snapshot."""

        with self._lock:

            if snapshot is None:
                snapshot = self._snapshot

            if snapshot is None:
                raise ValueError(
                    "No snapshot available."
                )

            self._enabled = bool(
                snapshot.get(
                    "enabled",
                    True,
                )
            )

            self._frozen = bool(
                snapshot.get(
                    "frozen",
                    False,
                )
            )

            self._closed = bool(
                snapshot.get(
                    "closed",
                    False,
                )
            )

            restored_thresholds = snapshot.get(
                "thresholds",
                {},
            )

            self._thresholds = dict(
                self.DEFAULT_THRESHOLDS
            )

            self._thresholds.update(
                restored_thresholds
            )

            self._history = copy.deepcopy(
                snapshot.get(
                    "history",
                    [],
                )
            )

            self._last_result = copy.deepcopy(
                snapshot.get(
                    "last_result",
                    None,
                )
            )

            self._context = copy.deepcopy(
                snapshot.get(
                    "context",
                    {},
                )
            )

            self._detection_count = int(
                snapshot.get(
                    "detection_count",
                    0,
                )
            )

            self._anomaly_count = int(
                snapshot.get(
                    "anomaly_count",
                    0,
                )
            )

            self._false_positive = int(
                snapshot.get(
                    "false_positive",
                    0,
                )
            )

            self._latency = float(
                snapshot.get(
                    "latency",
                    0.0,
                )
            )

            self._uptime = float(
                snapshot.get(
                    "uptime",
                    0.0,
                )
            )

            self._touch()

        return self

    # ========================================================================
    # Copy Protocol
    # ========================================================================

    def clone(self) -> MetricAnomalyDetector:
        """
        Create an independent detector clone.

        Runtime synchronization primitives and bound built-in
        detector methods are recreated for the cloned instance.
        User callables are preserved by reference.
        """

        with self._lock:

            obj = self.__class__.__new__(
                self.__class__
            )

            # ------------------------------------------------------------
            # Scalar / immutable state
            # ------------------------------------------------------------

            obj._id = self._id
            obj._name = self._name
            obj._description = self._description

            obj._enabled = self._enabled
            obj._frozen = self._frozen
            obj._closed = self._closed

            obj._version = self._version

            obj._created_at = self._created_at
            obj._updated_at = self._updated_at

            obj._detection_count = self._detection_count
            obj._anomaly_count = self._anomaly_count
            obj._false_positive = self._false_positive

            obj._latency = self._latency
            obj._uptime = self._uptime

            # ------------------------------------------------------------
            # Deep-copyable runtime configuration/state
            # ------------------------------------------------------------

            obj._thresholds = copy.deepcopy(
                self._thresholds
            )

            obj._history = copy.deepcopy(
                self._history
            )

            obj._last_result = copy.deepcopy(
                self._last_result
            )

            obj._context = copy.deepcopy(
                self._context
            )

            obj._statistics = copy.deepcopy(
                self._statistics
            )

            obj._snapshot = copy.deepcopy(
                self._snapshot
            )

            obj._events = copy.deepcopy(
                self._events
            )

            # ------------------------------------------------------------
            # Rules
            #
            # Rule callables are intentionally preserved by reference.
            # Mutable metadata is independently copied.
            # ------------------------------------------------------------

            obj._rules = {}

            for name, entry in self._rules.items():

                cloned_entry = dict(entry)

                if "metadata" in cloned_entry:
                    cloned_entry["metadata"] = copy.deepcopy(
                        cloned_entry["metadata"]
                    )

                obj._rules[name] = cloned_entry

            # ------------------------------------------------------------
            # Hooks
            #
            # Callback objects are intentionally preserved by reference.
            # The callback lists themselves are independent.
            # ------------------------------------------------------------

            obj._hooks = {
                event: list(callbacks)
                for event, callbacks in self._hooks.items()
            }

            # ------------------------------------------------------------
            # Lock
            # ------------------------------------------------------------

            obj._lock = threading.RLock()

            # ------------------------------------------------------------
            # Rebuild detector registry
            #
            # Built-in detectors MUST be rebound to the cloned instance.
            # Custom detector callables are preserved by reference.
            # ------------------------------------------------------------

            obj._detectors = {}

            builtin_names = self._builtin_detector_names()

            for name in builtin_names:

                detector = getattr(
                    obj,
                    name,
                    None,
                )

                if detector is not None:
                    obj._detectors[name] = detector

            for name, detector in self._detectors.items():

                if name not in builtin_names:
                    obj._detectors[name] = detector

            return obj


    def copy(self) -> MetricAnomalyDetector:
        """
        Return an independent detector copy.
        """
        return self.clone()


    def __copy__(self) -> MetricAnomalyDetector:
        return self.clone()


    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> MetricAnomalyDetector:
        """
        Create an independent deep copy without copying the thread lock.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():

            if key == "_lock":
                setattr(
                    obj,
                    key,
                    threading.RLock(),
                )
                continue

            setattr(
                obj,
                key,
                copy.deepcopy(
                    value,
                    memo,
                ),
            )

        return obj
    # ========================================================================
    # Statistics & Diagnostics
    # ========================================================================

    @classmethod
    def _builtin_detector_names(cls) -> frozenset[str]:
        """Return names of built-in detectors."""
        return cls.BUILTIN_DETECTORS

    def _custom_detector_names(self) -> list[str]:
        """
        Return names of user-registered detectors.

        Built-in detectors are intentionally excluded.
        """

        builtin = self._builtin_detector_names()

        return [
            name
            for name in self._detectors
            if name not in builtin
        ]

    def _custom_detector_count(self) -> int:
        """
        Return the number of registered custom detectors.
        """

        builtin = self._builtin_detector_names()

        return sum(
            1
            for name in self._detectors
            if name not in builtin
        )

    def summary(self) -> dict[str, Any]:
        """Return compact runtime summary."""

        with self._lock:

            return {
                "id": self._id,
                "name": self._name,

                "enabled": self._enabled,
                "frozen": self._frozen,
                "closed": self._closed,
                "active": self.active,

                "detection_count":
                    self._detection_count,

                "anomaly_count":
                    self._anomaly_count,

                "false_positive":
                    self._false_positive,

                "rule_count":
                    len(self._rules),

                # Custom detectors only.
                "detector_count":
                    self._custom_detector_count(),

                "history_size":
                    len(self._history),

                "latency":
                    self._latency,

                "uptime":
                    self._uptime,

                "version":
                    self._version,

                "updated_at":
                    self._updated_at,
            }

    def report(self) -> dict[str, Any]:
        """
        Return a complete runtime report.

        Unlike ``summary()``, this report exposes the actual detector
        registry, including built-in and custom detectors.
        """

        with self._lock:

            builtin_names = self._builtin_detector_names()

            builtin_detectors = [
                name
                for name in self._detectors
                if name in builtin_names
            ]

            custom_detectors = [
                name
                for name in self._detectors
                if name not in builtin_names
            ]

            return {
                # ------------------------------------------------------------
                # Summary
                # ------------------------------------------------------------

                "summary":
                    self.summary(),

                # ------------------------------------------------------------
                # Configuration
                # ------------------------------------------------------------

                "thresholds":
                    dict(self._thresholds),

                # ------------------------------------------------------------
                # Statistics
                # ------------------------------------------------------------

                "statistics": (
                    self._statistics.describe()
                    if self._statistics
                    else {}
                ),

                # ------------------------------------------------------------
                # Rules
                # ------------------------------------------------------------

                "rules":
                    list(self._rules.keys()),

                # ------------------------------------------------------------
                # Detector registry
                # ------------------------------------------------------------

                "detectors":
                    list(self._detectors.keys()),

                "builtin_detectors":
                    builtin_detectors,

                "custom_detectors":
                    custom_detectors,

                # ------------------------------------------------------------
                # Runtime result
                # ------------------------------------------------------------

                "last_result":
                    copy.deepcopy(
                        self._last_result
                    ),
            }

    def health(self) -> dict[str, Any]:
        """
        Return runtime health information.

        ``detector_count`` counts only custom detectors.
        """

        with self._lock:

            if self._closed:
                state = "closed"

            elif self._frozen:
                state = "frozen"

            elif not self._enabled:
                state = "disabled"

            else:
                state = "healthy"

            builtin_names = self._builtin_detector_names()

            builtin_count = sum(
                name in builtin_names
                for name in self._detectors
            )

            custom_count = (
                len(self._detectors)
                - builtin_count
            )

            return {
                "state": state,
                "healthy": state == "healthy",
                "active": self.active,

                "enabled": self._enabled,
                "disabled": self.disabled,
                "frozen": self._frozen,
                "closed": self._closed,

                "rule_count": len(self._rules),

                "detector_count": custom_count,
                "builtin_detector_count": builtin_count,
                "total_detector_count": len(self._detectors),
            }

    def status(self) -> dict[str, Any]:
        """
        Return current runtime lifecycle state.
        """

        with self._lock:

            return {
                "enabled":
                    self._enabled,

                "disabled":
                    not self._enabled,

                "frozen":
                    self._frozen,

                "closed":
                    self._closed,

                "active":
                    self.active,
            }

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize detector configuration and runtime metadata.

        Callables are represented by names rather than serialized.
        """

        with self._lock:

            return {
                "id": self._id,
                "name": self._name,
                "description": self._description,

                "enabled": self._enabled,
                "frozen": self._frozen,
                "closed": self._closed,

                "thresholds":
                    dict(self._thresholds),

                "detectors":
                    list(self._detectors.keys()),

                "rules":
                    list(self._rules.keys()),

                "detection_count":
                    self._detection_count,

                "anomaly_count":
                    self._anomaly_count,

                "false_positive":
                    self._false_positive,

                "latency":
                    self._latency,

                "uptime":
                    self._uptime,

                "history_size":
                    len(self._history),

                "last_result":
                    copy.deepcopy(
                        self._last_result
                    ),

                "created_at":
                    self._created_at.isoformat(),

                "updated_at":
                    self._updated_at.isoformat(),

                "version":
                    self._version,
            }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> MetricAnomalyDetector:

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary."
            )

        detector = cls(
            name=data.get(
                "name",
                "MetricAnomalyDetector",
            ),
            description=data.get(
                "description",
                "",
            ),
        )

        with detector._lock:

            detector._id = data.get(
                "id",
                detector._id,
            )

            detector._enabled = bool(
                data.get(
                    "enabled",
                    True,
                )
            )

            detector._frozen = bool(
                data.get(
                    "frozen",
                    False,
                )
            )

            detector._closed = bool(
                data.get(
                    "closed",
                    False,
                )
            )

            detector._thresholds = dict(
                cls.DEFAULT_THRESHOLDS
            )

            detector._thresholds.update(
                data.get(
                    "thresholds",
                    {},
                )
            )

            detector._detection_count = int(
                data.get(
                    "detection_count",
                    0,
                )
            )

            detector._anomaly_count = int(
                data.get(
                    "anomaly_count",
                    0,
                )
            )

            detector._false_positive = int(
                data.get(
                    "false_positive",
                    0,
                )
            )

            detector._latency = float(
                data.get(
                    "latency",
                    0.0,
                )
            )

            detector._uptime = float(
                data.get(
                    "uptime",
                    0.0,
                )
            )

            detector._last_result = copy.deepcopy(
                data.get(
                    "last_result",
                    None,
                )
            )

            detector._version = data.get(
                "version",
                cls.VERSION,
            )

            created_at = data.get(
                "created_at"
            )

            if created_at:
                try:
                    detector._created_at = (
                        datetime.fromisoformat(
                            created_at
                        )
                    )
                except (TypeError, ValueError):
                    pass

            updated_at = data.get(
                "updated_at"
            )

            if updated_at:
                try:
                    detector._updated_at = (
                        datetime.fromisoformat(
                            updated_at
                        )
                    )
                except (TypeError, ValueError):
                    pass

        return detector

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """Serialize detector to JSON."""

        kwargs.setdefault(
            "indent",
            4,
        )

        kwargs.setdefault(
            "default",
            str,
        )

        return json.dumps(
            self.to_dict(),
            **kwargs,
        )

    @classmethod
    def from_json(
        cls,
        data: str,
    ) -> MetricAnomalyDetector:

        if not isinstance(data, str):
            raise TypeError(
                "data must be a JSON string."
            )

        return cls.from_dict(
            json.loads(data)
        )

    def serialize(self) -> str:
        """Generic serialization."""

        return self.to_json()

    @classmethod
    def deserialize(
        cls,
        data: str,
    ) -> MetricAnomalyDetector:

        return cls.from_json(data)

    # ========================================================================
    # Events
    # ========================================================================

    def before_detect(
        self,
        values,
        method: str = "",
        **kwargs,
    ):
        """Emit before-detection event."""

        return self.emit(
            "before_detect",
            values=values,
            method=method,
            **kwargs,
        )

    def after_detect(
        self,
        result=None,
        **kwargs,
    ):
        """Emit after-detection event."""

        return self.emit(
            "after_detect",
            result=result,
            **kwargs,
        )

    def before_rule(
        self,
        name: str,
        values=None,
        **kwargs,
    ):
        """Emit before-rule event."""

        return self.emit(
            "before_rule",
            rule=name,
            values=values,
            **kwargs,
        )

    def after_rule(
        self,
        name: str,
        result=None,
        **kwargs,
    ):
        """Emit after-rule event."""

        return self.emit(
            "after_rule",
            rule=name,
            result=result,
            **kwargs,
        )

    # ========================================================================
    # Hook Management
    # ========================================================================

    def add_hook(
        self,
        event: str,
        callback: HookCallable,
    ) -> MetricAnomalyDetector:

        if not isinstance(event, str) or not event:
            raise ValueError(
                "event must be a non-empty string."
            )

        if not callable(callback):
            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            self._hooks.setdefault(
                event,
                [],
            ).append(callback)

            self._touch()

        return self

    def remove_hook(
        self,
        event: str,
        callback: HookCallable | None = None,
    ) -> MetricAnomalyDetector:

        with self._lock:

            if event not in self._hooks:
                return self

            if callback is None:

                self._hooks.pop(
                    event,
                    None,
                )

                self._touch()

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

            self._touch()

        return self

    def emit(
        self,
        event: str,
        **payload,
    ) -> dict[str, Any]:
        """Emit an event and execute registered hooks."""

        event_data = {
            "event": event,
            "payload": payload,
            "timestamp": self._now(),
        }

        with self._lock:

            self._events.append(
                event_data
            )

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
                    event_data,
                )

            except Exception:
                # Hook failures must never break
                # the anomaly detection pipeline.
                continue

        return event_data

    def subscribe(
        self,
        event: str,
        callback: HookCallable,
    ) -> MetricAnomalyDetector:

        return self.add_hook(
            event,
            callback,
        )

    def unsubscribe(
        self,
        event: str,
        callback: HookCallable | None = None,
    ) -> MetricAnomalyDetector:

        return self.remove_hook(
            event,
            callback,
        )

    def events(self) -> list[dict[str, Any]]:
        """Return a copy of emitted events."""

        with self._lock:
            return copy.deepcopy(
                self._events
            )

    def clear_events(
        self,
    ) -> MetricAnomalyDetector:

        with self._lock:

            self._events.clear()
            self._touch()

        return self

    # ========================================================================
    # Python Protocols
    # ========================================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"enabled={self._enabled}, "
            f"frozen={self._frozen}, "
            f"closed={self._closed}, "
            f"rules={len(self._rules)}, "
            f"detectors={len(self._detectors)}, "
            f"detections={self._detection_count})"
        )

    def __str__(self) -> str:

        return (
            f"{self._name} "
            f"[active={self.active}, "
            f"rules={len(self._rules)}, "
            f"detectors={len(self._detectors)}]"
        )

    def __len__(self) -> int:
        """Number of registered rules."""

        return len(self._rules)

    def __iter__(self):
        """Iterate over registered rules."""

        return iter(self._rules.items())

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._rules

    def __call__(
        self,
        values,
        method: str = "zscore",
        **kwargs,
    ):

        return self.detect(
            values,
            method=method,
            **kwargs,
        )