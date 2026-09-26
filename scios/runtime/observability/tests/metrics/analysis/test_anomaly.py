"""
SciOS-NG Runtime Metrics Analysis
=================================

Tests for MetricAnomalyDetector.

File
----
scios/runtime/observability/tests/metrics/analysis/test_anomaly.py
"""

from __future__ import annotations

import json

import pytest

from scios.runtime.observability.metrics.analysis import (
    MetricAnomalyDetector,
)


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def detector() -> MetricAnomalyDetector:
    return MetricAnomalyDetector(
        name="TestAnomalyDetector",
        description="Test detector",
    )


@pytest.fixture
def builtin_detector(
    detector: MetricAnomalyDetector,
) -> MetricAnomalyDetector:

    detector.register_detector(
        "threshold",
        detector.threshold,
    )

    detector.register_detector(
        "zscore",
        detector.zscore,
    )

    detector.register_detector(
        "modified_zscore",
        detector.modified_zscore,
    )

    detector.register_detector(
        "iqr",
        detector.iqr,
    )

    detector.register_detector(
        "sigma",
        detector.sigma,
    )

    detector.register_detector(
        "moving_average",
        detector.moving_average,
    )

    detector.register_detector(
        "rolling",
        detector.rolling,
    )

    detector.register_detector(
        "custom",
        detector.custom,
    )

    return detector


# ==========================================================
# Part 1. Construction
# ==========================================================


def test_default_construction() -> None:
    detector = MetricAnomalyDetector()

    assert detector.name == "MetricAnomalyDetector"
    assert detector.description == ""
    assert detector.enabled is True
    assert detector.disabled is False
    assert detector.frozen is False
    assert detector.closed is False
    assert detector.active is True
    assert detector.version == "0.2.0"


def test_custom_construction() -> None:
    detector = MetricAnomalyDetector(
        name="CustomDetector",
        description="Example",
    )

    assert detector.name == "CustomDetector"
    assert detector.description == "Example"


def test_identity_is_unique() -> None:
    first = MetricAnomalyDetector()
    second = MetricAnomalyDetector()

    assert first.id != second.id


# ==========================================================
# Part 2. Threshold Configuration
# ==========================================================


def test_default_thresholds(
    detector: MetricAnomalyDetector,
) -> None:

    thresholds = detector.thresholds()

    assert thresholds == {
        "warning": 0.80,
        "critical": 0.95,
        "zscore": 3.0,
        "mad": 3.5,
        "iqr": 1.5,
        "sigma": 3.0,
    }


def test_threshold_lookup(
    detector: MetricAnomalyDetector,
) -> None:

    assert detector.threshold_value("zscore") == 3.0
    assert detector.threshold_value("missing") is None
    assert detector.threshold_value("missing", 10.0) == 10.0


def test_set_threshold(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.set_threshold(
        "zscore",
        4.5,
    )

    assert result is detector
    assert detector.threshold_value("zscore") == 4.5


def test_set_threshold_converts_to_float(
    detector: MetricAnomalyDetector,
) -> None:

    detector.set_threshold(
        "sigma",
        4,
    )

    value = detector.threshold_value("sigma")

    assert value == 4.0
    assert isinstance(value, float)


def test_thresholds_returns_copy(
    detector: MetricAnomalyDetector,
) -> None:

    thresholds = detector.thresholds()

    thresholds["zscore"] = 999.0

    assert detector.threshold_value("zscore") == 3.0


# ==========================================================
# Part 3. Detector Registry
# ==========================================================


def test_detector_registry(
    detector: MetricAnomalyDetector,
) -> None:

    def custom(values):
        return {"anomalies": []}

    result = detector.register_detector(
        "custom",
        custom,
    )

    assert result is detector
    assert detector.detector("custom") is custom
    assert "custom" in detector.detectors()


def test_register_detector_requires_callable(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(TypeError):
        detector.register_detector(
            "invalid",
            "not callable",
        )


def test_unregister_detector(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_detector(
        "custom",
        lambda values: {"anomalies": []},
    )

    result = detector.unregister_detector(
        "custom",
    )

    assert result is detector
    assert detector.detector("custom") is None


def test_unregister_missing_detector(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.unregister_detector(
        "missing",
    )

    assert result is detector


def test_detectors_returns_copy(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_detector(
        "custom",
        lambda values: {"anomalies": []},
    )

    detectors = detector.detectors()

    detectors.clear()

    assert detector.detector("custom") is not None


# ==========================================================
# Part 4. Threshold Algorithm
# ==========================================================


def test_threshold_detection(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.threshold(
        [0.1, 0.5, 0.8, 0.9],
        threshold=0.8,
    )

    assert result["method"] == "threshold"
    assert result["threshold"] == 0.8
    assert len(result["anomalies"]) == 2

    assert result["anomalies"][0]["index"] == 2
    assert result["anomalies"][0]["value"] == 0.8

    assert result["anomalies"][1]["index"] == 3
    assert result["anomalies"][1]["value"] == 0.9


def test_threshold_absolute_mode(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.threshold(
        [-5.0, -1.0, 1.0, 5.0],
        threshold=4.0,
        absolute=True,
    )

    assert len(result["anomalies"]) == 2
    assert result["anomalies"][0]["value"] == -5.0
    assert result["anomalies"][1]["value"] == 5.0


def test_threshold_uses_warning_threshold(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.threshold(
        [0.79, 0.80, 0.81],
    )

    assert result["threshold"] == 0.80
    assert len(result["anomalies"]) == 2


# ==========================================================
# Part 5. Z-score
# ==========================================================


def test_zscore_without_anomaly(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.zscore(
        [1, 2, 3, 4, 5],
        threshold=3.0,
    )

    assert result["method"] == "zscore"
    assert result["anomalies"] == []


def test_zscore_detects_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.zscore(
        [10, 10, 10, 10, 100],
        threshold=1.5,
    )

    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["index"] == 4
    assert result["anomalies"][0]["value"] == 100


def test_zscore_short_input(
    detector: MetricAnomalyDetector,
) -> None:

    assert detector.zscore([])["anomalies"] == []
    assert detector.zscore([1])["anomalies"] == []


def test_zscore_constant_values(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.zscore(
        [5, 5, 5, 5],
    )

    assert result["anomalies"] == []


# ==========================================================
# Part 6. Modified Z-score
# ==========================================================


def test_modified_zscore_zero_mad(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.modified_zscore(
        [10, 10, 10, 10, 100],
        threshold=2.0,
    )

    assert result["method"] == "modified_zscore"
    assert result["median"] == 10.0
    assert result["mad"] == 0.0
    assert result["anomalies"] == []


def test_modified_zscore_empty(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.modified_zscore([])

    assert result["method"] == "modified_zscore"
    assert result["anomalies"] == []


def test_modified_zscore_detects_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    values = [
        10,
        11,
        10,
        9,
        10,
        50,
    ]

    result = detector.modified_zscore(
        values,
        threshold=3.0,
    )

    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["index"] == 5
    assert result["anomalies"][0]["value"] == 50


# ==========================================================
# Part 7. IQR
# ==========================================================


def test_iqr_without_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.iqr(
        [1, 2, 3, 4, 5],
    )

    assert result["method"] == "iqr"
    assert result["anomalies"] == []


def test_iqr_detects_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.iqr(
        [1, 2, 3, 4, 5, 100],
        factor=1.5,
    )

    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["index"] == 5
    assert result["anomalies"][0]["value"] == 100


def test_iqr_bounds_are_returned(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.iqr(
        [1, 2, 3, 4, 5],
    )

    assert "lower" in result
    assert "upper" in result
    assert result["lower"] < result["upper"]


# ==========================================================
# Part 8. Sigma
# ==========================================================


def test_sigma_without_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.sigma(
        [1, 2, 3, 4, 5],
        sigma=3.0,
    )

    assert result["method"] == "sigma"
    assert result["anomalies"] == []


def test_sigma_detects_outlier(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.sigma(
        [10, 10, 10, 10, 100],
        sigma=1.0,
    )

    assert len(result["anomalies"]) >= 1


def test_sigma_returns_bounds(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.sigma(
        [1, 2, 3, 4, 5],
    )

    assert "lower" in result
    assert "upper" in result
    assert result["lower"] < result["upper"]


# ==========================================================
# Part 9. Moving Average
# ==========================================================


def test_moving_average(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.moving_average(
        [1, 1, 1, 10, 1],
        window=3,
        threshold=2.0,
    )

    assert result["method"] == "moving_average"
    assert result["window"] == 3


def test_moving_average_short_input(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.moving_average(
        [1, 2, 3],
        window=5,
    )

    assert result["anomalies"] == []


def test_moving_average_detects_deviation(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.moving_average(
        [1, 1, 1, 10, 1, 1],
        window=3,
        threshold=2.0,
    )

    assert any(
        item["value"] == 10
        for item in result["anomalies"]
    )


# ==========================================================
# Part 10. Rolling Detection
# ==========================================================


def test_rolling_short_input(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.rolling(
        [1, 2, 3],
        window=10,
    )

    assert result["method"] == "rolling"
    assert result["anomalies"] == []


def test_rolling_uses_selected_detector(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.rolling(
        [1, 2, 3, 100],
        window=3,
        detector="zscore",
    )

    assert result["method"] == "rolling"
    assert result["window"] == 3
    assert result["detector"] == "zscore"


def test_rolling_rejects_unknown_detector(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(ValueError):
        detector.rolling(
            [1, 2, 3, 4],
            window=3,
            detector="missing",
        )


# ==========================================================
# Part 11. Custom Detector
# ==========================================================


def test_custom_detector(
    detector: MetricAnomalyDetector,
) -> None:

    def custom(values, limit=10):
        return {
            "method": "custom",
            "anomalies": [
                {
                    "index": index,
                    "value": value,
                }
                for index, value in enumerate(values)
                if value > limit
            ],
        }

    result = detector.custom(
        [1, 5, 20],
        custom,
        limit=10,
    )

    assert result["method"] == "custom"
    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["value"] == 20


def test_custom_detector_requires_callable(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(TypeError):
        detector.custom(
            [1, 2, 3],
            "invalid",
        )


# ==========================================================
# Part 12. Generic Detection API
# ==========================================================


def test_detect_requires_registered_detector(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(
        KeyError,
        match="Unknown detector",
    ):
        detector.detect(
            [1, 2, 3],
            method="not_registered",
        )


def test_detect(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect(
        [1, 2, 3, 100],
        method="zscore",
        threshold=1.0,
    )

    assert result["method"] == "zscore"
    assert builtin_detector.detection_count == 1
    assert builtin_detector.last_result == result


def test_detect_many(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect_many(
        [1, 2, 3],
        method="zscore",
    )

    assert result["method"] == "zscore"
    assert builtin_detector.detection_count == 1


def test_detect_one(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect_one(
        10,
        method="threshold",
        threshold=5,
    )

    assert result is not None
    assert result["value"] == 10


def test_detect_one_without_anomaly(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect_one(
        1,
        method="threshold",
        threshold=5,
    )

    assert result is None


def test_detect_batch(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect_batch(
        [
            [1, 2, 3],
            [10, 20, 30],
        ],
        method="zscore",
    )

    assert len(result) == 2
    assert builtin_detector.detection_count == 2


# ==========================================================
# Part 13. Detection Counters / History
# ==========================================================


def test_detection_counter(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    assert builtin_detector.detection_count == 0

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    assert builtin_detector.detection_count == 1


def test_history_is_updated(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    assert len(builtin_detector._history) == 1
    assert builtin_detector.last_result is not None


def test_error_does_not_increment_detection_count(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(KeyError):
        detector.detect(
            [1, 2, 3],
            method="missing",
        )

    assert detector.detection_count == 0


# ==========================================================
# Part 14. Rule Management
# ==========================================================


def test_register_rule(
    detector: MetricAnomalyDetector,
) -> None:

    def rule(values):
        return {"anomalies": []}

    result = detector.register_rule(
        "test",
        rule,
    )

    assert result is detector
    assert detector.contains_rule("test")
    assert detector.rule("test") is not None


def test_register_rule_requires_callable(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(TypeError):
        detector.register_rule(
            "invalid",
            "not callable",
        )


def test_rule_count(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "one",
        lambda values: {"anomalies": []},
    )

    detector.register_rule(
        "two",
        lambda values: {"anomalies": []},
    )

    assert detector.rule_count() == 2
    assert detector.rule_names() == [
        "one",
        "two",
    ]


def test_rule_execution(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "high",
        lambda values: {
            "anomalies": [
                value
                for value in values
                if value > 10
            ],
        },
    )

    result = detector.execute_rule(
        "high",
        [1, 20, 3],
    )

    assert result["anomalies"] == [20]


def test_unknown_rule_raises(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(KeyError):
        detector.execute_rule(
            "missing",
            [1, 2, 3],
        )


def test_disable_rule(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "test",
        lambda values: {
            "anomalies": [1],
        },
    )

    detector.disable_rule("test")

    result = detector.execute_rule(
        "test",
        [1, 2, 3],
    )

    assert result["enabled"] is False
    assert result["anomalies"] == []


def test_enable_rule(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "test",
        lambda values: {
            "anomalies": [1],
        },
        enabled=False,
    )

    detector.enable_rule("test")

    result = detector.execute_rule(
        "test",
        [1, 2, 3],
    )

    assert result["anomalies"] == [1]


def test_remove_rule(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "test",
        lambda values: {"anomalies": []},
    )

    removed = detector.remove_rule("test")

    assert removed is not None
    assert detector.contains_rule("test") is False


def test_clear_rules(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "one",
        lambda values: {"anomalies": []},
    )

    detector.register_rule(
        "two",
        lambda values: {"anomalies": []},
    )

    result = detector.clear_rules()

    assert result is detector
    assert detector.rule_count() == 0


# ==========================================================
# Part 15. Lifecycle
# ==========================================================


def test_disable(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.disable()

    assert result is detector
    assert detector.enabled is False
    assert detector.disabled is True
    assert detector.active is False


def test_enable(
    detector: MetricAnomalyDetector,
) -> None:

    detector.disable()

    result = detector.enable()

    assert result is detector
    assert detector.enabled is True
    assert detector.active is True


def test_freeze(
    detector: MetricAnomalyDetector,
) -> None:

    detector.freeze()

    assert detector.frozen is True
    assert detector.active is False


def test_unfreeze(
    detector: MetricAnomalyDetector,
) -> None:

    detector.freeze()
    detector.unfreeze()

    assert detector.frozen is False
    assert detector.active is True


def test_close(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.close()

    assert result is detector
    assert detector.closed is True
    assert detector.enabled is False
    assert detector.active is False


def test_reopen(
    detector: MetricAnomalyDetector,
) -> None:

    detector.close()

    result = detector.reopen()

    assert result is detector
    assert detector.closed is False
    assert detector.enabled is True
    assert detector.frozen is False
    assert detector.active is True


def test_detect_rejected_when_disabled(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.disable()

    with pytest.raises(RuntimeError):
        builtin_detector.detect(
            [1, 2, 3],
            method="zscore",
        )


def test_detect_rejected_when_frozen(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.freeze()

    with pytest.raises(RuntimeError):
        builtin_detector.detect(
            [1, 2, 3],
            method="zscore",
        )


def test_detect_rejected_when_closed(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.close()

    with pytest.raises(RuntimeError):
        builtin_detector.detect(
            [1, 2, 3],
            method="zscore",
        )


# ==========================================================
# Part 16. Hooks / Events
# ==========================================================


def test_add_hook(
    detector: MetricAnomalyDetector,
) -> None:

    calls = []

    def callback(instance, event_data):
        calls.append(
            (instance, event_data)
        )

    result = detector.add_hook(
        "before_detect",
        callback,
    )

    assert result is detector


def test_add_hook_requires_callable(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(TypeError):
        detector.add_hook(
            "event",
            "invalid",
        )


def test_remove_hook(
    detector: MetricAnomalyDetector,
) -> None:

    callback = (
        lambda instance, event_data: None
    )

    detector.add_hook(
        "event",
        callback,
    )

    result = detector.remove_hook(
        "event",
        callback,
    )

    assert result is detector


def test_emit(
    detector: MetricAnomalyDetector,
) -> None:

    calls = []

    def callback(instance, event_data):
        calls.append(event_data)

    detector.add_hook(
        "test",
        callback,
    )

    result = detector.emit(
        "test",
        value=10,
    )

    assert result["event"] == "test"
    assert result["payload"]["value"] == 10
    assert len(calls) == 1
    assert calls[0]["payload"]["value"] == 10


def test_subscribe_alias(
    detector: MetricAnomalyDetector,
) -> None:

    callback = (
        lambda instance, event_data: None
    )

    result = detector.subscribe(
        "test",
        callback,
    )

    assert result is detector


def test_unsubscribe(
    detector: MetricAnomalyDetector,
) -> None:

    callback = (
        lambda instance, event_data: None
    )

    detector.subscribe(
        "test",
        callback,
    )

    result = detector.unsubscribe(
        "test",
        callback,
    )

    assert result is detector


# ==========================================================
# Part 17. Summary / Health / Status
# ==========================================================


def test_summary(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.summary()

    assert result["id"] == detector.id
    assert result["name"] == detector.name
    assert result["enabled"] is True
    assert result["active"] is True
    assert result["rule_count"] == 0
    assert result["detector_count"] == 0


def test_health(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.health()

    assert result["healthy"] is True
    assert result["state"] == "healthy"
    assert result["active"] is True
    assert result["enabled"] is True


def test_health_disabled(
    detector: MetricAnomalyDetector,
) -> None:

    detector.disable()

    result = detector.health()

    assert result["healthy"] is False
    assert result["state"] == "disabled"


def test_health_frozen(
    detector: MetricAnomalyDetector,
) -> None:

    detector.freeze()

    result = detector.health()

    assert result["healthy"] is False
    assert result["state"] == "frozen"


def test_health_closed(
    detector: MetricAnomalyDetector,
) -> None:

    detector.close()

    result = detector.health()

    assert result["healthy"] is False
    assert result["state"] == "closed"


def test_status(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.status()

    assert result["enabled"] is True
    assert result["disabled"] is False
    assert result["frozen"] is False
    assert result["closed"] is False
    assert result["active"] is True


# ==========================================================
# Part 18. Serialization
# ==========================================================


def test_to_dict(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.to_dict()

    assert result["id"] == builtin_detector.id
    assert result["name"] == builtin_detector.name
    assert result["description"] == builtin_detector.description
    assert "thresholds" in result
    assert "rules" in result
    assert "detectors" in result
    assert "history_size" in result
    assert "last_result" in result


def test_to_json(
    detector: MetricAnomalyDetector,
) -> None:

    text = detector.to_json()

    assert isinstance(text, str)

    data = json.loads(text)

    assert data["id"] == detector.id
    assert data["name"] == detector.name


def test_from_dict(
    detector: MetricAnomalyDetector,
) -> None:

    data = detector.to_dict()

    restored = MetricAnomalyDetector.from_dict(
        data
    )

    assert restored.id == detector.id
    assert restored.name == detector.name
    assert restored.description == detector.description


def test_from_json(
    detector: MetricAnomalyDetector,
) -> None:

    text = detector.to_json()

    restored = MetricAnomalyDetector.from_json(
        text
    )

    assert restored.id == detector.id
    assert restored.name == detector.name


def test_serialize_alias(
    detector: MetricAnomalyDetector,
) -> None:

    serialized = detector.serialize()

    assert isinstance(serialized, str)

    assert json.loads(
        serialized
    )["id"] == detector.id


def test_deserialize_json(
    detector: MetricAnomalyDetector,
) -> None:

    restored = MetricAnomalyDetector.deserialize(
        detector.to_json()
    )

    assert restored.id == detector.id


# ==========================================================
# Part 19. Snapshot / Restore
# ==========================================================


def test_snapshot(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    snapshot = builtin_detector.snapshot()

    assert snapshot["id"] == builtin_detector.id
    assert snapshot["detection_count"] == 1


def test_restore(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    snapshot = builtin_detector.snapshot()

    builtin_detector.reset()
    builtin_detector.restore(snapshot)

    assert builtin_detector.detection_count == 1


def test_restore_without_snapshot_raises(
    detector: MetricAnomalyDetector,
) -> None:

    with pytest.raises(ValueError):
        detector.restore()


# ==========================================================
# Part 20. Reset / Clear
# ==========================================================


def test_reset(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    builtin_detector.reset()

    assert builtin_detector.detection_count == 0
    assert builtin_detector.anomaly_count == 0
    assert builtin_detector._history == []
    assert builtin_detector._last_result is None


def test_reset_preserves_configuration(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.set_threshold(
        "zscore",
        4.0,
    )

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    builtin_detector.reset()

    assert (
        builtin_detector.threshold_value("zscore")
        == 4.0
    )

    assert builtin_detector.detector(
        "zscore"
    ) is not None


def test_clear(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.detect(
        [1, 2, 3],
        method="zscore",
    )

    result = builtin_detector.clear()

    assert result is builtin_detector
    assert builtin_detector._history == []
    assert builtin_detector._last_result is None


# ==========================================================
# Part 21. Clone / Copy
# ==========================================================


def test_clone(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    builtin_detector.set_threshold(
        "zscore",
        4.0,
    )

    clone = builtin_detector.clone()

    assert isinstance(
        clone,
        MetricAnomalyDetector,
    )

    assert clone is not builtin_detector
    assert clone.id == builtin_detector.id
    assert clone.name == builtin_detector.name
    assert clone.threshold_value(
        "zscore"
    ) == 4.0


def test_copy(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    copied = builtin_detector.copy()

    assert isinstance(
        copied,
        MetricAnomalyDetector,
    )

    assert copied is not builtin_detector
    assert copied.id == builtin_detector.id


# ==========================================================
# Part 22. Protocols
# ==========================================================


def test_repr(
    detector: MetricAnomalyDetector,
) -> None:

    text = repr(detector)

    assert "MetricAnomalyDetector" in text
    assert detector.id in text


def test_str(
    detector: MetricAnomalyDetector,
) -> None:

    text = str(detector)

    assert detector.name in text
    assert "active=" in text


def test_len(
    detector: MetricAnomalyDetector,
) -> None:

    assert len(detector) == 0

    detector.register_rule(
        "test",
        lambda values: {"anomalies": []},
    )

    assert len(detector) == 1


def test_contains(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "test",
        lambda values: {"anomalies": []},
    )

    assert "test" in detector
    assert "missing" not in detector


def test_iteration(
    detector: MetricAnomalyDetector,
) -> None:

    detector.register_rule(
        "test",
        lambda values: {"anomalies": []},
    )

    items = list(detector)

    assert len(items) == 1
    assert items[0][0] == "test"


def test_callable(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector(
        [1, 2, 3],
        method="zscore",
    )

    assert result["method"] == "zscore"


def test_context_is_dictionary(
    detector: MetricAnomalyDetector,
) -> None:

    assert isinstance(
        detector._context,
        dict,
    )


# ==========================================================
# Part 23. Statistical Integration
# ==========================================================


def test_statistics_property(
    detector: MetricAnomalyDetector,
) -> None:

    stats = detector.statistics

    assert stats is not None
    assert hasattr(stats, "mean")
    assert hasattr(stats, "std")


def test_anomaly_count_tracks_results(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    result = builtin_detector.detect(
        [1, 1, 1, 100],
        method="zscore",
        threshold=1.0,
    )

    assert (
        builtin_detector.anomaly_count
        == len(result["anomalies"])
    )


# ==========================================================
# Part 24. Invariants
# ==========================================================


def test_detection_does_not_mutate_input(
    builtin_detector: MetricAnomalyDetector,
) -> None:

    values = [1, 2, 3, 100]
    original = values.copy()

    builtin_detector.detect(
        values,
        method="zscore",
    )

    assert values == original


def test_threshold_does_not_mutate_input(
    detector: MetricAnomalyDetector,
) -> None:

    values = [1, 2, 3]

    detector.threshold(
        values,
        threshold=2,
    )

    assert values == [1, 2, 3]


def test_zscore_result_contains_required_fields(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.zscore(
        [1, 2, 3, 4, 5],
    )

    assert {
        "method",
        "mean",
        "std",
        "threshold",
        "anomalies",
    }.issubset(result.keys())


def test_iqr_result_contains_required_fields(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.iqr(
        [1, 2, 3, 4, 5],
    )

    assert {
        "method",
        "lower",
        "upper",
        "anomalies",
    }.issubset(result.keys())


def test_sigma_result_contains_required_fields(
    detector: MetricAnomalyDetector,
) -> None:

    result = detector.sigma(
        [1, 2, 3, 4, 5],
    )

    assert {
        "method",
        "lower",
        "upper",
        "anomalies",
    }.issubset(result.keys())