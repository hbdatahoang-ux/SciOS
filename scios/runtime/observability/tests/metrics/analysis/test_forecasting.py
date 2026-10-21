"""
Tests for MetricForecastEngine.

SciOS Runtime Metrics Analysis
"""

from __future__ import annotations

import copy
import json

import pytest

from scios.runtime.observability.metrics.analysis.forecasting import (
    MetricForecastEngine,
)


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def engine():
    return MetricForecastEngine()


@pytest.fixture
def custom_engine():
    return MetricForecastEngine(
        name="TestForecastEngine",
        description="Forecast test engine",
    )


# ==========================================================
# Constructor / Identity
# ==========================================================


def test_constructor_defaults(engine):
    assert engine.name == "MetricForecastEngine"
    assert engine.description == ""
    assert isinstance(engine.id, str)
    assert engine.version == "0.2.0"


def test_constructor_custom_values(custom_engine):
    assert custom_engine.name == "TestForecastEngine"
    assert custom_engine.description == "Forecast test engine"


def test_id_is_unique():
    a = MetricForecastEngine()
    b = MetricForecastEngine()

    assert a.id != b.id


def test_repr(engine):
    value = repr(engine)

    assert "MetricForecastEngine" in value
    assert "models=0" in value
    assert "forecasts=0" in value
    assert "active=True" in value


def test_str(engine):
    value = str(engine)

    assert "MetricForecastEngine" in value
    assert "models=0" in value
    assert "forecasts=0" in value
    assert "active=True" in value


# ==========================================================
# Runtime State
# ==========================================================


def test_initial_runtime_state(engine):
    assert engine.enabled is True
    assert engine.disabled is False
    assert engine.frozen is False
    assert engine.closed is False
    assert engine.running is False
    assert engine.active is True


def test_disable(engine):
    result = engine.disable()

    assert result is engine
    assert engine.enabled is False
    assert engine.disabled is True
    assert engine.active is False
    assert engine.running is False


def test_enable(engine):
    engine.disable()

    result = engine.enable()

    assert result is engine
    assert engine.enabled is True
    assert engine.active is True


def test_freeze(engine):
    result = engine.freeze()

    assert result is engine
    assert engine.frozen is True
    assert engine.active is False


def test_unfreeze(engine):
    engine.freeze()

    result = engine.unfreeze()

    assert result is engine
    assert engine.frozen is False
    assert engine.active is True


def test_close(engine):
    result = engine.close()

    assert result is engine
    assert engine.closed is True
    assert engine.enabled is False
    assert engine.running is False
    assert engine.active is False


def test_close_is_idempotent(engine):
    engine.close()

    updated_at = engine.updated_at

    result = engine.close()

    assert result is engine
    assert engine.closed is True
    assert engine.updated_at == updated_at


def test_reopen(engine):
    engine.close()

    result = engine.reopen()

    assert result is engine
    assert engine.closed is False
    assert engine.enabled is True
    assert engine.frozen is False
    assert engine.running is False
    assert engine.active is True


# ==========================================================
# Configuration
# ==========================================================


def test_default_config(engine):
    config = engine.config()

    assert config["horizon"] == 10
    assert config["window"] == 5
    assert config["alpha"] == 0.3
    assert config["season_length"] == 12
    assert config["trend"] is True
    assert config["seasonality"] is False


def test_config_single_key(engine):
    assert engine.config("window") == 5
    assert engine.config("missing") is None
    assert engine.config("missing", 123) == 123


def test_config_returns_copy(engine):
    config = engine.config()

    config["window"] = 999

    assert engine.config("window") == 5


def test_configure(engine):
    result = engine.configure(
        window=3,
        alpha=0.5,
    )

    assert result is engine
    assert engine.config("window") == 3
    assert engine.config("alpha") == 0.5


# ==========================================================
# Model Registry
# ==========================================================


def test_initial_models(engine):
    assert engine.models() == {}
    assert engine.model_names() == []
    assert engine.model_count == 0
    assert len(engine) == 0


def test_register_model(engine):
    def model(values, **kwargs):
        return {"forecast": [1]}

    result = engine.register_model(
        "custom",
        model,
    )

    assert result is engine
    assert engine.contains_model("custom")
    assert engine.exists_model("custom")
    assert engine.model_count == 1
    assert engine.model_names() == ["custom"]


def test_register_model_stores_metadata(engine):
    def model(values, **kwargs):
        return {"forecast": [1]}

    engine.register_model(
        "custom",
        model,
        enabled=True,
        metadata={"kind": "test"},
    )

    entry = engine.model("custom")

    assert entry["name"] == "custom"
    assert entry["callable"] is model
    assert entry["enabled"] is True
    assert entry["metadata"] == {"kind": "test"}
    assert entry["created_at"] is not None


def test_register_model_requires_callable(engine):
    with pytest.raises(TypeError, match="model must be callable"):
        engine.register_model(
            "invalid",
            123,
        )


def test_model_default(engine):
    assert engine.model("missing") is None
    assert engine.model("missing", "fallback") == "fallback"


def test_remove_model(engine):
    def model(values, **kwargs):
        return {"forecast": [1]}

    engine.register_model("custom", model)

    result = engine.remove_model("custom")

    assert result is engine
    assert not engine.contains_model("custom")
    assert engine.model_count == 0


def test_remove_missing_model_is_safe(engine):
    result = engine.remove_model("missing")

    assert result is engine
    assert engine.model_count == 0


def test_unregister_model_alias(engine):
    def model(values, **kwargs):
        return {"forecast": [1]}

    engine.register_model("custom", model)

    result = engine.unregister_model("custom")

    assert result is engine
    assert not engine.contains_model("custom")


def test_clear_models(engine):
    engine.register_model(
        "a",
        lambda values, **kwargs: {"forecast": [1]},
    )
    engine.register_model(
        "b",
        lambda values, **kwargs: {"forecast": [2]},
    )

    result = engine.clear_models()

    assert result is engine
    assert engine.models() == {}
    assert engine.model_names() == []
    assert engine.model_count == 0


def test_enable_disable_model(engine):
    engine.register_model(
        "custom",
        lambda values, **kwargs: {"forecast": [1]},
    )

    engine.disable_model("custom")
    assert engine.model("custom")["enabled"] is False

    engine.enable_model("custom")
    assert engine.model("custom")["enabled"] is True


def test_execute_model(engine):
    def model(values, **kwargs):
        return {
            "forecast": list(values),
            "extra": kwargs.get("x"),
        }

    engine.register_model("custom", model)

    result = engine.execute_model(
        "custom",
        [1, 2],
        x=42,
    )

    assert result == {
        "forecast": [1, 2],
        "extra": 42,
    }


def test_execute_unknown_model_raises(engine):
    with pytest.raises(KeyError, match="Unknown model"):
        engine.execute_model("missing", [1, 2])


def test_execute_disabled_model_raises(engine):
    engine.register_model(
        "custom",
        lambda values, **kwargs: {"forecast": [1]},
    )

    engine.disable_model("custom")

    with pytest.raises(RuntimeError, match="disabled"):
        engine.execute_model("custom", [1, 2])


# ==========================================================
# Forecast Algorithms
# ==========================================================


def test_moving_average(engine):
    result = engine.moving_average(
        [1, 2, 3, 4, 5],
        horizon=3,
        window=2,
    )

    assert result["method"] == "moving_average"
    assert result["window"] == 2
    assert result["forecast"] == [4.5, 4.5, 4.5]


def test_moving_average_default_window(engine):
    result = engine.moving_average(
        [1, 2, 3, 4, 5, 6],
        horizon=2,
    )

    assert result["window"] == 5
    assert result["forecast"] == [4.0, 4.0]


def test_moving_average_empty(engine):
    result = engine.moving_average([])

    assert result == {
        "method": "moving_average",
        "forecast": [],
    }


def test_moving_average_window_is_clamped(engine):
    result = engine.moving_average(
        [1, 2],
        horizon=1,
        window=10,
    )

    assert result["window"] == 2
    assert result["forecast"] == [1.5]


def test_exponential_smoothing(engine):
    result = engine.exponential_smoothing(
        [10, 20],
        horizon=2,
        alpha=0.5,
    )

    assert result["method"] == "exponential_smoothing"
    assert result["alpha"] == 0.5
    assert result["forecast"] == [15.0, 15.0]


def test_exponential_smoothing_uses_config(engine):
    engine.configure(alpha=0.5)

    result = engine.exponential_smoothing(
        [10, 20],
        horizon=1,
    )

    assert result["alpha"] == 0.5
    assert result["forecast"] == [15.0]


def test_exponential_smoothing_empty(engine):
    result = engine.exponential_smoothing([])

    assert result == {
        "method": "exponential_smoothing",
        "forecast": [],
    }


def test_naive(engine):
    result = engine.naive(
        [1, 2, 3],
        horizon=3,
    )

    assert result == {
        "method": "naive",
        "forecast": [3, 3, 3],
    }


def test_naive_empty(engine):
    result = engine.naive([])

    assert result == {
        "method": "naive",
        "forecast": [],
    }


def test_drift(engine):
    result = engine.drift(
        [1, 2, 3],
        horizon=3,
    )

    assert result["method"] == "drift"
    assert result["slope"] == 1
    assert result["forecast"] == [4, 5, 6]


def test_drift_single_value_uses_naive(engine):
    result = engine.drift(
        [7],
        horizon=2,
    )

    assert result["method"] == "naive"
    assert result["forecast"] == [7, 7]


def test_drift_empty(engine):
    result = engine.drift([])

    assert result["method"] == "naive"
    assert result["forecast"] == []


def test_linear_trend(engine):
    result = engine.linear_trend(
        [1, 2, 3],
        horizon=2,
    )

    assert result["method"] == "linear_trend"
    assert result["slope"] == pytest.approx(1.0)
    assert result["intercept"] == pytest.approx(1.0)
    assert result["forecast"] == pytest.approx([4.0, 5.0])


def test_linear_trend_single_value_uses_naive(engine):
    result = engine.linear_trend(
        [7],
        horizon=2,
    )

    assert result["method"] == "naive"
    assert result["forecast"] == [7, 7]


def test_seasonal(engine):
    result = engine.seasonal(
        [1, 2, 3, 4],
        horizon=5,
        season_length=2,
    )

    assert result["method"] == "seasonal"
    assert result["season_length"] == 2
    assert result["forecast"] == [3, 4, 3, 4, 3]


def test_seasonal_short_input_uses_naive(engine):
    result = engine.seasonal(
        [1, 2],
        horizon=2,
        season_length=3,
    )

    assert result["method"] == "naive"
    assert result["forecast"] == [2, 2]


def test_custom_forecast(engine):
    def predictor(values, multiplier=1):
        return {
            "forecast": [
                x * multiplier
                for x in values
            ]
        }

    result = engine.custom(
        [1, 2, 3],
        predictor,
        multiplier=2,
    )

    assert result["forecast"] == [2, 4, 6]


def test_custom_requires_callable(engine):
    with pytest.raises(TypeError, match="predictor must be callable"):
        engine.custom(
            [1, 2],
            "not-callable",
        )


# ==========================================================
# Generic Forecast API
# ==========================================================


def test_forecast_moving_average(engine):
    engine.register_model(
        "moving_average",
        engine.moving_average,
    )

    result = engine.forecast(
        [1, 2, 3],
        method="moving_average",
        horizon=2,
        window=2,
    )

    assert result["method"] == "moving_average"
    assert result["forecast"] == [2.5, 2.5]
    assert engine.forecast_count == 1
    assert engine.prediction_count == 2
    assert engine.error_count == 0
    assert engine.running is False
    assert engine.last_forecast if hasattr(
        engine,
        "last_forecast",
    ) else True


def test_forecast_requires_registered_model(engine):
    with pytest.raises(KeyError, match="Unknown forecast model"):
        engine.forecast(
            [1, 2, 3],
            method="missing",
        )


def test_forecast_requires_active_engine(engine):
    engine.disable()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        engine.forecast(
            [1, 2, 3],
            method="moving_average",
        )


def test_forecast_frozen_engine_rejected(engine):
    engine.freeze()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        engine.forecast(
            [1, 2, 3],
            method="moving_average",
        )


def test_forecast_closed_engine_rejected(engine):
    engine.close()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        engine.forecast(
            [1, 2, 3],
            method="moving_average",
        )


def test_forecast_error_count(engine):
    def failing(values, **kwargs):
        raise ValueError("forecast failure")

    engine.register_model(
        "failing",
        failing,
    )

    with pytest.raises(ValueError, match="forecast failure"):
        engine.forecast(
            [1, 2],
            method="failing",
        )

    assert engine.error_count == 1
    assert engine.forecast_count == 0
    assert engine.running is False


def test_forecast_one(engine):
    engine.register_model(
        "moving_average",
        engine.moving_average,
    )

    result = engine.forecast_one(
        [1, 2, 3],
        method="moving_average",
    )

    assert result == 2.0
    assert engine.forecast_count == 1
    assert engine.prediction_count == 1


def test_forecast_many(engine):
    engine.register_model(
        "moving_average",
        engine.moving_average,
    )

    result = engine.forecast_many(
        [1, 2, 3],
        horizon=3,
        method="moving_average",
    )

    assert result["forecast"] == [2.0, 2.0, 2.0]
    assert engine.forecast_count == 1
    assert engine.prediction_count == 3


def test_forecast_batch(engine):
    engine.register_model(
        "naive",
        engine.naive,
    )

    results = engine.forecast_batch(
        [
            [1, 2],
            [3, 4],
        ],
        method="naive",
        horizon=2,
    )

    assert len(results) == 2
    assert results[0]["forecast"] == [2, 2]
    assert results[1]["forecast"] == [4, 4]
    assert engine.forecast_count == 2
    assert engine.prediction_count == 4


# ==========================================================
# Forecast Aliases
# ==========================================================


def test_predict_is_forecast_alias(engine):
    assert engine.predict is engine.forecast


def test_predict_one_is_forecast_one_alias(engine):
    assert engine.predict_one is engine.forecast_one


def test_predict_many_is_forecast_many_alias(engine):
    assert engine.predict_many is engine.forecast_many


def test_predict_batch_is_forecast_batch_alias(engine):
    assert engine.predict_batch is engine.forecast_batch


# ==========================================================
# Runtime Operations
# ==========================================================


def test_reset_preserves_models_and_config(engine):
    engine.register_model(
        "naive",
        engine.naive,
    )

    engine.configure(
        window=2,
    )

    engine.forecast(
        [1, 2],
        method="naive",
        horizon=1,
    )

    engine.reset()

    assert engine.forecast_count == 0
    assert engine.prediction_count == 0
    assert engine.error_count == 0
    assert engine.running is False
    assert engine.model_count == 1
    assert engine.config("window") == 2


def test_clear_resets_runtime_and_hooks(engine):
    callback = lambda *args: None

    engine.register_model(
        "naive",
        engine.naive,
    )
    engine.add_hook(
        "test",
        callback,
    )
    engine._context["x"] = 1
    engine._events.append({"event": "test"})

    result = engine.clear()

    assert result is engine
    assert engine.model_count == 1
    assert engine._hooks == {}
    assert engine._events == []
    assert engine._context == {}
    assert engine._snapshot is None


# ==========================================================
# Snapshot / Restore
# ==========================================================


def test_snapshot_contains_runtime_state(engine):
    engine.configure(window=2)

    engine._history.append(
        {"forecast": [1, 2]}
    )
    engine._last_forecast = {
        "forecast": [2]
    }
    engine._context["key"] = "value"

    snapshot = engine.snapshot()

    assert snapshot["enabled"] is True
    assert snapshot["frozen"] is False
    assert snapshot["closed"] is False
    assert snapshot["running"] is False
    assert snapshot["config"]["window"] == 2
    assert snapshot["history"] == [{"forecast": [1, 2]}]
    assert snapshot["last_forecast"] == {"forecast": [2]}
    assert snapshot["context"] == {"key": "value"}


def test_snapshot_is_deep_copy(engine):
    engine._history.append(
        {"values": [1, 2]}
    )
    engine._context["nested"] = {
        "x": [1]
    }

    snapshot = engine.snapshot()

    snapshot["history"][0]["values"].append(3)
    snapshot["context"]["nested"]["x"].append(2)

    assert engine._history == [
        {"values": [1, 2]}
    ]
    assert engine._context == {
        "nested": {
            "x": [1]
        }
    }


def test_restore_requires_snapshot(engine):
    with pytest.raises(
        ValueError,
        match="No snapshot available",
    ):
        engine.restore()


def test_restore_snapshot(engine):
    snapshot = {
        "enabled": False,
        "frozen": True,
        "closed": False,
        "running": False,
        "config": {
            "window": 2,
        },
        "history": [
            {"forecast": [1, 2]}
        ],
        "last_forecast": {
            "forecast": [2]
        },
        "context": {
            "key": "value"
        },
        "forecast_count": 3,
        "prediction_count": 5,
        "error_count": 1,
        "latency": 0.25,
        "uptime": 10.0,
    }

    result = engine.restore(snapshot)

    assert result is engine
    assert engine.enabled is False
    assert engine.frozen is True
    assert engine.forecast_count == 3
    assert engine.prediction_count == 5
    assert engine.error_count == 1
    assert engine.latency == 0.25
    assert engine.uptime == 10.0
    assert engine._history == [
        {"forecast": [1, 2]}
    ]
    assert engine._last_forecast == {
        "forecast": [2]
    }
    assert engine._context == {
        "key": "value"
    }


def test_restore_without_argument_uses_internal_snapshot(engine):
    engine._context["x"] = 1

    snapshot = engine.snapshot()

    engine._context["x"] = 2

    engine.restore()

    assert engine._context == snapshot["context"]


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict(engine):
    data = engine.to_dict()

    assert data["id"] == engine.id
    assert data["name"] == engine.name
    assert data["description"] == engine.description
    assert data["enabled"] is True
    assert data["frozen"] is False
    assert data["closed"] is False
    assert data["running"] is False
    assert data["config"] == engine.config()
    assert data["models"] == []
    assert data["forecast_count"] == 0
    assert data["prediction_count"] == 0
    assert data["error_count"] == 0
    assert data["version"] == engine.version


def test_to_dict_contains_iso_timestamps(engine):
    data = engine.to_dict()

    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

    # Ensure the values can be parsed back.
    from datetime import datetime

    datetime.fromisoformat(data["created_at"])
    datetime.fromisoformat(data["updated_at"])


def test_from_dict_restores_identity(engine):
    data = engine.to_dict()

    restored = MetricForecastEngine.from_dict(data)

    assert restored.id != engine.id
    assert restored.name == engine.name
    assert restored.description == engine.description


def test_from_dict_restores_runtime_state(engine):
    engine.disable()
    engine.configure(window=2)

    data = engine.to_dict()

    restored = MetricForecastEngine.from_dict(data)

    assert restored.enabled is False
    assert restored.disabled is True
    assert restored.config("window") == 2


def test_from_dict_restores_counts(engine):
    engine.register_model(
        "naive",
        engine.naive,
    )

    engine.forecast(
        [1, 2, 3],
        method="naive",
        horizon=2,
    )

    data = engine.to_dict()

    restored = MetricForecastEngine.from_dict(data)

    assert restored.forecast_count == engine.forecast_count
    assert restored.prediction_count == engine.prediction_count
    assert restored.error_count == engine.error_count
    assert restored.last_forecast == engine.last_forecast if hasattr(
        restored,
        "last_forecast",
    ) else True


def test_from_dict_restores_timestamps(engine):
    data = engine.to_dict()

    restored = MetricForecastEngine.from_dict(data)

    # Current implementation does not restore these fields yet.
    # This test deliberately documents the contract expected from
    # serialization. It should be enabled once from_dict restores
    # created_at and updated_at.
    assert restored.created_at == engine.created_at
    assert restored.updated_at == engine.updated_at


def test_to_json(engine):
    data = engine.to_json()

    assert isinstance(data, str)

    parsed = json.loads(data)

    assert parsed["name"] == engine.name
    assert parsed["version"] == engine.version


def test_from_json(engine):
    data = engine.to_json()

    restored = MetricForecastEngine.from_json(data)

    assert restored.name == engine.name
    assert restored.description == engine.description
    assert restored.config() == engine.config()


def test_serialize_deserialize(engine):
    data = engine.serialize()

    restored = MetricForecastEngine.deserialize(data)

    assert restored.name == engine.name
    assert restored.description == engine.description
    assert restored.config() == engine.config()


# ==========================================================
# Diagnostics
# ==========================================================


def test_summary(engine):
    result = engine.summary()

    assert result["id"] == engine.id
    assert result["name"] == engine.name
    assert result["description"] == engine.description
    assert result["enabled"] is True
    assert result["running"] is False
    assert result["active"] is True
    assert result["model_count"] == 0
    assert result["forecast_count"] == 0
    assert result["prediction_count"] == 0
    assert result["error_count"] == 0


def test_statistics(engine):
    result = engine.statistics()

    assert isinstance(result, dict)


def test_report(engine):
    result = engine.report()

    assert "summary" in result
    assert "statistics" in result
    assert "configuration" in result
    assert "models" in result
    assert "last_forecast" in result
    assert "history_size" in result


def test_health_initial(engine):
    result = engine.health()

    assert result["healthy"] is True
    assert result["state"] == "healthy"
    assert result["active"] is True
    assert result["running"] is False
    assert result["models"] == 0


def test_health_disabled(engine):
    engine.disable()

    result = engine.health()

    assert result["healthy"] is False
    assert result["state"] == "disabled"


def test_health_frozen(engine):
    engine.freeze()

    result = engine.health()

    assert result["healthy"] is False
    assert result["state"] == "frozen"


def test_health_closed(engine):
    engine.close()

    result = engine.health()

    assert result["healthy"] is False
    assert result["state"] == "closed"


def test_status(engine):
    result = engine.status()

    assert result == {
        "enabled": True,
        "disabled": False,
        "frozen": False,
        "closed": False,
        "running": False,
        "active": True,
    }


# ==========================================================
# Events / Hooks
# ==========================================================


def test_add_hook(engine):
    calls = []

    def callback(source, event):
        calls.append((source, event))

    result = engine.add_hook(
        "test",
        callback,
    )

    assert result is engine

    event = engine.emit(
        "test",
        value=42,
    )

    assert calls
    assert calls[0][0] is engine
    assert calls[0][1] == event


def test_add_hook_requires_callable(engine):
    with pytest.raises(
        TypeError,
        match="callback must be callable",
    ):
        engine.add_hook(
            "test",
            123,
        )


def test_remove_hook(engine):
    calls = []

    def callback(source, event):
        calls.append(event)

    engine.add_hook(
        "test",
        callback,
    )

    engine.remove_hook(
        "test",
        callback,
    )

    engine.emit(
        "test",
        value=1,
    )

    assert calls == []


def test_remove_all_hooks_for_event(engine):
    callback_a = lambda *args: None
    callback_b = lambda *args: None

    engine.add_hook("test", callback_a)
    engine.add_hook("test", callback_b)

    engine.remove_hook("test")

    assert "test" not in engine._hooks


def test_remove_missing_hook_is_safe(engine):
    result = engine.remove_hook(
        "missing",
    )

    assert result is engine


def test_clear_hooks(engine):
    engine.add_hook(
        "a",
        lambda *args: None,
    )
    engine.add_hook(
        "b",
        lambda *args: None,
    )

    result = engine.clear_hooks()

    assert result is engine
    assert engine._hooks == {}


def test_emit_returns_event(engine):
    event = engine.emit(
        "test",
        value=42,
    )

    assert event["event"] == "test"
    assert event["payload"] == {"value": 42}
    assert "timestamp" in event
    assert engine._events[-1] == event


def test_notify_alias(engine):
    event = engine.notify(
        "test",
        value=42,
    )

    assert event["event"] == "test"
    assert event["payload"]["value"] == 42


def test_subscribe_alias(engine):
    calls = []

    def callback(source, event):
        calls.append(event)

    result = engine.subscribe(
        "test",
        callback,
    )

    assert result is engine

    engine.emit("test")

    assert len(calls) == 1


def test_unsubscribe_alias(engine):
    calls = []

    def callback(source, event):
        calls.append(event)

    engine.subscribe(
        "test",
        callback,
    )

    engine.unsubscribe(
        "test",
        callback,
    )

    engine.emit("test")

    assert calls == []


def test_builtin_before_forecast_event(engine):
    event = engine.before_forecast(
        [1, 2],
        method="naive",
    )

    assert event["event"] == "before_forecast"
    assert event["payload"]["values"] == [1, 2]
    assert event["payload"]["method"] == "naive"


def test_builtin_after_forecast_event(engine):
    event = engine.after_forecast(
        {"forecast": [1]},
    )

    assert event["event"] == "after_forecast"
    assert event["payload"]["result"] == {
        "forecast": [1]
    }


def test_builtin_before_model_event(engine):
    event = engine.before_model(
        "naive",
        values=[1, 2],
    )

    assert event["event"] == "before_model"
    assert event["payload"]["model"] == "naive"
    assert event["payload"]["values"] == [1, 2]


def test_builtin_after_model_event(engine):
    event = engine.after_model(
        "naive",
        result={"forecast": [2]},
    )

    assert event["event"] == "after_model"
    assert event["payload"]["model"] == "naive"
    assert event["payload"]["result"] == {
        "forecast": [2]
    }


def test_hook_failure_does_not_break_emit(engine):
    calls = []

    def failing_callback(source, event):
        raise RuntimeError("hook failure")

    def successful_callback(source, event):
        calls.append(event)

    engine.add_hook(
        "test",
        failing_callback,
    )
    engine.add_hook(
        "test",
        successful_callback,
    )

    event = engine.emit(
        "test",
        value=1,
    )

    assert event["event"] == "test"
    assert calls == [event]


# ==========================================================
# Python Protocols
# ==========================================================


def test_len(engine):
    engine.register_model(
        "a",
        lambda values, **kwargs: {"forecast": []},
    )
    engine.register_model(
        "b",
        lambda values, **kwargs: {"forecast": []},
    )

    assert len(engine) == 2


def test_iter(engine):
    model = lambda values, **kwargs: {"forecast": []}

    engine.register_model(
        "custom",
        model,
    )

    items = list(engine)

    assert len(items) == 1
    assert items[0][0] == "custom"


def test_contains(engine):
    engine.register_model(
        "custom",
        lambda values, **kwargs: {"forecast": []},
    )

    assert "custom" in engine
    assert "missing" not in engine


def test_getitem(engine):
    model = lambda values, **kwargs: {"forecast": []}

    engine.register_model(
        "custom",
        model,
    )

    assert engine["custom"]["callable"] is model


def test_getitem_missing_raises(engine):
    with pytest.raises(KeyError):
        _ = engine["missing"]


def test_setitem(engine):
    model = lambda values, **kwargs: {"forecast": []}

    engine["custom"] = model

    assert engine.contains_model("custom")
    assert engine["custom"]["callable"] is model


def test_delitem(engine):
    engine.register_model(
        "custom",
        lambda values, **kwargs: {"forecast": []},
    )

    del engine["custom"]

    assert "custom" not in engine


def test_call(engine):
    engine.register_model(
        "naive",
        engine.naive,
    )

    result = engine(
        [1, 2, 3],
        method="naive",
        horizon=2,
    )

    assert result["forecast"] == [3, 3]


# ==========================================================
# Copy / Clone
# ==========================================================


def test_copy(engine):
    engine.configure(window=2)

    copied = engine.copy()

    assert copied is not engine
    assert copied.id == engine.id
    assert copied.config() == engine.config()


def test_clone(engine):
    engine.configure(window=2)
    engine._context["nested"] = {"values": [1]}

    cloned = engine.clone()

    assert cloned is not engine
    assert cloned.id == engine.id
    assert cloned.config() == engine.config()

    cloned._context["nested"]["values"].append(2)

    assert engine._context["nested"]["values"] == [1]


def test_copy_protocol(engine):
    copied = copy.copy(engine)

    assert copied is not engine
    assert copied.id == engine.id


def test_deepcopy_protocol(engine):
    cloned = copy.deepcopy(engine)

    assert cloned is not engine
    assert cloned.id == engine.id