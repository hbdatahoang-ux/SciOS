"""
SciOS-NG Runtime Metrics Analysis

Anomaly Detection Engine

SciOS/scios/runtime/observability/metrics/analysis/anomaly.py
"""

from __future__ import annotations

import threading
import uuid

from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics
import json

# ==========================================================
# MetricAnomalyDetector
# ==========================================================

class MetricAnomalyDetector:
    """
    Runtime Metrics Anomaly Detection Engine.

    Foundation
    ----------
    - Threshold Configuration
    - Detection Registry
    - Runtime State
    - Metadata
    - Statistics Engine
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        name: str = "MetricAnomalyDetector",
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

        # --------------------------------------------------
        # Threshold Configuration
        # --------------------------------------------------

        self._thresholds = {

            "warning": 0.80,

            "critical": 0.95,

            "zscore": 3.0,

            "mad": 3.5,

            "iqr": 1.5,

            "sigma": 3.0,

        }

        # --------------------------------------------------
        # Detection Registry
        # --------------------------------------------------

        self._detectors: dict[
            str,
            Callable[..., Any]
        ] = {}

        self._rules: dict[
            str,
            Callable[..., Any]
        ] = {}

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

        # --------------------------------------------------
        # Statistics Engine
        # --------------------------------------------------

        self._statistics = MetricStatistics()

        # Runtime counters

        self._detection_count = 0

        self._anomaly_count = 0

        self._false_positive = 0

        self._latency = 0.0

        self._uptime = 0.0

        # --------------------------------------------------
        # Internal Components
        # --------------------------------------------------

        self._hooks: dict[
            str,
            list[Callable]
        ] = {}

        self._events: list[dict] = []

        self._snapshot = None

        self._context: dict[str, Any] = {}

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
    def frozen(self):

        return self._frozen

    @property
    def closed(self):

        return self._closed

    @property
    def active(self):

        return (

            self._enabled
            and
            not self._closed
            and
            not self._frozen

        )

    # ======================================================
    # Threshold Configuration
    # ======================================================

    def threshold(
        self,
        name: str,
        default=None,
    ):

        return self._thresholds.get(
            name,
            default,
        )

    def thresholds(self):

        return dict(
            self._thresholds
        )

    def set_threshold(
        self,
        name: str,
        value: float,
    ):

        with self._lock:

            self._thresholds[name] = float(
                value
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Detection Registry
    # ======================================================

    def detector(
        self,
        name: str,
    ):

        return self._detectors.get(
            name
        )

    def detectors(self):

        return dict(
            self._detectors
        )

    def register_detector(
        self,
        name: str,
        detector: Callable,
    ):

        with self._lock:

            self._detectors[name] = detector

            self._updated_at = datetime.utcnow()

        return self

    def unregister_detector(
        self,
        name: str,
    ):

        with self._lock:

            self._detectors.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Rules
    # ======================================================

    def rule(
        self,
        name: str,
    ):

        return self._rules.get(
            name
        )

    def rules(self):

        return dict(
            self._rules
        )

    def register_rule(
        self,
        name: str,
        rule: Callable,
    ):

        self._rules[name] = rule

        return self

    # ======================================================
    # Runtime Statistics
    # ======================================================

    @property
    def detection_count(self):

        return self._detection_count

    @property
    def anomaly_count(self):

        return self._anomaly_count

    @property
    def statistics(self):

        return self._statistics

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
    # Part 2. Detection API
    # ======================================================

    def detect(
        self,
        values,
        method: str = "zscore",
        **kwargs,
    ):
        """
        Generic anomaly detection entry point.
        """

        if not self.active:
            raise RuntimeError(
                "MetricAnomalyDetector is not active."
            )

        detector = self._detectors.get(method)

        if detector is None:

            raise KeyError(
                f"Unknown detector: {method}"
            )

        result = detector(
            values,
            **kwargs,
        )

        self._detection_count += 1

        anomalies = result.get(
            "anomalies",
            [],
        )

        self._anomaly_count += len(
            anomalies
        )

        self._last_result = result

        self._history.append(result)

        self._updated_at = datetime.utcnow()

        return result

    def detect_one(
        self,
        value,
        method: str = "threshold",
        **kwargs,
    ):
        """
        Detect anomaly for a single value.
        """

        result = self.detect(
            [value],
            method=method,
            **kwargs,
        )

        anomalies = result.get(
            "anomalies",
            [],
        )

        return (

            anomalies[0]

            if anomalies

            else None

        )

    def detect_many(
        self,
        values,
        method: str = "zscore",
        **kwargs,
    ):
        """
        Detect anomalies from iterable values.
        """

        return self.detect(
            list(values),
            method=method,
            **kwargs,
        )

    def detect_batch(
        self,
        batches,
        method: str = "zscore",
        **kwargs,
    ):
        """
        Detect anomalies for multiple batches.
        """

        results = []

        for batch in batches:

            results.append(

                self.detect(
                    batch,
                    method=method,
                    **kwargs,
                )

            )

        return results
    # ======================================================
    # Part 3. Detection Algorithms
    # ======================================================

    def threshold(
        self,
        values,
        threshold: float | None = None,
        *,
        absolute: bool = False,
    ):
        """
        Threshold-based anomaly detection.
        """

        if threshold is None:

            threshold = self.threshold(
                "warning"
            )

        anomalies = []

        for index, value in enumerate(values):

            target = abs(value) if absolute else value

            if target >= threshold:

                anomalies.append({

                    "index": index,

                    "value": value,

                    "score": target,

                    "method": "threshold",

                })

        return {

            "method": "threshold",

            "threshold": threshold,

            "anomalies": anomalies,

        }

    def zscore(
        self,
        values,
        threshold: float | None = None,
    ):
        """
        Classical Z-score detection.
        """

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

                "anomalies": [],

            }

        if threshold is None:

            threshold = self.threshold(
                "zscore"
            )

        anomalies = []

        for index, value in enumerate(values):

            score = abs(
                (value - mean) / std
            )

            if score >= threshold:

                anomalies.append({

                    "index": index,

                    "value": value,

                    "zscore": score,

                    "method": "zscore",

                })

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
    ):
        """
        Modified Z-score using MAD.
        """

        values = list(values)

        if not values:

            return {

                "method": "modified_zscore",

                "anomalies": [],

            }

        stats = MetricStatistics(values)

        median = stats.median()

        deviations = [

            abs(v - median)

            for v in values

        ]

        mad = MetricStatistics(
            deviations
        ).median()

        if mad == 0:

            return {

                "method": "modified_zscore",

                "anomalies": [],

            }

        if threshold is None:

            threshold = self.threshold(
                "mad"
            )

        anomalies = []

        for index, value in enumerate(values):

            score = (

                0.6745

                * (value - median)

                / mad

            )

            if abs(score) >= threshold:

                anomalies.append({

                    "index": index,

                    "value": value,

                    "score": score,

                    "method": "modified_zscore",

                })

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
    ):
        """
        IQR-based anomaly detection.
        """

        values = list(values)

        stats = MetricStatistics(values)

        q1 = stats.percentile(25)

        q3 = stats.percentile(75)

        iqr = q3 - q1

        if factor is None:

            factor = self.threshold(
                "iqr"
            )

        lower = q1 - factor * iqr

        upper = q3 + factor * iqr

        anomalies = []

        for index, value in enumerate(values):

            if value < lower or value > upper:

                anomalies.append({

                    "index": index,

                    "value": value,

                    "method": "iqr",

                })

        return {

            "method": "iqr",

            "lower": lower,

            "upper": upper,

            "anomalies": anomalies,

        }

    def sigma(
        self,
        values,
        sigma: float | None = None,
    ):
        """
        N-sigma anomaly detection.
        """

        values = list(values)

        stats = MetricStatistics(values)

        mean = stats.mean()

        std = stats.std()

        if sigma is None:

            sigma = self.threshold(
                "sigma"
            )

        lower = mean - sigma * std

        upper = mean + sigma * std

        anomalies = []

        for index, value in enumerate(values):

            if value < lower or value > upper:

                anomalies.append({

                    "index": index,

                    "value": value,

                    "method": "sigma",

                })

        return {

            "method": "sigma",

            "lower": lower,

            "upper": upper,

            "anomalies": anomalies,

        }

    def moving_average(
        self,
        values,
        window: int = 5,
        threshold: float = 2.0,
    ):
        """
        Moving-average deviation detection.
        """

        values = list(values)

        if len(values) <= window:

            return {

                "method": "moving_average",

                "anomalies": [],

            }

        stats = MetricStatistics(values)

        averages = stats.moving_average(
            window
        )

        anomalies = []

        for i, avg in enumerate(averages):

            value = values[
                i + window - 1
            ]

            if abs(value - avg) >= threshold:

                anomalies.append({

                    "index": i + window - 1,

                    "value": value,

                    "average": avg,

                    "method": "moving_average",

                })

        return {

            "method": "moving_average",

            "window": window,

            "anomalies": anomalies,

        }

    def rolling(
        self,
        values,
        window: int = 10,
        detector: str = "zscore",
    ):
        """
        Rolling-window anomaly detection.
        """

        values = list(values)

        if len(values) < window:

            return {

                "method": "rolling",

                "anomalies": [],

            }

        anomalies = []

        for start in range(
            len(values) - window + 1
        ):

            subset = values[
                start:start + window
            ]

            result = getattr(
                self,
                detector,
            )(subset)

            for item in result.get(
                "anomalies",
                [],
            ):

                entry = dict(item)

                entry["index"] += start

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
        detector,
        **kwargs,
    ):
        """
        Execute user-defined detector.
        """

        if not callable(detector):

            raise TypeError(
                "detector must be callable."
            )

        return detector(
            values,
            **kwargs,
        )
    # ======================================================
    # Part 4. Rule Management
    # ======================================================

    def register_rule(
        self,
        name: str,
        rule: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a custom anomaly detection rule.
        """

        if not callable(rule):

            raise TypeError(
                "rule must be callable."
            )

        with self._lock:

            self._rules[name] = {

                "name": name,

                "callable": rule,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._updated_at = datetime.utcnow()

        return self

    def remove_rule(
        self,
        name: str,
    ):
        """
        Remove a registered rule.
        """

        with self._lock:

            removed = self._rules.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return removed

    def rule(
        self,
        name: str,
        default=None,
    ):
        """
        Get a registered rule.
        """

        return self._rules.get(
            name,
            default,
        )

    def rules(
        self,
    ):
        """
        Return all registered rules.
        """

        return dict(
            self._rules
        )

    def contains_rule(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a rule exists.
        """

        return name in self._rules

    def enable_rule(
        self,
        name: str,
    ):
        """
        Enable a rule.
        """

        rule = self._rules.get(
            name
        )

        if rule:

            rule["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_rule(
        self,
        name: str,
    ):
        """
        Disable a rule.
        """

        rule = self._rules.get(
            name
        )

        if rule:

            rule["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def clear_rules(
        self,
    ):
        """
        Remove all registered rules.
        """

        with self._lock:

            self._rules.clear()

            self._updated_at = datetime.utcnow()

        return self

    def rule_count(
        self,
    ) -> int:
        """
        Number of registered rules.
        """

        return len(
            self._rules
        )

    def rule_names(
        self,
    ):
        """
        Return all rule names.
        """

        return list(
            self._rules.keys()
        )

    def execute_rule(
        self,
        name: str,
        values,
        **kwargs,
    ):
        """
        Execute a registered rule.
        """

        entry = self._rules.get(
            name
        )

        if entry is None:

            raise KeyError(
                f"Unknown rule: {name}"
            )

        if not entry["enabled"]:

            return {

                "rule": name,

                "enabled": False,

                "anomalies": [],

            }

        return entry["callable"](
            values,
            **kwargs,
        )
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(self):
        """
        Enable anomaly detector.
        """

        with self._lock:

            self._enabled = True
            self._updated_at = datetime.utcnow()

        return self

    def disable(self):
        """
        Disable anomaly detector.
        """

        with self._lock:

            self._enabled = False
            self._updated_at = datetime.utcnow()

        return self

    def freeze(self):
        """
        Freeze anomaly detector.
        """

        with self._lock:

            self._frozen = True
            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(self):
        """
        Resume anomaly detector.
        """

        with self._lock:

            self._frozen = False
            self._updated_at = datetime.utcnow()

        return self

    def close(self):
        """
        Close anomaly detector.
        """

        with self._lock:

            if self._closed:
                return self

            self._closed = True
            self._enabled = False

            self._updated_at = datetime.utcnow()

        return self

    def reopen(self):
        """
        Reopen anomaly detector.
        """

        with self._lock:

            self._closed = False
            self._enabled = True
            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Lifecycle Properties
    # ======================================================

    @property
    def disabled(self):
        """
        Whether the detector is disabled.
        """

        return not self._enabled

    @property
    def active(self):
        """
        Whether the detector is active.
        """

        return (
            self._enabled
            and not self._frozen
            and not self._closed
        )
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(self):
        """
        Reset runtime statistics while preserving
        detector configuration, thresholds and rules.
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

            self._updated_at = datetime.utcnow()

        return self

    def clear(self):
        """
        Clear runtime state.

        Rules and registered detectors are preserved.
        """

        with self._lock:

            self.reset()

            self._events.clear()

            self._hooks.clear()

            self._context.clear()

            self._snapshot = None

            self._updated_at = datetime.utcnow()

        return self

    def snapshot(self):
        """
        Create runtime snapshot.
        """

        with self._lock:

            self._snapshot = {

                # Runtime

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                # Configuration

                "thresholds": dict(
                    self._thresholds
                ),

                # Runtime Data

                "history": list(
                    self._history
                ),

                "last_result":
                    copy.deepcopy(
                        self._last_result
                    ),

                "context":
                    copy.deepcopy(
                        self._context
                    ),

                # Statistics

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

                "updated_at":
                    self._updated_at,

            }

            return copy.deepcopy(
                self._snapshot
            )

    def restore(
        self,
        snapshot: dict | None = None,
    ):
        """
        Restore runtime snapshot.
        """

        with self._lock:

            if snapshot is None:

                snapshot = self._snapshot

            if snapshot is None:

                raise ValueError(
                    "No snapshot available."
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

            self._thresholds = dict(

                snapshot.get(
                    "thresholds",
                    {},
                )

            )

            self._history = list(

                snapshot.get(
                    "history",
                    [],
                )

            )

            self._last_result = copy.deepcopy(

                snapshot.get(
                    "last_result",
                )

            )

            self._context = copy.deepcopy(

                snapshot.get(
                    "context",
                    {},
                )

            )

            self._detection_count = snapshot.get(
                "detection_count",
                0,
            )

            self._anomaly_count = snapshot.get(
                "anomaly_count",
                0,
            )

            self._false_positive = snapshot.get(
                "false_positive",
                0,
            )

            self._latency = snapshot.get(
                "latency",
                0.0,
            )

            self._uptime = snapshot.get(
                "uptime",
                0.0,
            )

            self._updated_at = datetime.utcnow()

        return self

    def clone(self):
        """
        Deep clone detector.
        """

        return copy.deepcopy(
            self
        )

    def copy(self):
        """
        Shallow copy detector.
        """

        return copy.copy(
            self
        )
    # ======================================================
    # Part 7. Statistics & Diagnostics
    # ======================================================

    def summary(self) -> dict:
        """
        Return runtime summary.
        """

        return {

            "id": self._id,

            "name": self._name,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "active": self.active,

            "detection_count": self._detection_count,

            "anomaly_count": self._anomaly_count,

            "false_positive": self._false_positive,

            "rule_count": len(self._rules),

            "detector_count": len(self._detectors),

            "history_size": len(self._history),

            "latency": self._latency,

            "uptime": self._uptime,

            "version": self._version,

            "updated_at": self._updated_at,

        }

    def report(self) -> dict:
        """
        Return complete runtime report.
        """

        return {

            "summary": self.summary(),

            "thresholds": dict(
                self._thresholds
            ),

            "statistics": (
                self._statistics.describe()
                if self._statistics
                else {}
            ),

            "rules": list(
                self._rules.keys()
            ),

            "detectors": list(
                self._detectors.keys()
            ),

            "last_result": self._last_result,

        }

    def health(self) -> dict:
        """
        Runtime health information.
        """

        if self._closed:

            state = "closed"

        elif self._frozen:

            state = "frozen"

        elif not self._enabled:

            state = "disabled"

        else:

            state = "healthy"

        return {

            "state": state,

            "healthy": state == "healthy",

            "active": self.active,

            "enabled": self._enabled,

            "rule_count": len(
                self._rules
            ),

            "detector_count": len(
                self._detectors
            ),

        }

    def status(self) -> dict:
        """
        Runtime status.
        """

        return {

            "enabled": self._enabled,

            "disabled": self.disabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "active": self.active,

        }

    # ======================================================
    # Runtime Metrics
    # ======================================================

    @property
    def detection_count(self) -> int:
        """
        Total detection executions.
        """

        return self._detection_count

    @property
    def anomaly_count(self) -> int:
        """
        Total detected anomalies.
        """

        return self._anomaly_count

    @property
    def false_positive(self) -> int:
        """
        Total false positives.
        """

        return self._false_positive

    @property
    def uptime(self) -> float:
        """
        Detector uptime.
        """

        return self._uptime

    @property
    def latency(self) -> float:
        """
        Average detection latency.
        """

        return self._latency
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(self) -> dict:
        """
        Serialize detector to dictionary.
        """

        return {

            # Identity

            "id": self._id,

            "name": self._name,

            "description": self._description,

            # Runtime

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            # Configuration

            "thresholds": dict(
                self._thresholds
            ),

            "rules": list(
                self._rules.keys()
            ),

            "detectors": list(
                self._detectors.keys()
            ),

            # Statistics

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

            # Runtime

            "history_size":
                len(self._history),

            "last_result":
                self._last_result,

            # Metadata

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
        data: dict,
    ):
        """
        Restore detector from dictionary.
        """

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

        detector._enabled = data.get(
            "enabled",
            True,
        )

        detector._frozen = data.get(
            "frozen",
            False,
        )

        detector._closed = data.get(
            "closed",
            False,
        )

        detector._thresholds.update(

            data.get(
                "thresholds",
                {},
            )

        )

        detector._detection_count = data.get(
            "detection_count",
            0,
        )

        detector._anomaly_count = data.get(
            "anomaly_count",
            0,
        )

        detector._false_positive = data.get(
            "false_positive",
            0,
        )

        detector._latency = data.get(
            "latency",
            0.0,
        )

        detector._uptime = data.get(
            "uptime",
            0.0,
        )

        return detector

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize detector to JSON.
        """

        kwargs.setdefault(
            "indent",
            4,
        )

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
        Restore detector from JSON.
        """

        return cls.from_dict(

            json.loads(data)

        )

    def serialize(
        self,
    ) -> str:
        """
        Generic serialization.
        """

        return self.to_json()

    @classmethod
    def deserialize(
        cls,
        data: str,
    ):
        """
        Generic deserialization.
        """

        return cls.from_json(
            data
        )
    # ======================================================
    # Part 9. Events & Hooks
    # ======================================================

    # ------------------------------------------------------
    # Built-in Events
    # ------------------------------------------------------

    def before_detect(
        self,
        values,
        method: str = "",
        **kwargs,
    ):
        """
        Emit before detection event.
        """

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
        """
        Emit after detection event.
        """

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
        """
        Emit before rule event.
        """

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
        """
        Emit after rule event.
        """

        return self.emit(

            "after_rule",

            rule=name,

            result=result,

            **kwargs,

        )

    # ------------------------------------------------------
    # Hook Management
    # ------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Register event hook.
        """

        if not callable(callback):

            raise TypeError(
                "callback must be callable."
            )

        with self._lock:

            self._hooks.setdefault(
                event,
                [],
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
        Remove hook.
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

    # ------------------------------------------------------
    # Event Dispatcher
    # ------------------------------------------------------

    def emit(
        self,
        event: str,
        **payload,
    ):
        """
        Emit an event.
        """

        event_data = {

            "event": event,

            "payload": payload,

            "timestamp": datetime.utcnow(),

        }

        self._events.append(
            event_data
        )

        for callback in self._hooks.get(
            event,
            [],
        ):

            try:

                callback(
                    self,
                    event_data,
                )

            except Exception:

                # Never allow hook failures
                # to interrupt runtime.

                continue

        return event_data

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

    def unsubscribe(
        self,
        event: str,
        callback: Callable | None = None,
    ):
        """
        Alias of remove_hook().
        """

        return self.remove_hook(
            event,
            callback,
        )
    # ======================================================
    # Part 10. Python Protocols
    # ======================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (

            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"name={self._name!r}, "
            f"enabled={self._enabled}, "
            f"rules={len(self._rules)}, "
            f"detectors={len(self._detectors)}, "
            f"detections={self._detection_count})"

        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "
            f"[active={self.active}, "
            f"rules={len(self._rules)}, "
            f"detectors={len(self._detectors)}]"

        )

    def __len__(self) -> int:
        """
        Number of registered rules.
        """

        return len(self._rules)

    def __iter__(self):
        """
        Iterate over registered rules.
        """

        return iter(self._rules.items())

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Membership test.
        """

        return name in self._rules

    def __call__(
        self,
        values,
        method: str = "zscore",
        **kwargs,
    ):
        """
        Callable detector.
        """

        return self.detect(
            values,
            method=method,
            **kwargs,
        )

    def __copy__(self):
        """
        Shallow copy protocol.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        obj.__dict__.update(
            self.__dict__.copy()
        )

        return obj

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy protocol.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():

            setattr(

                obj,

                key,

                copy.deepcopy(
                    value,
                    memo,
                ),

            )

        return obj                