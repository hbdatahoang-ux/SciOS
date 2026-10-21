"""
Tests for MetricBottleneckDetector.

SciOS-NG Runtime Metrics Analysis
"""

from __future__ import annotations

import copy
import json

import pytest

from scios.runtime.observability.metrics.analysis.bottleneck import (
    MetricBottleneckDetector,
)


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def detector() -> MetricBottleneckDetector:
    return MetricBottleneckDetector()


@pytest.fixture
def registered_detector() -> MetricBottleneckDetector:
    detector = MetricBottleneckDetector()
    detector.register_builtin_algorithms()
    return detector


@pytest.fixture
def healthy_metrics() -> dict:
    return {
        "latency": 50.0,
        "throughput": 2000.0,
        "utilization": 0.50,
        "queue": 20,
        "contention": 0.25,
        "saturation": 0.50,
        "dependency_depth": 2,
    }


@pytest.fixture
def bottleneck_metrics() -> dict:
    return {
        "latency": 150.0,
        "throughput": 500.0,
        "utilization": 0.95,
        "queue": 150,
        "contention": 0.90,
        "saturation": 0.95,
        "dependency_depth": 10,
    }


# ======================================================================
# Part 1. Foundation / Identity
# ======================================================================


def test_default_identity(detector):
    assert detector.name == "MetricBottleneckDetector"
    assert detector.description == ""
    assert detector.version == "0.2.0"


def test_custom_identity():
    detector = MetricBottleneckDetector(
        name="CustomDetector",
        description="Test detector",
    )

    assert detector.name == "CustomDetector"
    assert detector.description == "Test detector"
    assert detector.version == "0.2.0"


def test_id_is_unique():
    first = MetricBottleneckDetector()
    second = MetricBottleneckDetector()

    assert isinstance(first.id, str)
    assert isinstance(second.id, str)
    assert first.id
    assert second.id
    assert first.id != second.id


# ======================================================================
# Part 2. Runtime State
# ======================================================================


def test_initial_runtime_state(detector):
    assert detector.enabled is True
    assert detector.disabled is False
    assert detector.frozen is False
    assert detector.closed is False
    assert detector.running is False
    assert detector.active is True


def test_disable_changes_runtime_state(detector):
    result = detector.disable()

    assert result is detector
    assert detector.enabled is False
    assert detector.disabled is True
    assert detector.running is False
    assert detector.active is False


def test_enable_changes_runtime_state(detector):
    detector.disable()

    result = detector.enable()

    assert result is detector
    assert detector.enabled is True
    assert detector.disabled is False
    assert detector.active is True


def test_freeze_changes_runtime_state(detector):
    result = detector.freeze()

    assert result is detector
    assert detector.frozen is True
    assert detector.active is False


def test_unfreeze_changes_runtime_state(detector):
    detector.freeze()

    result = detector.unfreeze()

    assert result is detector
    assert detector.frozen is False
    assert detector.active is True


def test_close_changes_runtime_state(detector):
    result = detector.close()

    assert result is detector
    assert detector.closed is True
    assert detector.running is False
    assert detector.active is False


def test_reopen_changes_runtime_state(detector):
    detector.close()

    result = detector.reopen()

    assert result is detector
    assert detector.closed is False
    assert detector.active is True


def test_disable_also_stops_running_state(detector):
    detector._running = True

    detector.disable()

    assert detector.running is False


def test_close_also_stops_running_state(detector):
    detector._running = True

    detector.close()

    assert detector.running is False


def test_detect_requires_active_detector(detector):
    detector.disable()

    with pytest.raises(RuntimeError, match="not active"):
        detector.detect(
            {"latency": 100},
            method="latency",
        )


def test_frozen_detector_cannot_detect(detector):
    detector.freeze()

    with pytest.raises(RuntimeError, match="not active"):
        detector.detect(
            {"latency": 100},
            method="latency",
        )


def test_closed_detector_cannot_detect(detector):
    detector.close()

    with pytest.raises(RuntimeError, match="not active"):
        detector.detect(
            {"latency": 100},
            method="latency",
        )


# ======================================================================
# Part 3. Configuration
# ======================================================================


def test_default_configuration(detector):
    assert detector.config == {
        "latency_threshold": 100.0,
        "throughput_threshold": 1000.0,
        "utilization_threshold": 0.80,
        "queue_threshold": 100,
        "contention_threshold": 0.75,
        "saturation_threshold": 0.90,
        "dependency_depth": 5,
    }


def test_config_returns_copy(detector):
    config = detector.config

    config["latency_threshold"] = 9999

    assert detector.config["latency_threshold"] == 100.0


def test_configure_updates_configuration(detector):
    result = detector.configure(
        latency_threshold=250.0,
        queue_threshold=200,
    )

    assert result is detector
    assert detector.config["latency_threshold"] == 250.0
    assert detector.config["queue_threshold"] == 200


def test_configure_preserves_unmodified_configuration(detector):
    detector.configure(
        latency_threshold=250.0,
    )

    assert detector.config["throughput_threshold"] == 1000.0
    assert detector.config["utilization_threshold"] == 0.80
    assert detector.config["queue_threshold"] == 100


def test_configuration_change_updates_timestamp(detector):
    before = detector.updated_at

    detector.configure(
        latency_threshold=200.0,
    )

    assert detector.updated_at >= before


# ======================================================================
# Part 4. Detection Algorithms - Contract
# ======================================================================


def test_latency_is_callable_algorithm(detector):
    """
    Regression guard.

    `latency` is the detection algorithm.
    Runtime latency statistic is exposed separately.
    """
    assert callable(detector.latency)


def test_latest_latency_is_statistic(detector):
    assert detector.latest_latency == 0.0


def test_latency_value_is_statistic(detector):
    assert detector.latency_value == 0.0


def test_latest_latency_and_latency_value_are_consistent(detector):
    assert detector.latest_latency == detector.latency_value


def test_throughput_is_callable(detector):
    assert callable(detector.throughput)


def test_utilization_is_callable(detector):
    assert callable(detector.utilization)


def test_queue_is_callable(detector):
    assert callable(detector.queue)


def test_contention_is_callable(detector):
    assert callable(detector.contention)


def test_saturation_is_callable(detector):
    assert callable(detector.saturation)


def test_dependency_is_callable(detector):
    assert callable(detector.dependency)


def test_pipeline_is_callable(detector):
    assert callable(detector.pipeline)


def test_custom_is_callable(detector):
    assert callable(detector.custom)


# ======================================================================
# Part 5. Latency Detection
# ======================================================================


def test_latency_below_threshold(detector):
    result = detector.latency(
        {"latency": 50},
    )

    assert result == {
        "algorithm": "latency",
        "metric": 50.0,
        "threshold": 100.0,
        "bottleneck": False,
        "severity": "normal",
    }


def test_latency_at_threshold(detector):
    result = detector.latency(
        {"latency": 100},
    )

    assert result["metric"] == 100.0
    assert result["threshold"] == 100.0
    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_latency_above_threshold(detector):
    result = detector.latency(
        {"latency": 150},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_latency_custom_threshold(detector):
    result = detector.latency(
        {"latency": 150},
        threshold=200,
    )

    assert result["threshold"] == 200
    assert result["bottleneck"] is False


def test_latency_missing_metric_defaults_to_zero(detector):
    result = detector.latency({})

    assert result["metric"] == 0.0
    assert result["bottleneck"] is False


# ======================================================================
# Part 6. Throughput Detection
# ======================================================================


def test_throughput_above_threshold_is_normal(detector):
    result = detector.throughput(
        {"throughput": 2000},
    )

    assert result == {
        "algorithm": "throughput",
        "metric": 2000.0,
        "threshold": 1000.0,
        "bottleneck": False,
        "severity": "normal",
    }


def test_throughput_at_threshold_is_bottleneck(detector):
    result = detector.throughput(
        {"throughput": 1000},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_throughput_below_threshold_is_bottleneck(detector):
    result = detector.throughput(
        {"throughput": 500},
    )

    assert result["metric"] == 500.0
    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_throughput_custom_threshold(detector):
    result = detector.throughput(
        {"throughput": 1500},
        threshold=1200,
    )

    assert result["threshold"] == 1200
    assert result["bottleneck"] is False


def test_throughput_missing_metric_defaults_to_zero(detector):
    result = detector.throughput({})

    assert result["metric"] == 0.0
    assert result["bottleneck"] is True


# ======================================================================
# Part 7. Utilization Detection
# ======================================================================


def test_utilization_below_threshold(detector):
    result = detector.utilization(
        {"utilization": 0.50},
    )

    assert result["metric"] == 0.50
    assert result["threshold"] == 0.80
    assert result["bottleneck"] is False
    assert result["severity"] == "normal"


def test_utilization_at_threshold(detector):
    result = detector.utilization(
        {"utilization": 0.80},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_utilization_above_threshold(detector):
    result = detector.utilization(
        {"utilization": 0.95},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_utilization_custom_threshold(detector):
    result = detector.utilization(
        {"utilization": 0.85},
        threshold=0.90,
    )

    assert result["threshold"] == 0.90
    assert result["bottleneck"] is False


# ======================================================================
# Part 8. Queue Detection
# ======================================================================


def test_queue_uses_canonical_queue_metric(detector):
    result = detector.queue(
        {"queue": 150},
    )

    assert result["metric"] == 150
    assert result["threshold"] == 100
    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_queue_at_threshold(detector):
    result = detector.queue(
        {"queue": 100},
    )

    assert result["metric"] == 100
    assert result["bottleneck"] is True


def test_queue_below_threshold(detector):
    result = detector.queue(
        {"queue": 20},
    )

    assert result["metric"] == 20
    assert result["bottleneck"] is False
    assert result["severity"] == "normal"


def test_queue_missing_metric_defaults_to_zero(detector):
    result = detector.queue({})

    assert result["metric"] == 0
    assert result["bottleneck"] is False


def test_queue_legacy_queue_size_is_supported_if_implemented(detector):
    result = detector.queue(
        {"queue_size": 150},
    )

    assert result["metric"] == 150
    assert result["bottleneck"] is True


def test_queue_custom_threshold(detector):
    result = detector.queue(
        {"queue": 150},
        threshold=200,
    )

    assert result["threshold"] == 200
    assert result["bottleneck"] is False


# ======================================================================
# Part 9. Contention Detection
# ======================================================================


def test_contention_below_threshold(detector):
    result = detector.contention(
        {"contention": 0.50},
    )

    assert result["metric"] == 0.50
    assert result["threshold"] == 0.75
    assert result["bottleneck"] is False
    assert result["severity"] == "normal"


def test_contention_at_threshold(detector):
    result = detector.contention(
        {"contention": 0.75},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_contention_above_threshold(detector):
    result = detector.contention(
        {"contention": 0.90},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_contention_custom_threshold(detector):
    result = detector.contention(
        {"contention": 0.80},
        threshold=0.90,
    )

    assert result["threshold"] == 0.90
    assert result["bottleneck"] is False


# ======================================================================
# Part 10. Saturation Detection
# ======================================================================


def test_saturation_below_threshold(detector):
    result = detector.saturation(
        {"saturation": 0.80},
    )

    assert result["metric"] == 0.80
    assert result["threshold"] == 0.90
    assert result["bottleneck"] is False
    assert result["severity"] == "normal"


def test_saturation_at_threshold(detector):
    result = detector.saturation(
        {"saturation": 0.90},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "critical"


def test_saturation_above_threshold(detector):
    result = detector.saturation(
        {"saturation": 0.95},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "critical"


def test_saturation_custom_threshold(detector):
    result = detector.saturation(
        {"saturation": 0.85},
        threshold=0.90,
    )

    assert result["threshold"] == 0.90
    assert result["bottleneck"] is False


# ======================================================================
# Part 11. Dependency Detection
# ======================================================================


def test_dependency_below_threshold(detector):
    result = detector.dependency(
        {"dependency_depth": 2},
    )

    assert result["metric"] == 2
    assert result["threshold"] == 5
    assert result["bottleneck"] is False
    assert result["severity"] == "normal"


def test_dependency_at_threshold(detector):
    result = detector.dependency(
        {"dependency_depth": 5},
    )

    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_dependency_above_threshold(detector):
    result = detector.dependency(
        {"dependency_depth": 10},
    )

    assert result["metric"] == 10
    assert result["bottleneck"] is True
    assert result["severity"] == "high"


def test_dependency_custom_threshold(detector):
    result = detector.dependency(
        {"dependency_depth": 8},
        threshold=10,
    )

    assert result["threshold"] == 10
    assert result["bottleneck"] is False


# ======================================================================
# Part 12. Pipeline Detection
# ======================================================================


def test_pipeline_returns_all_builtin_results(
    detector,
    healthy_metrics,
):
    result = detector.pipeline(
        healthy_metrics,
    )

    assert result["algorithm"] == "pipeline"
    assert result["bottleneck"] is False
    assert result["count"] == 0

    assert len(result["results"]) == 7

    assert [
        item["algorithm"]
        for item in result["results"]
    ] == [
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
    ]


def test_pipeline_detects_all_bottlenecks(
    detector,
    bottleneck_metrics,
):
    result = detector.pipeline(
        bottleneck_metrics,
    )

    assert result["algorithm"] == "pipeline"
    assert result["bottleneck"] is True
    assert result["count"] == 7
    assert len(result["results"]) == 7

    assert all(
        item["bottleneck"]
        for item in result["results"]
    )


def test_pipeline_detects_partial_bottlenecks(detector):
    result = detector.pipeline(
        {
            "latency": 150,
            "throughput": 2000,
            "utilization": 0.50,
            "queue": 20,
            "contention": 0.90,
            "saturation": 0.50,
            "dependency_depth": 2,
        }
    )

    assert result["bottleneck"] is True
    assert result["count"] == 2

    algorithms = [
        item["algorithm"]
        for item in result["results"]
        if item["bottleneck"]
    ]

    assert algorithms == [
        "latency",
        "contention",
    ]


def test_pipeline_does_not_require_registry(detector, healthy_metrics):
    result = detector.pipeline(
        healthy_metrics,
    )

    assert result["algorithm"] == "pipeline"
    assert len(result["results"]) == 7


# ======================================================================
# Part 13. Custom Detection
# ======================================================================


def test_custom_detector(detector):
    def custom(metrics):
        return {
            "algorithm": "custom-test",
            "metric": metrics["value"],
            "bottleneck": metrics["value"] > 10,
        }

    result = detector.custom(
        {"value": 20},
        custom,
    )

    assert result["algorithm"] == "custom-test"
    assert result["metric"] == 20
    assert result["bottleneck"] is True


def test_custom_detector_accepts_kwargs(detector):
    def custom(metrics, *, threshold):
        return {
            "metric": metrics["value"],
            "threshold": threshold,
            "bottleneck": metrics["value"] >= threshold,
        }

    result = detector.custom(
        {"value": 20},
        custom,
        threshold=15,
    )

    assert result["metric"] == 20
    assert result["threshold"] == 15
    assert result["bottleneck"] is True


def test_custom_detector_requires_callable(detector):
    with pytest.raises(
        TypeError,
        match="detector must be callable",
    ):
        detector.custom(
            {},
            object(),
        )


# ======================================================================
# Part 14. Registry
# ======================================================================


def test_registry_starts_empty(detector):
    assert detector.algorithms() == {}
    assert detector.algorithm_names() == []
    assert detector.algorithm_count == 0
    assert len(detector) == 0


def test_register_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    result = detector.register_algorithm(
        "test",
        algorithm,
    )

    assert result is detector
    assert detector.algorithm_count == 1
    assert detector.algorithm_names() == ["test"]
    assert detector.contains_algorithm("test") is True
    assert detector.exists_algorithm("test") is True
    assert "test" in detector


def test_register_algorithm_metadata(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
        enabled=False,
        metadata={"source": "unit-test"},
    )

    entry = detector.algorithm("test")

    assert entry["name"] == "test"
    assert entry["callable"] is algorithm
    assert entry["enabled"] is False
    assert entry["metadata"] == {
        "source": "unit-test",
    }


def test_register_algorithm_requires_callable(detector):
    with pytest.raises(
        TypeError,
        match="algorithm must be callable",
    ):
        detector.register_algorithm(
            "invalid",
            object(),
        )


def test_register_algorithm_replaces_existing(detector):
    def first(metrics):
        return {"value": 1}

    def second(metrics):
        return {"value": 2}

    detector.register_algorithm(
        "test",
        first,
    )

    detector.register_algorithm(
        "test",
        second,
    )

    assert detector.algorithm_count == 1
    assert detector.algorithm("test")["callable"] is second


def test_remove_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
    )

    result = detector.remove_algorithm("test")

    assert result is detector
    assert detector.algorithm_count == 0
    assert detector.contains_algorithm("test") is False


def test_remove_missing_algorithm_is_noop(detector):
    result = detector.remove_algorithm("missing")

    assert result is detector
    assert detector.algorithm_count == 0


def test_unregister_algorithm_alias(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
    )

    result = detector.unregister_algorithm("test")

    assert result is detector
    assert detector.contains_algorithm("test") is False


def test_algorithm_default(detector):
    sentinel = object()

    assert detector.algorithm(
        "missing",
        sentinel,
    ) is sentinel


def test_algorithms_returns_copy(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
    )

    algorithms = detector.algorithms()
    algorithms.clear()

    assert detector.algorithm_count == 1
    assert detector.contains_algorithm("test")


def test_enable_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
        enabled=False,
    )

    result = detector.enable_algorithm("test")

    assert result is detector
    assert detector.algorithm("test")["enabled"] is True


def test_disable_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
    )

    result = detector.disable_algorithm("test")

    assert result is detector
    assert detector.algorithm("test")["enabled"] is False


def test_enable_missing_algorithm_is_noop(detector):
    result = detector.enable_algorithm("missing")

    assert result is detector


def test_disable_missing_algorithm_is_noop(detector):
    result = detector.disable_algorithm("missing")

    assert result is detector


# ======================================================================
# Part 15. Built-in Registry
# ======================================================================


def test_register_builtin_algorithms(detector):
    assert detector.algorithm_names() == []

    result = detector.register_builtin_algorithms()

    assert result is detector

    assert detector.algorithm_names() == [
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
        "pipeline",
        "custom",
    ]

    assert detector.algorithm_count == 9


def test_register_builtin_algorithms_is_idempotent(detector):
    detector.register_builtin_algorithms()
    detector.register_builtin_algorithms()

    assert detector.algorithm_count == 9
    assert detector.algorithm_names() == [
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
        "pipeline",
        "custom",
    ]


def test_builtin_algorithms_are_callable(
    registered_detector,
):
    for name in registered_detector.algorithm_names():
        entry = registered_detector.algorithm(name)

        assert callable(entry["callable"])
        assert entry["enabled"] is True


def test_builtin_latency_can_execute(
    registered_detector,
):
    result = registered_detector.execute_algorithm(
        "latency",
        {"latency": 150},
    )

    assert result["algorithm"] == "latency"
    assert result["bottleneck"] is True


def test_builtin_pipeline_can_execute(
    registered_detector,
    bottleneck_metrics,
):
    result = registered_detector.execute_algorithm(
        "pipeline",
        bottleneck_metrics,
    )

    assert result["algorithm"] == "pipeline"
    assert result["bottleneck"] is True
    assert result["count"] == 7


# ======================================================================
# Part 16. Registry Execution
# ======================================================================


def test_execute_algorithm(detector):
    def algorithm(metrics):
        return {
            "algorithm": "test",
            "metric": metrics["value"],
            "bottleneck": False,
        }

    detector.register_algorithm(
        "test",
        algorithm,
    )

    result = detector.execute_algorithm(
        "test",
        {"value": 42},
    )

    assert result["algorithm"] == "test"
    assert result["metric"] == 42


def test_execute_unknown_algorithm(detector):
    with pytest.raises(
        KeyError,
        match="Unknown bottleneck algorithm",
    ):
        detector.execute_algorithm(
            "missing",
            {},
        )


def test_execute_disabled_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
        enabled=False,
    )

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        detector.execute_algorithm(
            "test",
            {},
        )


# ======================================================================
# Part 17. Detection API
# ======================================================================


def test_detect_unknown_algorithm(detector):
    with pytest.raises(
        KeyError,
        match="Unknown bottleneck algorithm",
    ):
        detector.detect(
            {},
            method="missing",
        )


def test_detect_disabled_algorithm(detector):
    def algorithm(metrics):
        return {"bottleneck": False}

    detector.register_algorithm(
        "test",
        algorithm,
        enabled=False,
    )

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        detector.detect(
            {},
            method="test",
        )


def test_detect_updates_statistics(detector):
    detector.register_builtin_algorithms()

    result = detector.detect(
        {"latency": 150},
        method="latency",
    )

    assert result["bottleneck"] is True
    assert detector.detection_count == 1
    assert detector.bottleneck_count == 1
    assert detector.error_count == 0
    assert detector.latest_latency >= 0.0
    assert detector.latest_latency == detector.latency_value


def test_detect_non_bottleneck_updates_detection_only(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 50},
        method="latency",
    )

    assert detector.detection_count == 1
    assert detector.bottleneck_count == 0
    assert detector.error_count == 0


def test_detect_stores_last_result(detector):
    detector.register_builtin_algorithms()

    result = detector.detect(
        {"latency": 150},
        method="latency",
    )

    assert detector.last_result == result


def test_detect_appends_history(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 50},
        method="latency",
    )

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    assert detector.history_size == 2


def test_detect_error_increments_error_count(detector):
    def failing(metrics):
        raise ValueError("boom")

    detector.register_algorithm(
        "failing",
        failing,
    )

    with pytest.raises(
        ValueError,
        match="boom",
    ):
        detector.detect(
            {},
            method="failing",
        )

    assert detector.error_count == 1
    assert detector.running is False


def test_detect_many(detector):
    detector.register_builtin_algorithms()

    results = detector.detect_many(
        [
            {"latency": 50},
            {"latency": 100},
            {"latency": 150},
        ],
        method="latency",
    )

    assert len(results) == 3
    assert detector.detection_count == 3


def test_detect_batch_alias(detector):
    detector.register_builtin_algorithms()

    results = detector.detect_batch(
        [
            {"latency": 50},
            {"latency": 150},
        ],
        method="latency",
    )

    assert len(results) == 2
    assert detector.detection_count == 2


def test_detect_one(detector):
    detector.register_builtin_algorithms()

    result = detector.detect_one(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"


def test_run_alias(detector):
    detector.register_builtin_algorithms()

    result = detector.run(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"


def test_execute_alias(detector):
    detector.register_builtin_algorithms()

    result = detector.execute(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"


def test_process_alias(detector):
    detector.register_builtin_algorithms()

    result = detector.process(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"


def test_call_delegates_to_detect(detector):
    detector.register_builtin_algorithms()

    result = detector(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"
    assert result["bottleneck"] is True
    assert detector.detection_count == 1


# ======================================================================
# Part 18. Runtime Operations
# ======================================================================


def test_reset_preserves_configuration_and_algorithms(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    detector.configure(
        latency_threshold=250,
    )

    detector.reset()

    assert detector.detection_count == 0
    assert detector.bottleneck_count == 0
    assert detector.error_count == 0
    assert detector.latest_latency == 0.0
    assert detector.latency_value == 0.0
    assert detector.running is False
    assert detector.history_size == 0
    assert detector.last_result is None

    assert detector.config["latency_threshold"] == 250
    assert detector.algorithm_count == 9


def test_clear_history(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    detector.clear()

    assert detector.history_size == 0
    assert detector.last_result is None

    assert detector.detection_count == 1
    assert detector.bottleneck_count == 1


def test_clear_preserves_statistics(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    detection_count = detector.detection_count
    bottleneck_count = detector.bottleneck_count

    detector.clear()

    assert detector.detection_count == detection_count
    assert detector.bottleneck_count == bottleneck_count


def test_snapshot(detector):
    detector.register_builtin_algorithms()

    detector.configure(
        latency_threshold=200,
    )

    detector.detect(
        {"latency": 250},
        method="latency",
    )

    snapshot = detector.snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot["config"]["latency_threshold"] == 200
    assert snapshot["detection_count"] == 1
    assert snapshot["bottleneck_count"] == 1
    assert snapshot["history"]
    assert snapshot["last_result"] is not None


def test_snapshot_contains_runtime_flags(detector):
    detector.freeze()

    snapshot = detector.snapshot()

    assert snapshot["enabled"] is True
    assert snapshot["frozen"] is True
    assert snapshot["closed"] is False


def test_snapshot_returns_independent_config(detector):
    detector.configure(
        latency_threshold=250,
    )

    snapshot = detector.snapshot()

    snapshot["config"]["latency_threshold"] = 9999

    assert detector.config["latency_threshold"] == 250


def test_snapshot_returns_independent_history(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    snapshot = detector.snapshot()

    snapshot["history"].clear()

    assert detector.history_size == 1


def test_snapshot_returns_independent_top_level_mapping(detector):
    snapshot = detector.snapshot()

    snapshot["config"] = {}

    assert detector.config != snapshot["config"]


def test_restore(detector):
    detector.register_builtin_algorithms()

    detector.configure(
        latency_threshold=200,
    )

    detector.detect(
        {"latency": 250},
        method="latency",
    )

    snapshot = detector.snapshot()

    restored = MetricBottleneckDetector()
    restored.register_builtin_algorithms()
    restored.restore(snapshot)

    assert restored.config["latency_threshold"] == 200
    assert restored.detection_count == 1
    assert restored.bottleneck_count == 1
    assert restored.history_size == 1
    assert restored.last_result is not None


def test_restore_returns_self(detector):
    snapshot = detector.snapshot()

    result = detector.restore(snapshot)

    assert result is detector


def test_restore_without_snapshot_is_noop(detector):
    result = detector.restore()

    assert result is detector
    assert detector.detection_count == 0


def test_restore_accepts_explicit_snapshot(detector):
    source = MetricBottleneckDetector()
    source.configure(
        latency_threshold=300,
    )

    snapshot = source.snapshot()

    detector.restore(snapshot)

    assert detector.config["latency_threshold"] == 300


def test_clone_preserves_runtime_state(detector):
    detector.register_builtin_algorithms()

    detector.configure(
        latency_threshold=200,
    )

    detector.detect(
        {"latency": 250},
        method="latency",
    )

    cloned = detector.clone()

    assert cloned is not detector
    assert cloned.id != detector.id

    assert cloned.name == detector.name
    assert cloned.description == detector.description
    assert cloned.version == detector.version

    assert cloned.config == detector.config
    assert cloned.detection_count == detector.detection_count
    assert cloned.bottleneck_count == detector.bottleneck_count
    assert cloned.error_count == detector.error_count
    assert cloned.history_size == detector.history_size
    assert cloned.last_result == detector.last_result


def test_clone_does_not_alias_config(detector):
    detector.configure(
        latency_threshold=200,
    )

    cloned = detector.clone()

    cloned.configure(
        latency_threshold=500,
    )

    assert detector.config["latency_threshold"] == 200
    assert cloned.config["latency_threshold"] == 500


def test_copy_alias(detector):
    cloned = detector.copy()

    assert cloned is not detector
    assert cloned.name == detector.name
    assert cloned.id != detector.id


# ======================================================================
# Part 19. Statistics & Diagnostics
# ======================================================================


def test_statistics_property(detector):
    statistics = detector.statistics

    assert statistics is not None


def test_summary_initial_state(detector):
    summary = detector.summary()

    assert summary["name"] == "MetricBottleneckDetector"
    assert summary["id"] == detector.id
    assert summary["version"] == "0.2.0"
    assert summary["enabled"] is True
    assert summary["running"] is False
    assert summary["bottleneck_count"] == 0
    assert summary["detection_count"] == 0
    assert summary["error_count"] == 0
    assert summary["latency"] == 0.0
    assert summary["algorithms"] == 0
    assert summary["uptime"] >= 0.0


def test_summary_after_detection(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    summary = detector.summary()

    assert summary["detection_count"] == 1
    assert summary["bottleneck_count"] == 1
    assert summary["algorithms"] == 9
    assert summary["latency"] >= 0.0


def test_health_initial_state(detector):
    health = detector.health()

    assert health["status"] == "healthy"
    assert health["active"] is True
    assert health["running"] is False
    assert health["errors"] == 0
    assert health["uptime"] >= 0.0


def test_health_disabled(detector):
    detector.disable()

    health = detector.health()

    assert health["status"] == "disabled"
    assert health["active"] is False


def test_health_frozen(detector):
    detector.freeze()

    health = detector.health()

    assert health["status"] == "frozen"
    assert health["active"] is False


def test_health_closed(detector):
    detector.close()

    health = detector.health()

    assert health["status"] == "closed"
    assert health["active"] is False


def test_health_priority_closed_over_disabled(detector):
    detector.disable()
    detector.close()

    health = detector.health()

    assert health["status"] == "closed"


def test_health_priority_disabled_over_frozen(detector):
    detector.freeze()
    detector.disable()

    health = detector.health()

    assert health["status"] == "disabled"


def test_status_is_health_alias(detector):
    assert detector.status() == detector.health()


def test_report(detector):
    report = detector.report()

    assert set(report) == {
        "summary",
        "configuration",
        "statistics",
        "history_size",
        "last_result",
    }

    assert report["configuration"] == detector.config
    assert report["history_size"] == 0
    assert report["last_result"] is None


# ======================================================================
# Part 20. Serialization
# ======================================================================


def test_to_dict(detector):
    data = detector.to_dict()

    assert data["id"] == detector.id
    assert data["name"] == detector.name
    assert data["description"] == detector.description
    assert data["version"] == detector.version
    assert data["enabled"] is True
    assert data["frozen"] is False
    assert data["closed"] is False
    assert data["config"] == detector.config
    assert data["bottleneck_count"] == 0
    assert data["detection_count"] == 0
    assert data["error_count"] == 0
    assert data["latency"] == 0.0
    assert data["algorithm_names"] == []
    assert data["history"] == []
    assert data["last_result"] is None


def test_to_dict_contains_timestamps(detector):
    data = detector.to_dict()

    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

    assert data["created_at"]
    assert data["updated_at"]


def test_to_dict_returns_config_copy(detector):
    data = detector.to_dict()

    data["config"]["latency_threshold"] = 9999

    assert detector.config["latency_threshold"] == 100.0


def test_to_dict_returns_history_copy(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    data = detector.to_dict()

    data["history"].clear()

    assert detector.history_size == 1


def test_serialize_alias(detector):
    assert detector.serialize() == detector.to_dict()


def test_from_dict(detector):
    detector.configure(
        latency_threshold=250,
    )

    data = detector.to_dict()

    restored = MetricBottleneckDetector.from_dict(
        data,
    )

    assert restored.id == detector.id
    assert restored.name == detector.name
    assert restored.description == detector.description
    assert restored.version == detector.version
    assert restored.config == detector.config
    assert restored.enabled == detector.enabled
    assert restored.frozen == detector.frozen
    assert restored.closed == detector.closed


def test_from_dict_restores_runtime_statistics(detector):
    detector.register_builtin_algorithms()

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    data = detector.to_dict()

    restored = MetricBottleneckDetector.from_dict(data)

    assert restored.detection_count == detector.detection_count
    assert restored.bottleneck_count == detector.bottleneck_count
    assert restored.error_count == detector.error_count
    assert restored.history_size == detector.history_size
    assert restored.last_result == detector.last_result
    assert restored.latest_latency == detector.latest_latency


def test_from_dict_restores_timestamps(detector):
    data = detector.to_dict()

    restored = MetricBottleneckDetector.from_dict(data)

    assert restored.created_at == detector.created_at
    assert restored.updated_at == detector.updated_at


def test_to_json(detector):
    text = detector.to_json()

    assert isinstance(text, str)

    data = json.loads(text)

    assert data["id"] == detector.id
    assert data["name"] == detector.name


def test_to_json_accepts_kwargs(detector):
    text = detector.to_json(
        indent=2,
        sort_keys=True,
    )

    assert isinstance(text, str)

    data = json.loads(text)

    assert data["id"] == detector.id


def test_from_json(detector):
    text = detector.to_json()

    restored = MetricBottleneckDetector.from_json(
        text,
    )

    assert restored.id == detector.id
    assert restored.name == detector.name
    assert restored.config == detector.config


def test_deserialize_from_dict(detector):
    data = detector.to_dict()

    restored = MetricBottleneckDetector.deserialize(
        data,
    )

    assert restored.id == detector.id
    assert restored.name == detector.name


def test_deserialize_from_json(detector):
    text = detector.to_json()

    restored = MetricBottleneckDetector.deserialize(
        text,
    )

    assert restored.id == detector.id
    assert restored.name == detector.name


def test_serialization_round_trip_preserves_runtime_state(
    detector,
):
    detector.register_builtin_algorithms()

    detector.configure(
        latency_threshold=250,
    )

    detector.detect(
        {"latency": 300},
        method="latency",
    )

    data = detector.to_dict()

    restored = MetricBottleneckDetector.from_dict(
        data,
    )

    assert restored.id == detector.id
    assert restored.config == detector.config
    assert restored.detection_count == detector.detection_count
    assert restored.bottleneck_count == detector.bottleneck_count
    assert restored.error_count == detector.error_count
    assert restored.history_size == detector.history_size
    assert restored.last_result == detector.last_result


# ======================================================================
# Part 21. Events & Hooks
# ======================================================================


def test_add_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(
            (
                sender,
                payload,
            )
        )

    result = detector.add_hook(
        "test",
        callback,
    )

    assert result is detector

    detector.emit(
        "test",
        value=42,
    )

    assert len(events) == 1
    assert events[0][0] is detector
    assert events[0][1]["value"] == 42


def test_add_hook_requires_callable(detector):
    with pytest.raises(
        TypeError,
        match="callback must be callable",
    ):
        detector.add_hook(
            "test",
            object(),
        )


def test_remove_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "test",
        callback,
    )

    result = detector.remove_hook(
        "test",
        callback,
    )

    assert result is detector

    detector.emit(
        "test",
        value=42,
    )

    assert events == []


def test_remove_all_hooks(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "test",
        callback,
    )

    detector.remove_hook(
        "test",
    )

    detector.emit(
        "test",
        value=42,
    )

    assert events == []


def test_remove_missing_hook_is_noop(detector):
    result = detector.remove_hook(
        "missing",
    )

    assert result is detector


def test_remove_missing_callback_is_noop(detector):
    def first(sender, **payload):
        pass

    def second(sender, **payload):
        pass

    detector.add_hook(
        "test",
        first,
    )

    result = detector.remove_hook(
        "test",
        second,
    )

    assert result is detector

    detector.emit(
        "test",
        value=42,
    )


def test_subscribe_alias(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    result = detector.subscribe(
        "test",
        callback,
    )

    assert result is detector

    detector.emit(
        "test",
        value=42,
    )

    assert events == [
        {"value": 42},
    ]


def test_emit_records_event(detector):
    detector.emit(
        "test",
        value=42,
    )

    assert len(detector._events) == 1

    event = detector._events[0]

    assert event["event"] == "test"
    assert event["payload"] == {
        "value": 42,
    }
    assert event["timestamp"] is not None


def test_emit_returns_self(detector):
    result = detector.emit(
        "test",
        value=42,
    )

    assert result is detector


def test_emit_supports_multiple_hooks(detector):
    calls = []

    def first(sender, **payload):
        calls.append("first")

    def second(sender, **payload):
        calls.append("second")

    detector.add_hook("test", first)
    detector.add_hook("test", second)

    detector.emit("test")

    assert calls == [
        "first",
        "second",
    ]


def test_before_detect_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "before_detect",
        callback,
    )

    result = detector.before_detect(
        {"latency": 100},
        "latency",
        threshold=50,
    )

    assert result is detector
    assert len(events) == 1
    assert events[0]["metrics"] == {
        "latency": 100,
    }
    assert events[0]["method"] == "latency"
    assert events[0]["kwargs"] == {
        "threshold": 50,
    }


def test_after_detect_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "after_detect",
        callback,
    )

    result = {
        "bottleneck": True,
    }

    returned = detector.after_detect(
        result,
        "latency",
    )

    assert returned is detector
    assert events[0]["result"] == result
    assert events[0]["method"] == "latency"


def test_before_algorithm_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "before_algorithm",
        callback,
    )

    result = detector.before_algorithm(
        "latency",
    )

    assert result is detector
    assert events == [
        {
            "algorithm": "latency",
        }
    ]


def test_after_algorithm_hook(detector):
    events = []

    def callback(sender, **payload):
        events.append(payload)

    detector.add_hook(
        "after_algorithm",
        callback,
    )

    result = {
        "bottleneck": False,
    }

    returned = detector.after_algorithm(
        "latency",
        result,
    )

    assert returned is detector
    assert events == [
        {
            "algorithm": "latency",
            "result": result,
        }
    ]


# ======================================================================
# Part 22. Python Protocols
# ======================================================================


def test_repr(detector):
    text = repr(detector)

    assert "MetricBottleneckDetector" in text
    assert "algorithms=0" in text
    assert "detections=0" in text


def test_str(detector):
    text = str(detector)

    assert "MetricBottleneckDetector" in text
    assert "algorithms=0" in text
    assert "detections=0" in text
    assert "bottlenecks=0" in text


def test_len(detector):
    assert len(detector) == 0

    detector.register_builtin_algorithms()

    assert len(detector) == 9


def test_iter(detector):
    detector.register_builtin_algorithms()

    names = [
        name
        for name, entry in detector
    ]

    assert names == [
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
        "pipeline",
        "custom",
    ]


def test_contains(detector):
    detector.register_builtin_algorithms()

    assert "latency" in detector
    assert "pipeline" in detector
    assert "missing" not in detector


def test_call(detector):
    detector.register_builtin_algorithms()

    result = detector(
        {"latency": 150},
        method="latency",
    )

    assert result["algorithm"] == "latency"
    assert result["bottleneck"] is True


def test_copy_protocol(detector):
    detector.register_builtin_algorithms()

    cloned = copy.copy(detector)

    assert cloned is not detector
    assert cloned.name == detector.name
    assert cloned.algorithm_count == detector.algorithm_count


def test_deepcopy_protocol(detector):
    detector.register_builtin_algorithms()

    cloned = copy.deepcopy(detector)

    assert cloned is not detector
    assert cloned.name == detector.name
    assert cloned.algorithm_count == detector.algorithm_count


def test_copy_protocol_has_independent_config(detector):
    detector.configure(
        latency_threshold=200,
    )

    cloned = copy.copy(detector)

    cloned.configure(
        latency_threshold=500,
    )

    assert detector.config["latency_threshold"] == 200
    assert cloned.config["latency_threshold"] == 500


def test_deepcopy_protocol_has_independent_config(detector):
    detector.configure(
        latency_threshold=200,
    )

    cloned = copy.deepcopy(detector)

    cloned.configure(
        latency_threshold=500,
    )

    assert detector.config["latency_threshold"] == 200
    assert cloned.config["latency_threshold"] == 500


# ======================================================================
# Part 23. Contract Matrix
# ======================================================================


@pytest.mark.parametrize(
    "method,metrics,expected_bottleneck",
    [
        (
            "latency",
            {"latency": 150},
            True,
        ),
        (
            "throughput",
            {"throughput": 500},
            True,
        ),
        (
            "utilization",
            {"utilization": 0.95},
            True,
        ),
        (
            "queue",
            {"queue": 150},
            True,
        ),
        (
            "contention",
            {"contention": 0.90},
            True,
        ),
        (
            "saturation",
            {"saturation": 0.95},
            True,
        ),
        (
            "dependency",
            {"dependency_depth": 10},
            True,
        ),
    ],
)
def test_builtin_detection_contract(
    detector,
    method,
    metrics,
    expected_bottleneck,
):
    result = getattr(
        detector,
        method,
    )(metrics)

    assert result["algorithm"] == method
    assert result["bottleneck"] is expected_bottleneck


@pytest.mark.parametrize(
    "method",
    [
        "latency",
        "throughput",
        "utilization",
        "queue",
        "contention",
        "saturation",
        "dependency",
        "pipeline",
        "custom",
    ],
)
def test_builtin_algorithm_methods_are_callable(
    detector,
    method,
):
    assert callable(
        getattr(
            detector,
            method,
        )
    )


# ======================================================================
# Part 24. Final Invariants
# ======================================================================


def test_detector_initial_invariants(detector):
    assert detector.active is True
    assert detector.enabled is True
    assert detector.frozen is False
    assert detector.closed is False

    assert detector.algorithm_count == 0
    assert detector.detection_count == 0
    assert detector.bottleneck_count == 0
    assert detector.error_count == 0

    assert detector.latest_latency == 0.0
    assert detector.latency_value == 0.0
    assert detector.history_size == 0
    assert detector.last_result is None


def test_registered_detector_invariants(
    registered_detector,
):
    assert registered_detector.active is True
    assert registered_detector.algorithm_count == 9

    assert all(
        callable(
            entry["callable"]
        )
        for entry in registered_detector.algorithms().values()
    )


def test_full_detection_lifecycle(
    detector,
    bottleneck_metrics,
):
    detector.register_builtin_algorithms()

    assert detector.algorithm_count == 9

    result = detector.pipeline(
        bottleneck_metrics,
    )

    assert result["bottleneck"] is True
    assert result["count"] == 7

    detector.detect(
        {"latency": 150},
        method="latency",
    )

    assert detector.detection_count == 1
    assert detector.bottleneck_count == 1
    assert detector.history_size == 1
    assert detector.last_result is not None
    assert detector.latest_latency >= 0.0


def test_full_lifecycle_enable_freeze_close_reopen(detector):
    assert detector.active is True

    detector.freeze()

    assert detector.frozen is True
    assert detector.active is False

    detector.unfreeze()

    assert detector.frozen is False
    assert detector.active is True

    detector.close()

    assert detector.closed is True
    assert detector.active is False

    detector.reopen()

    assert detector.closed is False
    assert detector.active is True

    detector.disable()

    assert detector.enabled is False
    assert detector.active is False

    detector.enable()

    assert detector.enabled is True
    assert detector.active is True