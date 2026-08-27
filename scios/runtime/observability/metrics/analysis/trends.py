"""
SciOS-NG Runtime Metrics Analysis

Trend Analysis Engine

SciOS/scios/runtime/observability/metrics/analysis/trends.py
"""

from __future__ import annotations

import threading
import time
import uuid

from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics


# ==========================================================
# MetricTrendAnalyzer
# ==========================================================

class MetricTrendAnalyzer:
    """
    Runtime Metrics Trend Analysis Engine.

    Features
    --------
    - Trend Analysis
    - Moving Average
    - EMA
    - Rolling Statistics
    - Seasonal Analysis
    - Momentum Analysis
    - Custom Algorithms
    """

    # ======================================================
    # Part 1. Foundation
    # ======================================================

    def __init__(
        self,
        name: str = "MetricTrendAnalyzer",
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
        # Trend Configuration
        # --------------------------------------------------

        self._config = {

            "window": 5,

            "alpha": 0.30,

            "beta": 0.20,

            "season_length": 12,

            "min_samples": 3,

        }

        # --------------------------------------------------
        # Trend Registry
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

        self._trend_count = 0

        self._analysis_count = 0

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

        self._context: dict[str, Any] = {}

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
    # Trend Configuration
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

    @property
    def trend_count(self):

        return self._trend_count

    @property
    def analysis_count(self):

        return self._analysis_count

    @property
    def error_count(self):

        return self._error_count

    # ======================================================
    # NOTE
    # ======================================================
    # Python Protocols (__repr__, __len__, __iter__, ...)
    # sẽ được triển khai trong Part 10.
    # ======================================================
        # ======================================================
    # Part 2. Trend Analysis API
    # ======================================================

    def analyze(
        self,
        values,
        method: str = "linear",
        **kwargs,
    ):
        """
        Analyze a sequence using a registered trend algorithm.

        Parameters
        ----------
        values:
            Iterable of numeric values.

        method:
            Registered algorithm name.

        Returns
        -------
        dict
        """

        if not self.active:

            raise RuntimeError(
                "MetricTrendAnalyzer is not active."
            )

        entry = self._algorithms.get(
            method
        )

        if entry is None:

            raise KeyError(
                f"Unknown trend algorithm: {method}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Trend algorithm '{method}' is disabled."
            )

        start = time.perf_counter()

        self._running = True

        try:

            result = entry["callable"](
                values,
                **kwargs,
            )

            elapsed = (
                time.perf_counter()
                - start
            )

            self._latency = elapsed

            self._analysis_count += 1

            if isinstance(
                result,
                dict,
            ):

                if "trend" in result:

                    self._trend_count += 1

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
        values,
        method: str = "linear",
        **kwargs,
    ):
        """
        Analyze one dataset.
        """

        return self.analyze(

            values,

            method=method,

            **kwargs,

        )

    def analyze_many(
        self,
        datasets,
        method: str = "linear",
        **kwargs,
    ):
        """
        Analyze multiple datasets.
        """

        results = []

        for values in datasets:

            results.append(

                self.analyze(

                    values,

                    method=method,

                    **kwargs,

                )

            )

        return results

    def analyze_batch(
        self,
        batches,
        method: str = "linear",
        **kwargs,
    ):
        """
        Batch trend analysis.
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
    # Part 3. Trend Algorithms
    # ======================================================

    def linear(
        self,
        values,
    ):
        """
        Linear trend using least-squares regression.
        """

        values = list(values)

        n = len(values)

        if n == 0:

            return {

                "algorithm": "linear",

                "trend": "stable",

                "slope": 0.0,

                "intercept": 0.0,

            }

        if n == 1:

            return {

                "algorithm": "linear",

                "trend": "stable",

                "slope": 0.0,

                "intercept": values[0],

            }

        x_mean = sum(
            range(n)
        ) / n

        y_mean = sum(
            values
        ) / n

        numerator = 0.0

        denominator = 0.0

        for x, y in enumerate(values):

            dx = x - x_mean

            numerator += dx * (
                y - y_mean
            )

            denominator += dx * dx

        slope = (

            numerator / denominator

            if denominator

            else 0.0

        )

        intercept = (

            y_mean
            -
            slope * x_mean

        )

        if slope > 0:

            trend = "upward"

        elif slope < 0:

            trend = "downward"

        else:

            trend = "stable"

        return {

            "algorithm": "linear",

            "trend": trend,

            "slope": slope,

            "intercept": intercept,

        }

    def slope(
        self,
        values,
    ):
        """
        Endpoint slope.
        """

        values = list(values)

        if len(values) < 2:

            slope = 0.0

        else:

            slope = (

                values[-1]
                -
                values[0]

            ) / (

                len(values) - 1

            )

        return {

            "algorithm": "slope",

            "trend":

                "upward"

                if slope > 0

                else

                "downward"

                if slope < 0

                else

                "stable",

            "slope": slope,

        }

    def momentum(
        self,
        values,
    ):
        """
        Last-step momentum.
        """

        values = list(values)

        if len(values) < 2:

            momentum = 0.0

        else:

            momentum = (

                values[-1]
                -
                values[-2]

            )

        return {

            "algorithm": "momentum",

            "trend":

                "upward"

                if momentum > 0

                else

                "downward"

                if momentum < 0

                else

                "stable",

            "momentum": momentum,

        }

    def moving_average(
        self,
        values,
        window: int | None = None,
    ):
        """
        Moving average.
        """

        values = list(values)

        if not values:

            return {

                "algorithm": "moving_average",

                "trend": "stable",

                "average": 0.0,

            }

        if window is None:

            window = self._config[
                "window"
            ]

        window = max(
            1,
            min(
                window,
                len(values),
            ),
        )

        average = (

            sum(
                values[-window:]
            )

            / window

        )

        if values[-1] > average:

            trend = "upward"

        elif values[-1] < average:

            trend = "downward"

        else:

            trend = "stable"

        return {

            "algorithm": "moving_average",

            "trend": trend,

            "average": average,

            "window": window,

        }

    def ema(
        self,
        values,
        alpha: float | None = None,
    ):
        """
        Exponential Moving Average.
        """

        values = list(values)

        if not values:

            return {

                "algorithm": "ema",

                "trend": "stable",

                "ema": 0.0,

            }

        if alpha is None:

            alpha = self._config[
                "alpha"
            ]

        estimate = values[0]

        for value in values[1:]:

            estimate = (

                alpha * value

                +

                (1 - alpha)
                * estimate

            )

        if values[-1] > estimate:

            trend = "upward"

        elif values[-1] < estimate:

            trend = "downward"

        else:

            trend = "stable"

        return {

            "algorithm": "ema",

            "trend": trend,

            "ema": estimate,

            "alpha": alpha,

        }

    def rolling(
        self,
        values,
        window: int | None = None,
    ):
        """
        Rolling averages.
        """

        values = list(values)

        if window is None:

            window = self._config[
                "window"
            ]

        if len(values) < window:

            return self.moving_average(
                values,
                window,
            )

        rolling_values = []

        for i in range(

            len(values)
            -
            window
            +
            1

        ):

            chunk = values[
                i:i + window
            ]

            rolling_values.append(

                sum(chunk)
                / window

            )

        return {

            "algorithm": "rolling",

            "trend": self.linear(
                rolling_values
            )["trend"],

            "rolling": rolling_values,

        }

    def seasonal(
        self,
        values,
        season_length: int | None = None,
    ):
        """
        Seasonal trend.
        """

        values = list(values)

        if season_length is None:

            season_length = self._config[
                "season_length"
            ]

        if len(values) < season_length:

            return self.linear(
                values
            )

        season = values[
            -season_length:
        ]

        result = self.linear(
            season
        )

        result["algorithm"] = (
            "seasonal"
        )

        result["season_length"] = (
            season_length
        )

        return result

    def cumulative(
        self,
        values,
    ):
        """
        Cumulative trend.
        """

        values = list(values)

        cumulative = []

        total = 0.0

        for value in values:

            total += value

            cumulative.append(
                total
            )

        return {

            "algorithm": "cumulative",

            "trend": self.linear(
                cumulative
            )["trend"],

            "cumulative": cumulative,

        }

    def custom(
        self,
        values,
        analyzer: Callable,
        **kwargs,
    ):
        """
        Execute user-defined analyzer.
        """

        if not callable(
            analyzer
        ):

            raise TypeError(
                "analyzer must be callable."
            )

        return analyzer(

            values,

            **kwargs,

        )
    # ======================================================
    # Part 4. Trend Registry API
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
        Register a trend analysis algorithm.
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

    # Backward compatibility

    unregister_algorithm = remove_algorithm

    def algorithm(
        self,
        name: str,
        default=None,
    ):
        """
        Get algorithm entry.
        """

        return self._algorithms.get(
            name,
            default,
        )

    def algorithms(self):
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
        Enable algorithm.
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
        Disable algorithm.
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
        Return algorithm names.
        """

        return list(
            self._algorithms.keys()
        )

    @property
    def algorithm_count(
        self,
    ):
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
        Remove every algorithm.
        """

        with self._lock:

            self._algorithms.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_algorithm(
        self,
        name: str,
        values,
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
                f"Unknown trend algorithm: {name}"
            )

        if not entry.get(
            "enabled",
            True,
        ):

            raise RuntimeError(
                f"Trend algorithm '{name}' is disabled."
            )

        return entry["callable"](

            values,

            **kwargs,

        )

    def register_builtin_algorithms(
        self,
    ):
        """
        Register all built-in algorithms.
        """

        self.register_algorithm(
            "linear",
            self.linear,
        )

        self.register_algorithm(
            "slope",
            self.slope,
        )

        self.register_algorithm(
            "momentum",
            self.momentum,
        )

        self.register_algorithm(
            "moving_average",
            self.moving_average,
        )

        self.register_algorithm(
            "ema",
            self.ema,
        )

        self.register_algorithm(
            "rolling",
            self.rolling,
        )

        self.register_algorithm(
            "seasonal",
            self.seasonal,
        )

        self.register_algorithm(
            "cumulative",
            self.cumulative,
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
        Enable the trend analyzer.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(
        self,
    ):
        """
        Disable the trend analyzer.
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
        Freeze the trend analyzer.
        """

        with self._lock:

            self._frozen = True

            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(
        self,
    ):
        """
        Unfreeze the trend analyzer.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(
        self,
    ):
        """
        Close the trend analyzer.
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
        Reopen the trend analyzer.
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

            self._trend_count = 0

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

                "last_result": self._last_result,

                "trend_count": self._trend_count,

                "analysis_count": self._analysis_count,

                "error_count": self._error_count,

                "latency": self._latency,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "updated_at": self._updated_at,

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

            self._trend_count = snapshot.get(
                "trend_count",
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

        The clone preserves the logical identity and runtime state
        of the source analyzer while remaining a distinct object.
        """

        cloned = self.__class__(
            name=self._name,
            description=self._description,
        )

        cloned.restore(
            self.snapshot()
        )

        # Preserve logical identity.
        cloned._id = self._id

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

            "frozen": self._frozen,

            "closed": self._closed,

            "running": self._running,

            "algorithm_count": len(
                self._algorithms
            ),

            "history_size": len(
                self._history
            ),

            "trend_count": self._trend_count,

            "analysis_count": self._analysis_count,

            "error_count": self._error_count,

            "latency": self._latency,

            "uptime": self.uptime,

            "updated_at": self._updated_at,

        }

    def report(
        self,
    ) -> dict:
        """
        Return diagnostics report.
        """

        return {

            "summary": self.summary(),

            "algorithms": self.algorithm_names(),

            "configuration": dict(
                self._config
            ),

            "statistics": {

                "trend_count":
                    self._trend_count,

                "analysis_count":
                    self._analysis_count,

                "error_count":
                    self._error_count,

                "history_size":
                    len(self._history),

            },

            "last_result":
                self._last_result,

        }

    def health(
        self,
    ) -> dict:
        """
        Runtime health information.
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

            "healthy": (

                self.active

                and

                self._error_count == 0

            ),

            "state": state,

            "errors": self._error_count,

            "latency": self._latency,

            "uptime": self.uptime,

        }

    def status(
        self,
    ) -> dict:
        """
        Return runtime status.
        """

        return {

            "enabled": self._enabled,

            "disabled": self.disabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "running": self._running,

            "active": self.active,

        }

    # ------------------------------------------------------
    # Runtime Metrics
    # ------------------------------------------------------

    @property
    def trend_count(
        self,
    ) -> int:

        return self._trend_count

    @property
    def analysis_count(
        self,
    ) -> int:

        return self._analysis_count

    @property
    def error_count(
        self,
    ) -> int:

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

    def to_dict(
        self,
    ) -> dict:
        """
        Serialize analyzer to dictionary.
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

            "trend_count": self._trend_count,

            "analysis_count": self._analysis_count,

            "error_count": self._error_count,

            "latency": self._latency,

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
        Restore analyzer from dictionary.
        """

        obj = cls(

            name=data.get(
                "name",
                "MetricTrendAnalyzer",
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

        obj._trend_count = data.get(
            "trend_count",
            0,
        )

        obj._analysis_count = data.get(
            "analysis_count",
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
        Serialize analyzer to JSON.
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
        Restore analyzer from JSON.
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
        Deserialize analyzer from dict or JSON.
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

    def before_analyze(
        self,
        values,
        method: str,
        **kwargs,
    ):
        """
        Hook executed before trend analysis.
        """

        self.emit(

            "before_analyze",

            values=values,

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
        Hook executed after trend analysis.
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

        if not callable(
            callback
        ):

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
        Remove one hook or all hooks of an event.
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

                self._hooks[
                    event
                ].remove(
                    callback
                )

            except ValueError:

                pass

            if not self._hooks[
                event
            ]:

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

            f"running={self._running}, "

            f"algorithms={len(self._algorithms)}, "

            f"analyses={self._analysis_count}"

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

            f"[enabled={self._enabled}, "

            f"running={self._running}, "

            f"algorithms={len(self._algorithms)}]"

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
        Iterate over registered algorithm names.
        """

        return iter(
            self._algorithms
        )

    def __contains__(
        self,
        name,
    ) -> bool:
        """
        Membership test.
        """

        return (

            name

            in

            self._algorithms

        )

    def __call__(
        self,
        values,
        method: str = "linear",
        **kwargs,
    ):
        """
        Callable interface.
        """

        return self.analyze(

            values,

            method=method,

            **kwargs,

        )

    def __copy__(
        self,
    ):
        """
        Shallow copy.
        """

        return self.copy()

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy.
        """

        del memo

        return self.clone()                                                            