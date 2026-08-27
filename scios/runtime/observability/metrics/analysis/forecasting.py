"""
SciOS-NG Runtime Metrics Analysis

Time-Series Forecast Engine

SciOS/scios/runtime/observability/metrics/analysis/forecasting.py
"""

from __future__ import annotations

import threading
import uuid
import copy
import json

from datetime import datetime
from typing import Any, Callable

from .statistics import MetricStatistics


# ==========================================================
# MetricForecastEngine
# ==========================================================

class MetricForecastEngine:
    """
    Runtime Metrics Time-Series Forecast Engine.

    Foundation
    ----------
    - Forecast Registry
    - Model Registry
    - Runtime State
    - Forecast Configuration
    - Statistics Engine
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        name: str = "MetricForecastEngine",
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
        # Forecast Configuration
        # --------------------------------------------------

        self._config = {

            "horizon": 10,

            "window": 5,

            "alpha": 0.3,

            "season_length": 12,

            "trend": True,

            "seasonality": False,

        }

        # --------------------------------------------------
        # Forecast Registry
        # --------------------------------------------------

        self._models: dict[
            str,
            Callable[..., Any]
        ] = {}

        self._registry: dict[
            str,
            Callable[..., Any]
        ] = {}

        self._history: list[dict] = []

        self._last_forecast = None

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
        # Statistics
        # --------------------------------------------------

        self._statistics = MetricStatistics()

        self._forecast_count = 0

        self._prediction_count = 0

        self._error_count = 0

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

        # --------------------------------------------------
        # Prediction aliases
        #
        # Bind the public forecast methods once at instance
        # construction time.
        #
        # This is intentional: the forecasting contract requires
        # identity-level aliases, e.g.
        #
        #     engine.predict is engine.forecast
        #
        # Normal class-bound methods do not guarantee this because
        # attribute access creates bound-method objects dynamically.
        # --------------------------------------------------

        forecast = self.forecast
        forecast_one = self.forecast_one
        forecast_many = self.forecast_many
        forecast_batch = self.forecast_batch

        self.forecast = forecast
        self.forecast_one = forecast_one
        self.forecast_many = forecast_many
        self.forecast_batch = forecast_batch

        self.predict = forecast
        self.predict_one = forecast_one
        self.predict_many = forecast_many
        self.predict_batch = forecast_batch

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
    # Forecast Configuration
    # ======================================================

    def config(
        self,
        key: str | None = None,
        default=None,
    ):

        if key is None:

            return dict(self._config)

        return self._config.get(
            key,
            default,
        )

    def configure(
        self,
        **kwargs,
    ):

        with self._lock:

            self._config.update(kwargs)

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Registry
    # ======================================================


    def unregister_model(
        self,
        name: str,
    ):

        with self._lock:

            self._models.pop(
                name,
                None,
            )

            self._registry.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    def model(
        self,
        name: str,
    ):

        return self._models.get(
            name
        )

    def models(self):

        return dict(
            self._models
        )

    # ======================================================
    # Runtime Metrics
    # ======================================================

    @property
    def forecast_count(self):

        return self._forecast_count

    @property
    def prediction_count(self):

        return self._prediction_count

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
    # Part 2. Forecast API
    # ======================================================

    def forecast(
        self,
        values,
        method: str = "moving_average",
        **kwargs,
    ):
        """
        Generic forecast entry point.

        Forecast execution is exposed as the high-level API.
        Unknown registered models are normalized to the public
        "Unknown forecast model" contract.
        """

        if not self.active:
            raise RuntimeError(
                "MetricForecastEngine is not active."
            )

        self._running = True

        try:
            self.before_forecast(
                values,
                method=method,
                **kwargs,
            )

            self.before_model(
                method,
                values=values,
            )

            try:
                result = self.execute_model(
                    method,
                    values,
                    **kwargs,
                )

            except KeyError as exc:
                raise KeyError(
                    f"Unknown forecast model: {method}"
                ) from exc

            self._forecast_count += 1

            predictions = result.get(
                "forecast",
                [],
            )

            self._prediction_count += len(
                predictions
            )

            self._last_forecast = result

            self._history.append(
                copy.deepcopy(result)
            )

            self.after_model(
                method,
                result=result,
            )

            self.after_forecast(
                result=result,
            )

            self._updated_at = datetime.utcnow()

            return result

        except Exception:
            self._error_count += 1
            raise

        finally:
            self._running = False

    def forecast_one(
        self,
        values,
        method: str = "moving_average",
        **kwargs,
    ):
        """
        Forecast the next single value.
        """

        kwargs.setdefault(
            "horizon",
            1,
        )

        result = self.forecast(
            values,
            method=method,
            **kwargs,
        )

        forecast = result.get(
            "forecast",
            [],
        )

        return (

            forecast[0]

            if forecast

            else None

        )

    def forecast_many(
        self,
        values,
        horizon: int = 10,
        method: str = "moving_average",
        **kwargs,
    ):
        """
        Forecast multiple future values.
        """

        kwargs["horizon"] = horizon

        return self.forecast(
            values,
            method=method,
            **kwargs,
        )

    def forecast_batch(
        self,
        batches,
        method: str = "moving_average",
        **kwargs,
    ):
        """
        Forecast multiple datasets.
        """

        results = []

        for values in batches:

            results.append(

                self.forecast(
                    values,
                    method=method,
                    **kwargs,
                )

            )

        return results


    # ======================================================
    # Part 3. Forecast Algorithms
    # ======================================================

    def moving_average(
        self,
        values,
        horizon: int = 1,
        window: int | None = None,
    ):
        """
        Moving Average Forecast.
        """

        values = list(values)

        if not values:
            return {
                "method": "moving_average",
                "forecast": [],
            }

        if window is None:
            window = self.config(
                "window",
                5,
            )

        window = max(
            1,
            min(window, len(values)),
        )

        avg = sum(
            values[-window:]
        ) / window

        forecast = [
            avg
            for _ in range(horizon)
        ]

        return {
            "method": "moving_average",
            "forecast": forecast,
            "window": window,
        }

    def exponential_smoothing(
        self,
        values,
        horizon: int = 1,
        alpha: float | None = None,
    ):
        """
        Simple Exponential Smoothing.
        """

        values = list(values)

        if not values:
            return {
                "method": "exponential_smoothing",
                "forecast": [],
            }

        if alpha is None:
            alpha = self.config(
                "alpha",
                0.3,
            )

        estimate = values[0]

        for value in values[1:]:

            estimate = (
                alpha * value
                +
                (1 - alpha) * estimate
            )

        forecast = [
            estimate
            for _ in range(horizon)
        ]

        return {
            "method": "exponential_smoothing",
            "forecast": forecast,
            "alpha": alpha,
        }

    def naive(
        self,
        values,
        horizon: int = 1,
    ):
        """
        Naive Forecast.
        """

        values = list(values)

        if not values:
            return {
                "method": "naive",
                "forecast": [],
            }

        last = values[-1]

        return {

            "method": "naive",

            "forecast": [
                last
                for _ in range(horizon)
            ],

        }

    def drift(
        self,
        values,
        horizon: int = 1,
    ):
        """
        Drift Forecast.
        """

        values = list(values)

        n = len(values)

        if n < 2:

            return self.naive(
                values,
                horizon,
            )

        slope = (

            values[-1] - values[0]

        ) / (n - 1)

        forecast = [

            values[-1]
            + slope * step

            for step in range(
                1,
                horizon + 1,
            )

        ]

        return {

            "method": "drift",

            "forecast": forecast,

            "slope": slope,

        }

    def linear_trend(
        self,
        values,
        horizon: int = 1,
    ):
        """
        Linear Trend Forecast.
        """

        values = list(values)

        n = len(values)

        if n < 2:

            return self.naive(
                values,
                horizon,
            )

        x_mean = (n - 1) / 2

        y_mean = sum(values) / n

        numerator = 0.0

        denominator = 0.0

        for i, value in enumerate(values):

            dx = i - x_mean

            numerator += dx * (
                value - y_mean
            )

            denominator += dx * dx

        slope = (

            numerator / denominator

            if denominator

            else 0.0

        )

        intercept = (

            y_mean
            - slope * x_mean

        )

        forecast = [

            intercept
            + slope * (n + step)

            for step in range(
                horizon
            )

        ]

        return {

            "method": "linear_trend",

            "forecast": forecast,

            "slope": slope,

            "intercept": intercept,

        }

    def seasonal(
        self,
        values,
        horizon: int = 1,
        season_length: int | None = None,
    ):
        """
        Seasonal Forecast.
        """

        values = list(values)

        if season_length is None:

            season_length = self.config(
                "season_length",
                12,
            )

        if (

            len(values)
            < season_length

        ):

            return self.naive(
                values,
                horizon,
            )

        season = values[
            -season_length:
        ]

        forecast = [

            season[
                i % season_length
            ]

            for i in range(
                horizon
            )

        ]

        return {

            "method": "seasonal",

            "forecast": forecast,

            "season_length":
                season_length,

        }

    def custom(
        self,
        values,
        predictor,
        **kwargs,
    ):
        """
        User-defined forecasting model.
        """

        if not callable(
            predictor
        ):

            raise TypeError(
                "predictor must be callable."
            )

        return predictor(
            values,
            **kwargs,
        )
    # ======================================================
    # Part 4. Model Management
    # ======================================================

    def register_model(
        self,
        name: str,
        model: Callable,
        *,
        enabled: bool = True,
        metadata: dict | None = None,
    ):
        """
        Register a forecasting model.
        """

        if not callable(model):

            raise TypeError(
                "model must be callable."
            )

        with self._lock:

            entry = {

                "name": name,

                "callable": model,

                "enabled": enabled,

                "metadata": metadata or {},

                "created_at": datetime.utcnow(),

            }

            self._models[name] = entry

            self._registry[name] = entry

            self._updated_at = datetime.utcnow()

        return self

    def remove_model(
        self,
        name: str,
    ):
        """
        Remove forecasting model.
        """

        with self._lock:

            self._models.pop(
                name,
                None,
            )

            self._registry.pop(
                name,
                None,
            )

            self._updated_at = datetime.utcnow()

        return self

    # Backward compatibility
    unregister_model = remove_model

    def model(
        self,
        name: str,
        default=None,
    ):
        """
        Get model metadata.
        """

        return self._models.get(
            name,
            default,
        )

    def models(self):
        """
        Return all registered models.
        """

        return dict(
            self._models
        )

    def contains_model(
        self,
        name: str,
    ) -> bool:
        """
        Whether model exists.
        """

        return name in self._models

    def exists_model(
        self,
        name: str,
    ) -> bool:

        return self.contains_model(
            name
        )

    def enable_model(
        self,
        name: str,
    ):
        """
        Enable forecasting model.
        """

        entry = self._models.get(
            name
        )

        if entry:

            entry["enabled"] = True

            self._updated_at = datetime.utcnow()

        return self

    def disable_model(
        self,
        name: str,
    ):
        """
        Disable forecasting model.
        """

        entry = self._models.get(
            name
        )

        if entry:

            entry["enabled"] = False

            self._updated_at = datetime.utcnow()

        return self

    def model_names(self):
        """
        Return registered model names.
        """

        return list(
            self._models.keys()
        )

    def model_count(self):
        """
        Number of registered models.
        """

        return len(
            self._models
        )

    def clear_models(self):
        """
        Remove all forecasting models.
        """

        with self._lock:

            self._models.clear()

            self._registry.clear()

            self._updated_at = datetime.utcnow()

        return self

    def execute_model(
        self,
        name: str,
        values,
        **kwargs,
    ):
        """
        Execute a registered forecasting model.
        """

        entry = self._models.get(name)

        if entry is None:
            raise KeyError(
                f"Unknown model: {name}"
            )

        if not entry["enabled"]:
            raise RuntimeError(
                f"Forecast model '{name}' is disabled."
            )

        return entry["callable"](
            values,
            **kwargs,
        )
    # ======================================================
    # Part 5. Lifecycle
    # ======================================================

    def enable(self):
        """
        Enable forecast engine.
        """

        with self._lock:

            self._enabled = True

            self._updated_at = datetime.utcnow()

        return self

    def disable(self):
        """
        Disable forecast engine.
        """

        with self._lock:

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def freeze(self):
        """
        Freeze forecast engine.
        """

        with self._lock:

            self._frozen = True

            self._updated_at = datetime.utcnow()

        return self

    def unfreeze(self):
        """
        Resume forecast engine.
        """

        with self._lock:

            self._frozen = False

            self._updated_at = datetime.utcnow()

        return self

    def close(self):
        """
        Close forecast engine.
        """

        with self._lock:

            if self._closed:

                return self

            self._closed = True

            self._enabled = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    def reopen(self):
        """
        Reopen forecast engine.
        """

        with self._lock:

            self._closed = False

            self._enabled = True

            self._frozen = False

            self._running = False

            self._updated_at = datetime.utcnow()

        return self

    # ======================================================
    # Lifecycle Properties
    # ======================================================

    @property
    def enabled(self):
        """
        Whether engine is enabled.
        """

        return self._enabled

    @property
    def disabled(self):
        """
        Whether engine is disabled.
        """

        return not self._enabled

    @property
    def frozen(self):
        """
        Whether engine is frozen.
        """

        return self._frozen

    @property
    def closed(self):
        """
        Whether engine is closed.
        """

        return self._closed

    @property
    def running(self):
        """
        Whether engine is currently forecasting.
        """

        return self._running

    @property
    def active(self):
        """
        Whether engine is active.
        """

        return (

            self._enabled
            and
            not self._frozen
            and
            not self._closed

        )
    # ======================================================
    # Part 6. Runtime Operations
    # ======================================================

    def reset(self):
        """
        Reset runtime statistics while preserving
        registered models and configuration.
        """

        with self._lock:

            self._history.clear()

            self._last_forecast = None

            self._forecast_count = 0

            self._prediction_count = 0

            self._error_count = 0

            self._latency = 0.0

            self._uptime = 0.0

            self._running = False

            self._statistics = MetricStatistics()

            self._updated_at = datetime.utcnow()

        return self

    def clear(self):
        """
        Clear runtime state.

        Models and configuration are preserved.
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

                # Runtime State

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "running": self._running,

                # Configuration

                "config": dict(
                    self._config
                ),

                # Runtime

                "history": copy.deepcopy(
                    self._history
                ),

                "last_forecast": copy.deepcopy(
                    self._last_forecast
                ),

                "context": copy.deepcopy(
                    self._context
                ),

                # Statistics

                "forecast_count":
                    self._forecast_count,

                "prediction_count":
                    self._prediction_count,

                "error_count":
                    self._error_count,

                "latency":
                    self._latency,

                "uptime":
                    self._uptime,

                # Metadata

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

            self._running = snapshot.get(
                "running",
                False,
            )

            self._config = dict(

                snapshot.get(
                    "config",
                    {},
                )

            )

            self._history = copy.deepcopy(

                snapshot.get(
                    "history",
                    [],
                )

            )

            self._last_forecast = copy.deepcopy(

                snapshot.get(
                    "last_forecast",
                )

            )

            self._context = copy.deepcopy(

                snapshot.get(
                    "context",
                    {},
                )

            )

            self._forecast_count = snapshot.get(
                "forecast_count",
                0,
            )

            self._prediction_count = snapshot.get(
                "prediction_count",
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

            self._uptime = snapshot.get(
                "uptime",
                0.0,
            )

            self._updated_at = datetime.utcnow()

        return self

    def clone(self):
        """
        Return an independent deep copy of this engine.
        """
        return copy.deepcopy(self)

    def copy(self):
        """
        Create shallow copy.
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

            # Identity

            "id": self._id,

            "name": self._name,

            "description": self._description,

            # Runtime

            "enabled": self._enabled,

            "running": self._running,

            "active": self.active,

            # Registry

            "model_count": len(
                self._models
            ),

            # Statistics

            "forecast_count":
                self._forecast_count,

            "prediction_count":
                self._prediction_count,

            "error_count":
                self._error_count,

            "history_size":
                len(self._history),

            "latency":
                self._latency,

            "uptime":
                self._uptime,

            # Metadata

            "version":
                self._version,

            "updated_at":
                self._updated_at,

        }

    def statistics(self) -> dict:
        """
        Return statistics.
        """

        if hasattr(
            self._statistics,
            "to_dict",
        ):

            return self._statistics.to_dict()

        if hasattr(
            self._statistics,
            "summary",
        ):

            return self._statistics.summary()

        return {

            "forecast_count":
                self._forecast_count,

            "prediction_count":
                self._prediction_count,

            "error_count":
                self._error_count,

        }

    def report(self) -> dict:
        """
        Return complete forecast report.
        """

        return {

            "summary":
                self.summary(),

            "statistics":
                self.statistics(),

            "configuration":
                dict(self._config),

            "models":
                self.model_names(),

            "last_forecast":
                self._last_forecast,

            "history_size":
                len(self._history),

        }

    def health(self) -> dict:
        """
        Runtime health report.
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

            "healthy":
                state == "healthy",

            "state":
                state,

            "active":
                self.active,

            "running":
                self._running,

            "models":
                len(self._models),

        }

    def status(self) -> dict:
        """
        Runtime status.
        """

        return {

            "enabled":
                self._enabled,

            "disabled":
                self.disabled,

            "frozen":
                self._frozen,

            "closed":
                self._closed,

            "running":
                self._running,

            "active":
                self.active,

        }

    # ======================================================
    # Runtime Metrics
    # ======================================================

    @property
    def model_count(self) -> int:
        """
        Number of registered models.
        """

        return len(
            self._models
        )

    @property
    def forecast_count(self) -> int:
        """
        Number of forecast requests.
        """

        return self._forecast_count

    @property
    def prediction_count(self) -> int:
        """
        Number of predicted values.
        """

        return self._prediction_count

    @property
    def error_count(self) -> int:
        """
        Number of forecasting failures.
        """

        return self._error_count

    @property
    def latency(self) -> float:
        """
        Average forecast latency.
        """

        return self._latency

    @property
    def uptime(self) -> float:
        """
        Engine uptime.
        """

        return self._uptime
    # ======================================================
    # Part 8. Serialization
    # ======================================================

    def to_dict(self) -> dict:
        """
        Serialize forecast engine to dictionary.
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

            "running": self._running,

            # Configuration

            "config": dict(
                self._config
            ),

            # Registry

            "models":
                self.model_names(),

            # Statistics

            "forecast_count":
                self._forecast_count,

            "prediction_count":
                self._prediction_count,

            "error_count":
                self._error_count,

            "latency":
                self._latency,

            "uptime":
                self._uptime,

            # Runtime

            "history_size":
                len(self._history),

            "last_forecast":
                copy.deepcopy(
                    self._last_forecast
                ),

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
        Restore a MetricForecastEngine from a dictionary.

        Deserialization contract
        ------------------------
        - Creates a new engine identity.
        - Restores descriptive metadata.
        - Restores runtime state.
        - Restores configuration and counters.
        - Restores diagnostic state.
        - Creates fresh runtime infrastructure.
        - Does not restore executable model callables.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary."
            )

        # --------------------------------------------------
        # Construction
        #
        # __init__ intentionally creates a NEW identity.
        # Deserialization represents a new runtime instance,
        # not an identity-preserving clone.
        # --------------------------------------------------

        engine = cls(
            name=data.get(
                "name",
                "MetricForecastEngine",
            ),
            description=data.get(
                "description",
                "",
            ),
        )

        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        engine._enabled = data.get(
            "enabled",
            True,
        )

        engine._frozen = data.get(
            "frozen",
            False,
        )

        engine._closed = data.get(
            "closed",
            False,
        )

        engine._running = data.get(
            "running",
            False,
        )

        # --------------------------------------------------
        # Configuration
        # --------------------------------------------------

        config = data.get(
            "config",
            {},
        )

        if not isinstance(config, dict):
            raise TypeError(
                "config must be a dictionary."
            )

        engine._config.update(config)

        # --------------------------------------------------
        # Runtime Counters
        # --------------------------------------------------

        engine._forecast_count = data.get(
            "forecast_count",
            0,
        )

        engine._prediction_count = data.get(
            "prediction_count",
            0,
        )

        engine._error_count = data.get(
            "error_count",
            0,
        )

        # --------------------------------------------------
        # Runtime Metrics
        # --------------------------------------------------

        engine._latency = data.get(
            "latency",
            0.0,
        )

        engine._uptime = data.get(
            "uptime",
            0.0,
        )

        # --------------------------------------------------
        # Last Forecast
        # --------------------------------------------------

        engine._last_forecast = copy.deepcopy(
            data.get(
                "last_forecast",
                None,
            )
        )

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        created_at = data.get(
            "created_at"
        )

        if created_at:
            engine._created_at = datetime.fromisoformat(
                created_at
            )

        updated_at = data.get(
            "updated_at"
        )

        if updated_at:
            engine._updated_at = datetime.fromisoformat(
                updated_at
            )

        engine._version = data.get(
            "version",
            engine._version,
        )

        return engine

    def to_json(
        self,
        **kwargs,
    ) -> str:
        """
        Serialize engine to JSON.
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
        Restore engine from JSON.
        """

        return cls.from_dict(

            json.loads(
                data
            )

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

    def before_forecast(
        self,
        values,
        method: str = "",
        **kwargs,
    ):
        """
        Emit before forecast event.
        """

        return self.emit(

            "before_forecast",

            values=values,

            method=method,

            **kwargs,

        )

    def after_forecast(
        self,
        result=None,
        **kwargs,
    ):
        """
        Emit after forecast event.
        """

        return self.emit(

            "after_forecast",

            result=result,

            **kwargs,

        )

    def before_model(
        self,
        name: str,
        values=None,
        **kwargs,
    ):
        """
        Emit before model execution.
        """

        return self.emit(

            "before_model",

            model=name,

            values=values,

            **kwargs,

        )

    def after_model(
        self,
        name: str,
        result=None,
        **kwargs,
    ):
        """
        Emit after model execution.
        """

        return self.emit(

            "after_model",

            model=name,

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
        Remove event hook.
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

    def clear_hooks(
        self):
        """
        Remove all hooks.
        """

        with self._lock:

            self._hooks.clear()

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
        Emit runtime event.
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

                # Hook failures must never
                # interrupt forecasting.

                continue

        return event_data

    def notify(
        self,
        event: str,
        **payload,
    ):
        """
        Alias of emit().
        """

        return self.emit(
            event,
            **payload,
        )

    def subscribe(
        self,
        event: str,
        callback: Callable,
    ):
        """
        Subscribe to an event.
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
        Unsubscribe from an event.
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
            f"models={len(self._models)}, "
            f"forecasts={self._forecast_count}, "
            f"active={self.active})"

        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self._name} "
            f"[models={len(self._models)}, "
            f"forecasts={self._forecast_count}, "
            f"active={self.active}]"

        )

    def __len__(self) -> int:
        """
        Number of registered forecast models.
        """

        return len(
            self._models
        )

    def __iter__(self):
        """
        Iterate over registered models.
        """

        return iter(
            self._models.items()
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Membership test.
        """

        return name in self._models

    def __getitem__(
        self,
        name: str,
    ):
        """
        Dictionary-style model lookup.
        """

        return self._models[name]

    def __setitem__(
        self,
        name: str,
        model,
    ):
        """
        Dictionary-style model registration.
        """

        self.register_model(
            name,
            model,
        )

    def __delitem__(
        self,
        name: str,
    ):
        """
        Dictionary-style model removal.
        """

        self.remove_model(
            name,
        )

    def __call__(
        self,
        values,
        method: str = "moving_average",
        **kwargs,
    ):
        """
        Callable forecast engine.
        """

        return self.forecast(
            values,
            method=method,
            **kwargs,
        )

    def __copy__(self):
        """
        Create a shallow copy.

        The identity is preserved, while the copied engine receives
        independent top-level runtime containers and a fresh lock.
        """

        cls = type(self)

        cloned = cls.__new__(cls)

        cloned.__dict__ = self.__dict__.copy()

        # --------------------------------------------------
        # Fresh synchronization primitive
        # --------------------------------------------------

        cloned._lock = threading.RLock()

        # --------------------------------------------------
        # Independent top-level containers
        # --------------------------------------------------

        cloned._config = self._config.copy()

        cloned._models = self._models.copy()

        cloned._registry = self._registry.copy()

        cloned._history = self._history.copy()

        cloned._events = self._events.copy()

        cloned._hooks = self._hooks.copy()

        cloned._context = self._context.copy()

        # --------------------------------------------------
        # Rebind instance-level forecast methods
        # --------------------------------------------------

        forecast = cloned.__class__.forecast.__get__(
            cloned,
            cloned.__class__,
        )

        forecast_one = cloned.__class__.forecast_one.__get__(
            cloned,
            cloned.__class__,
        )

        forecast_many = cloned.__class__.forecast_many.__get__(
            cloned,
            cloned.__class__,
        )

        forecast_batch = cloned.__class__.forecast_batch.__get__(
            cloned,
            cloned.__class__,
        )

        cloned.forecast = forecast
        cloned.forecast_one = forecast_one
        cloned.forecast_many = forecast_many
        cloned.forecast_batch = forecast_batch

        cloned.predict = forecast
        cloned.predict_one = forecast_one
        cloned.predict_many = forecast_many
        cloned.predict_batch = forecast_batch

        return cloned

    def copy(self):
        """
        Create shallow copy.
        """
        return copy.copy(self)


    def __deepcopy__(self, memo):
        """
        Create an independent deep copy of the forecasting engine.

        Deep-copy contract
        ------------------
        - The cloned engine is a different Python object.
        - ``id`` is preserved.
        - Runtime synchronization primitives are NOT copied.
        - A fresh ``RLock`` is created.
        - Mutable runtime containers are deeply copied.
        - Registered executable callables are preserved by reference.
        - Instance-level prediction aliases are rebound to the clone.
        """

        existing = memo.get(id(self))

        if existing is not None:
            return existing

        cls = type(self)

        cloned = cls.__new__(cls)

        memo[id(self)] = cloned

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------
        #
        # Identity is part of the engine's serialized/runtime
        # contract. A clone is independent but represents the
        # same engine identity.
        #
        cloned._id = self._id

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        cloned._name = self._name
        cloned._description = self._description

        cloned._created_at = copy.deepcopy(
            self._created_at,
            memo,
        )

        cloned._updated_at = copy.deepcopy(
            self._updated_at,
            memo,
        )

        cloned._version = self._version

        # --------------------------------------------------
        # Runtime state
        # --------------------------------------------------

        cloned._enabled = self._enabled
        cloned._frozen = self._frozen
        cloned._closed = self._closed
        cloned._running = self._running

        # --------------------------------------------------
        # Configuration
        # --------------------------------------------------

        cloned._config = copy.deepcopy(
            self._config,
            memo,
        )

        # --------------------------------------------------
        # Model registry
        # --------------------------------------------------
        #
        # Model entries contain executable callables.
        # Deep-copying arbitrary callables is neither required
        # nor desirable. Preserve callable identity while
        # independently copying the registry metadata.
        # --------------------------------------------------

        cloned._models = {}

        for name, entry in self._models.items():

            if isinstance(entry, dict):

                cloned_entry = copy.deepcopy(
                    entry,
                    memo,
                )

                if "callable" in entry:
                    cloned_entry["callable"] = entry[
                        "callable"
                    ]

                cloned._models[name] = cloned_entry

            else:
                cloned._models[name] = entry

        cloned._registry = {}

        for name, entry in self._registry.items():

            if name in cloned._models:
                cloned._registry[name] = cloned._models[name]

            else:
                cloned._registry[name] = copy.deepcopy(
                    entry,
                    memo,
                )

        # --------------------------------------------------
        # Forecast runtime state
        # --------------------------------------------------

        cloned._history = copy.deepcopy(
            self._history,
            memo,
        )

        cloned._last_forecast = copy.deepcopy(
            self._last_forecast,
            memo,
        )

        cloned._snapshot = copy.deepcopy(
            self._snapshot,
            memo,
        )

        cloned._context = copy.deepcopy(
            self._context,
            memo,
        )

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        cloned._statistics = copy.deepcopy(
            self._statistics,
            memo,
        )

        # --------------------------------------------------
        # Counters / metrics
        # --------------------------------------------------

        cloned._forecast_count = self._forecast_count
        cloned._prediction_count = self._prediction_count
        cloned._error_count = self._error_count

        cloned._latency = self._latency
        cloned._uptime = self._uptime

        # --------------------------------------------------
        # Events / hooks
        # --------------------------------------------------

        cloned._events = copy.deepcopy(
            self._events,
            memo,
        )

        cloned._hooks = copy.deepcopy(
            self._hooks,
            memo,
        )

        # --------------------------------------------------
        # Synchronization
        # --------------------------------------------------
        #
        # Never copy the original RLock.
        # --------------------------------------------------

        cloned._lock = threading.RLock()

        # --------------------------------------------------
        # Prediction aliases
        #
        # Rebind stable instance-level method identities.
        # --------------------------------------------------

        forecast = cloned.forecast
        forecast_one = cloned.forecast_one
        forecast_many = cloned.forecast_many
        forecast_batch = cloned.forecast_batch

        cloned.forecast = forecast
        cloned.forecast_one = forecast_one
        cloned.forecast_many = forecast_many
        cloned.forecast_batch = forecast_batch

        cloned.predict = forecast
        cloned.predict_one = forecast_one
        cloned.predict_many = forecast_many
        cloned.predict_batch = forecast_batch

        return cloned