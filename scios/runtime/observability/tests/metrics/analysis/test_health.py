"""
SciOS-NG Runtime Metrics Analysis

Tests for MetricHealthAnalyzer.

SciOS/scios/runtime/observability/tests/metrics/analysis/test_health.py
"""

from __future__ import annotations

import copy
import json
import time

import pytest

from scios.runtime.observability.metrics.analysis.health import (
    MetricHealthAnalyzer,
)


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def analyzer():
    return MetricHealthAnalyzer()


@pytest.fixture
def metrics():
    return {
        "availability": 0.999,
        "reliability": 0.98,
        "latency": 20.0,
        "throughput": 200.0,
        "utilization": 0.50,
        "saturation": 0.20,
    }


@pytest.fixture
def unhealthy_metrics():
    return {
        "availability": 0.80,
        "reliability": 0.70,
        "latency": 200.0,
        "throughput": 20.0,
        "utilization": 0.95,
        "saturation": 1.50,
    }


# ==========================================================
# Part 1. Construction
# ==========================================================


def test_default_constructor(analyzer):
    assert analyzer.name == "MetricHealthAnalyzer"
    assert analyzer.description == ""
    assert analyzer.id
    assert isinstance(analyzer.id, str)


def test_custom_constructor():
    analyzer = MetricHealthAnalyzer(
        name="custom",
        description="health analyzer",
    )

    assert analyzer.name == "custom"
    assert analyzer.description == "health analyzer"
    assert analyzer.id


def test_identity_is_unique():
    a = MetricHealthAnalyzer()
    b = MetricHealthAnalyzer()

    assert a.id != b.id


# ==========================================================
# Part 2. Runtime State
# ==========================================================


def test_initial_runtime_state(analyzer):
    assert analyzer.enabled is True
    assert analyzer.disabled is False
    assert analyzer.frozen is False
    assert analyzer.closed is False
    assert analyzer.running is False
    assert analyzer.active is True


def test_initial_statistics(analyzer):
    assert analyzer.health_count == 0
    assert analyzer.analysis_count == 0
    assert analyzer.error_count == 0
    assert analyzer.latency == 0.0
    assert analyzer.uptime >= 0.0


def test_initial_algorithms_are_registered(analyzer):
    expected = {
        "availability",
        "reliability",
        "latency",
        "throughput",
        "utilization",
        "saturation",
        "health_score",
        "overall",
        "custom",
    }

    assert expected.issubset(
        set(analyzer.algorithm_names())
    )


def test_algorithm_count(analyzer):
    assert analyzer.algorithm_count >= 9


# ==========================================================
# Part 3. Configuration
# ==========================================================


def test_config_returns_copy(analyzer):
    config = analyzer.config()

    assert isinstance(config, dict)

    config["healthy_score"] = -1

    assert analyzer.config("healthy_score") == 90.0


def test_config_get(analyzer):
    assert analyzer.config("healthy_score") == 90.0
    assert analyzer.config("missing") is None
    assert analyzer.config("missing", 123) == 123


def test_configure(analyzer):
    result = analyzer.configure(
        healthy_score=95.0,
        warning_score=75.0,
    )

    assert result is analyzer
    assert analyzer.config("healthy_score") == 95.0
    assert analyzer.config("warning_score") == 75.0


def test_configure_preserves_existing_config(analyzer):
    analyzer.configure(custom_threshold=42)

    assert analyzer.config("healthy_score") == 90.0
    assert analyzer.config("custom_threshold") == 42


# ==========================================================
# Part 4. Health Analysis API
# ==========================================================


def test_analyze_overall(analyzer, metrics):
    result = analyzer.analyze(metrics)

    assert isinstance(result, dict)
    assert result["algorithm"] == "overall"
    assert "score" in result
    assert "level" in result
    assert "results" in result


def test_analyze_explicit_method(analyzer, metrics):
    result = analyzer.analyze(
        metrics,
        method="availability",
    )

    assert result["algorithm"] == "availability"


def test_analyze_one(analyzer, metrics):
    result = analyzer.analyze_one(metrics)

    assert isinstance(result, dict)
    assert result["algorithm"] == "overall"


def test_analyze_many(analyzer, metrics):
    results = analyzer.analyze_many(
        [metrics, metrics]
    )

    assert len(results) == 2
    assert all(isinstance(x, dict) for x in results)


def test_analyze_batch(analyzer, metrics):
    results = analyzer.analyze_batch(
        [metrics, metrics]
    )

    assert len(results) == 2


# ==========================================================
# Part 5. Analysis Aliases
# ==========================================================


def test_run_is_analyze_alias(analyzer):
    assert analyzer.run.__func__ is analyzer.analyze.__func__


def test_execute_is_analyze_alias(analyzer):
    assert analyzer.execute.__func__ is analyzer.analyze.__func__


def test_process_is_analyze_alias(analyzer):
    assert analyzer.process.__func__ is analyzer.analyze.__func__


def test_run_behaves_like_analyze(analyzer, metrics):
    assert analyzer.run(metrics) == analyzer.analyze(metrics)


# ==========================================================
# Part 6. Unknown / Disabled Algorithms
# ==========================================================


def test_analyze_unknown_algorithm_raises(analyzer, metrics):
    with pytest.raises(
        KeyError,
        match="Unknown health algorithm",
    ):
        analyzer.analyze(
            metrics,
            method="missing",
        )


def test_execute_unknown_algorithm_raises(analyzer, metrics):
    with pytest.raises(
        KeyError,
        match="Unknown health algorithm",
    ):
        analyzer.execute_algorithm(
            "missing",
            metrics,
        )


def test_disabled_algorithm_raises(analyzer, metrics):
    analyzer.disable_algorithm("overall")

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        analyzer.analyze(
            metrics,
            method="overall",
        )


def test_enable_algorithm(analyzer):
    analyzer.disable_algorithm("overall")

    assert analyzer.algorithm("overall")["enabled"] is False

    result = analyzer.enable_algorithm("overall")

    assert result is analyzer
    assert analyzer.algorithm("overall")["enabled"] is True


# ==========================================================
# Part 7. Built-in Algorithms
# ==========================================================


def test_availability_healthy(analyzer):
    result = analyzer.availability(
        {"availability": 0.999}
    )

    assert result["algorithm"] == "availability"
    assert result["metric"] == pytest.approx(0.999)
    assert result["healthy"] is True
    assert result["score"] == pytest.approx(99.9)


def test_availability_unhealthy(analyzer):
    result = analyzer.availability(
        {"availability": 0.90}
    )

    assert result["healthy"] is False
    assert result["score"] == pytest.approx(90.0)


def test_reliability(analyzer):
    result = analyzer.reliability(
        {"reliability": 0.98}
    )

    assert result["algorithm"] == "reliability"
    assert result["healthy"] is True
    assert result["score"] == pytest.approx(98.0)


def test_latency_healthy(analyzer):
    result = analyzer.latency(
        {"latency": 20.0}
    )

    assert result["healthy"] is True
    assert result["score"] == pytest.approx(80.0)


def test_latency_at_threshold(analyzer):
    threshold = analyzer.config(
        "latency_threshold"
    )

    result = analyzer.latency(
        {"latency": threshold}
    )

    assert result["healthy"] is True
    assert result["score"] == pytest.approx(0.0)


def test_latency_above_threshold(analyzer):
    result = analyzer.latency(
        {"latency": 200.0}
    )

    assert result["healthy"] is False
    assert result["score"] == pytest.approx(0.0)


def test_throughput_healthy(analyzer):
    result = analyzer.throughput(
        {"throughput": 200.0}
    )

    assert result["healthy"] is True
    assert result["score"] == pytest.approx(100.0)


def test_throughput_below_threshold(analyzer):
    result = analyzer.throughput(
        {"throughput": 50.0}
    )

    assert result["healthy"] is False
    assert result["score"] == pytest.approx(50.0)


def test_utilization_healthy(analyzer):
    result = analyzer.utilization(
        {"utilization": 0.50}
    )

    assert result["healthy"] is True
    assert result["score"] == pytest.approx(
        100.0 * (1.0 - 0.50 / 0.85)
    )


def test_utilization_above_threshold(analyzer):
    result = analyzer.utilization(
        {"utilization": 0.95}
    )

    assert result["healthy"] is False
    assert result["score"] == pytest.approx(0.0)


def test_saturation_healthy(analyzer):
    result = analyzer.saturation(
        {"saturation": 0.20}
    )

    assert result["healthy"] is True
    assert result["score"] == pytest.approx(80.0)


def test_saturation_above_threshold(analyzer):
    result = analyzer.saturation(
        {"saturation": 1.50}
    )

    assert result["healthy"] is False
    assert result["score"] == pytest.approx(0.0)


def test_health_score(analyzer, metrics):
    result = analyzer.health_score(metrics)

    assert result["algorithm"] == "health_score"
    assert "score" in result
    assert "results" in result
    assert len(result["results"]) == 6


def test_overall_healthy(analyzer, metrics):
    result = analyzer.overall(metrics)

    assert result["algorithm"] == "overall"
    assert result["level"] in {
        "healthy",
        "warning",
        "critical",
    }
    assert result["score"] >= 0.0
    assert result["score"] <= 100.0


def test_overall_unhealthy(analyzer, unhealthy_metrics):
    result = analyzer.overall(
        unhealthy_metrics
    )

    assert result["level"] == "critical"
    assert result["score"] < analyzer.config(
        "warning_score"
    )


def test_custom_algorithm(analyzer, metrics):
    def custom(metrics, **kwargs):
        return {
            "algorithm": "custom_test",
            "healthy": True,
            "score": 123,
        }

    result = analyzer.custom(
        metrics,
        custom,
    )

    assert result["algorithm"] == "custom_test"
    assert result["score"] == 123


def test_custom_requires_callable(analyzer, metrics):
    with pytest.raises(
        TypeError,
        match="analyzer must be callable",
    ):
        analyzer.custom(
            metrics,
            None,
        )


# ==========================================================
# Part 8. Analysis Counters
# ==========================================================


def test_analysis_count(analyzer, metrics):
    assert analyzer.analysis_count == 0

    analyzer.analyze(metrics)

    assert analyzer.analysis_count == 1


def test_health_count_for_healthy_result(
    analyzer,
    metrics,
):
    result = analyzer.analyze(metrics)

    print("\nDEBUG RESULT = - test_health.py:491", result)
    print("DEBUG CONFIG = - test_health.py:492", analyzer.config())
    print("DEBUG HEALTH_COUNT = - test_health.py:493", analyzer.health_count)
    print("DEBUG ANALYSIS_COUNT = - test_health.py:494", analyzer.analysis_count)

    assert analyzer.health_count == 1


def test_error_count(analyzer, metrics):
    with pytest.raises(KeyError):
        analyzer.analyze(
            metrics,
            method="missing",
        )

    assert analyzer.error_count == 1


def test_last_result(analyzer, metrics):
    result = analyzer.analyze(metrics)

    assert analyzer._last_result is result


def test_history(analyzer, metrics):
    analyzer.analyze(metrics)
    analyzer.analyze(metrics)

    assert len(analyzer._history) == 2


def test_running_is_false_after_analysis(
    analyzer,
    metrics,
):
    analyzer.analyze(metrics)

    assert analyzer.running is False


def test_latency_is_recorded(analyzer, metrics):
    analyzer.analyze(metrics)

    assert analyzer.latency >= 0.0


# ==========================================================
# Part 9. Registry API
# ==========================================================


def test_register_algorithm(analyzer):
    def algorithm(metrics, **kwargs):
        return {"healthy": True}

    result = analyzer.register_algorithm(
        "custom_test",
        algorithm,
    )

    assert result is analyzer
    assert analyzer.contains_algorithm(
        "custom_test"
    )
    assert analyzer.exists_algorithm(
        "custom_test"
    )


def test_register_algorithm_requires_callable(
    analyzer,
):
    with pytest.raises(
        TypeError,
        match="algorithm must be callable",
    ):
        analyzer.register_algorithm(
            "invalid",
            None,
        )


def test_algorithm(analyzer):
    entry = analyzer.algorithm("overall")

    assert entry is not None
    assert entry["name"] == "overall"
    assert callable(entry["callable"])


def test_algorithm_default(analyzer):
    assert analyzer.algorithm(
        "missing",
        "default",
    ) == "default"


def test_algorithms_returns_copy(analyzer):
    algorithms = analyzer.algorithms()

    assert isinstance(algorithms, dict)

    algorithms.clear()

    assert analyzer.algorithm_count >= 9


def test_algorithm_names(analyzer):
    names = analyzer.algorithm_names()

    assert "overall" in names
    assert "availability" in names


def test_remove_algorithm(analyzer):
    analyzer.register_algorithm(
        "temporary",
        lambda metrics: {},
    )

    result = analyzer.remove_algorithm(
        "temporary"
    )

    assert result is analyzer
    assert not analyzer.contains_algorithm(
        "temporary"
    )


def test_unregister_algorithm(analyzer):
    analyzer.register_algorithm(
        "temporary",
        lambda metrics: {},
    )

    analyzer.unregister_algorithm(
        "temporary"
    )

    assert not analyzer.contains_algorithm(
        "temporary"
    )


def test_clear_algorithms(analyzer):
    result = analyzer.clear_algorithms()

    assert result is analyzer
    assert analyzer.algorithm_count == 0


def test_execute_registered_algorithm(analyzer):
    def algorithm(metrics, **kwargs):
        return {
            "algorithm": "test",
            "healthy": True,
        }

    analyzer.register_algorithm(
        "test",
        algorithm,
    )

    result = analyzer.execute_algorithm(
        "test",
        {},
    )

    assert result["algorithm"] == "test"


def test_contains_algorithm(analyzer):
    assert analyzer.contains_algorithm(
        "overall"
    )
    assert not analyzer.contains_algorithm(
        "missing"
    )


# ==========================================================
# Part 10. Lifecycle
# ==========================================================


def test_enable(analyzer):
    analyzer.disable()

    assert analyzer.active is False

    result = analyzer.enable()

    assert result is analyzer
    assert analyzer.enabled is True
    assert analyzer.active is True


def test_disable(analyzer):
    result = analyzer.disable()

    assert result is analyzer
    assert analyzer.enabled is False
    assert analyzer.disabled is True
    assert analyzer.active is False
    assert analyzer.running is False


def test_freeze(analyzer):
    result = analyzer.freeze()

    assert result is analyzer
    assert analyzer.frozen is True
    assert analyzer.active is False


def test_unfreeze(analyzer):
    analyzer.freeze()

    result = analyzer.unfreeze()

    assert result is analyzer
    assert analyzer.frozen is False
    assert analyzer.active is True


def test_close(analyzer):
    result = analyzer.close()

    assert result is analyzer
    assert analyzer.closed is True
    assert analyzer.active is False
    assert analyzer.running is False


def test_reopen(analyzer):
    analyzer.close()

    result = analyzer.reopen()

    assert result is analyzer
    assert analyzer.closed is False
    assert analyzer.active is True


def test_analyze_requires_active(
    analyzer,
    metrics,
):
    analyzer.disable()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        analyzer.analyze(metrics)


def test_analyze_when_frozen(
    analyzer,
    metrics,
):
    analyzer.freeze()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        analyzer.analyze(metrics)


def test_analyze_when_closed(
    analyzer,
    metrics,
):
    analyzer.close()

    with pytest.raises(
        RuntimeError,
        match="not active",
    ):
        analyzer.analyze(metrics)


# ==========================================================
# Part 11. Reset / Clear
# ==========================================================


def test_reset_preserves_algorithms(
    analyzer,
    metrics,
):
    analyzer.analyze(metrics)

    analyzer.reset()

    assert analyzer.analysis_count == 0
    assert analyzer.health_count == 0
    assert analyzer.error_count == 0
    assert analyzer.latency == 0.0
    assert analyzer.running is False
    assert analyzer._last_result is None
    assert analyzer._history == []
    assert analyzer.algorithm_count >= 9


def test_reset_preserves_configuration(analyzer):
    analyzer.configure(
        healthy_score=95.0
    )

    analyzer.reset()

    assert analyzer.config(
        "healthy_score"
    ) == 95.0


def test_clear_history(analyzer, metrics):
    analyzer.analyze(metrics)

    analyzer.clear()

    assert analyzer._history == []
    assert analyzer._last_result is None

    # clear() in current contract preserves counters.
    assert analyzer.analysis_count == 1


# ==========================================================
# Part 12. Snapshot / Restore
# ==========================================================


def test_snapshot(analyzer, metrics):
    analyzer.configure(
        healthy_score=95.0
    )
    analyzer.analyze(metrics)

    snapshot = analyzer.snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot["config"]["healthy_score"] == 95.0
    assert snapshot["analysis_count"] == 1
    assert snapshot["health_count"] == 1
    assert "history" in snapshot
    assert "last_result" in snapshot


def test_snapshot_is_independent(analyzer, metrics):
    analyzer.analyze(metrics)

    snapshot = analyzer.snapshot()

    snapshot["config"]["healthy_score"] = -1
    snapshot["history"].clear()

    assert analyzer.config(
        "healthy_score"
    ) != -1
    assert len(analyzer._history) == 1


def test_restore(analyzer, metrics):
    analyzer.configure(
        healthy_score=95.0
    )
    analyzer.analyze(metrics)

    snapshot = analyzer.snapshot()

    analyzer.reset()

    analyzer.restore(snapshot)

    assert analyzer.config(
        "healthy_score"
    ) == 95.0
    assert analyzer.analysis_count == 1
    assert analyzer.health_count == 1
    assert len(analyzer._history) == 1


def test_restore_default_snapshot(analyzer):
    assert analyzer.restore() is analyzer


def test_restore_without_snapshot_is_noop(analyzer):
    analyzer._snapshot = None

    assert analyzer.restore() is analyzer


# ==========================================================
# Part 13. Clone
# ==========================================================


def test_clone(analyzer, metrics):
    analyzer.configure(
        healthy_score=95.0
    )
    analyzer._context["nested"] = {
        "values": [1]
    }
    analyzer.analyze(metrics)

    cloned = analyzer.clone()

    assert cloned is not analyzer

    # Contract: clone preserves identity.
    assert cloned.id == analyzer.id

    assert cloned.name == analyzer.name
    assert cloned.description == analyzer.description

    assert cloned.config(
        "healthy_score"
    ) == 95.0

    assert cloned._history == analyzer._history

    cloned._context["nested"]["values"].append(2)

    assert analyzer._context["nested"]["values"] == [1]


def test_clone_has_independent_lock(analyzer):
    cloned = analyzer.clone()

    assert cloned._lock is not analyzer._lock


def test_clone_preserves_algorithms(analyzer):
    cloned = analyzer.clone()

    assert set(
        cloned.algorithm_names()
    ) == set(
        analyzer.algorithm_names()
    )


def test_clone_algorithm_execution_belongs_to_clone(
    analyzer,
    metrics,
):
    cloned = analyzer.clone()

    result = cloned.analyze(metrics)

    assert result["algorithm"] == "overall"


def test_copy_is_clone(analyzer, metrics):
    analyzer.analyze(metrics)

    copied = analyzer.copy()

    assert copied is not analyzer
    assert copied.id == analyzer.id
    assert copied._history == analyzer._history


# ==========================================================
# Part 14. Copy / Deepcopy Protocol
# ==========================================================


def test_copy_protocol(analyzer):
    copied = copy.copy(analyzer)

    assert copied is not analyzer
    assert copied.id == analyzer.id


def test_deepcopy_protocol(analyzer):
    analyzer._context["nested"] = {
        "values": [1]
    }

    cloned = copy.deepcopy(analyzer)

    assert cloned is not analyzer

    # Contract: deepcopy preserves identity.
    assert cloned.id == analyzer.id

    assert cloned._lock is not analyzer._lock

    cloned._context["nested"]["values"].append(2)

    assert analyzer._context["nested"]["values"] == [1]


# ==========================================================
# Part 15. Serialization
# ==========================================================


def test_to_dict(analyzer):
    data = analyzer.to_dict()

    assert isinstance(data, dict)
    assert data["id"] == analyzer.id
    assert data["name"] == analyzer.name
    assert data["description"] == analyzer.description
    assert "config" in data
    assert "version" in data


def test_to_dict_contains_statistics(analyzer):
    data = analyzer.to_dict()

    assert data["health_count"] == 0
    assert data["analysis_count"] == 0
    assert data["error_count"] == 0
    assert data["latency"] == 0.0


def test_from_dict_creates_new_identity(analyzer):
    data = analyzer.to_dict()

    restored = MetricHealthAnalyzer.from_dict(
        data
    )

    assert restored is not analyzer

    # Deserialization creates a new runtime identity.
    assert restored.id != analyzer.id

    assert restored.name == analyzer.name
    assert restored.description == analyzer.description


def test_from_dict_restores_runtime_state(
    analyzer,
):
    analyzer.configure(
        healthy_score=95.0
    )

    analyzer._health_count = 4
    analyzer._analysis_count = 5
    analyzer._error_count = 1
    analyzer._latency = 0.25

    data = analyzer.to_dict()

    restored = MetricHealthAnalyzer.from_dict(
        data
    )

    assert restored.config(
        "healthy_score"
    ) == 95.0

    assert restored.health_count == 4
    assert restored.analysis_count == 5
    assert restored.error_count == 1
    assert restored.latency == pytest.approx(
        0.25
    )


def test_to_json(analyzer):
    data = analyzer.to_json()

    assert isinstance(data, str)

    decoded = json.loads(data)

    assert decoded["name"] == analyzer.name


def test_from_json(analyzer):
    data = analyzer.to_json()

    restored = MetricHealthAnalyzer.from_json(
        data
    )

    assert restored.name == analyzer.name
    assert restored.id != analyzer.id


def test_serialize(analyzer):
    data = analyzer.serialize()

    assert isinstance(data, str)
    assert json.loads(data)["name"] == analyzer.name


def test_deserialize(analyzer):
    data = analyzer.serialize()

    restored = MetricHealthAnalyzer.deserialize(
        data
    )

    assert restored.name == analyzer.name
    assert restored.id != analyzer.id


# ==========================================================
# Part 16. Health / Status Diagnostics
# ==========================================================


def test_health_initial(analyzer):
    result = analyzer.health()

    assert result["state"] == "idle"
    assert result["healthy"] is True
    assert result["errors"] == 0
    assert result["uptime"] >= 0.0


def test_health_disabled(analyzer):
    analyzer.disable()

    result = analyzer.health()

    assert result["state"] == "disabled"
    assert result["healthy"] is False


def test_health_frozen(analyzer):
    analyzer.freeze()

    result = analyzer.health()

    assert result["state"] == "frozen"
    assert result["healthy"] is False


def test_health_closed(analyzer):
    analyzer.close()

    result = analyzer.health()

    assert result["state"] == "closed"
    assert result["healthy"] is False


def test_status_is_health_result(analyzer):
    assert analyzer.status() == analyzer.health()


def test_summary(analyzer):
    result = analyzer.summary()

    assert result["id"] == analyzer.id
    assert result["name"] == analyzer.name
    assert result["version"] == analyzer.version
    assert result["health_count"] == 0
    assert result["analysis_count"] == 0
    assert "algorithms" in result


def test_report(analyzer):
    result = analyzer.report()

    assert isinstance(result, dict)
    assert "summary" in result
    assert "configuration" in result
    assert "history" in result
    assert "last_result" in result
    assert "statistics" in result


# ==========================================================
# Part 17. Events / Hooks
# ==========================================================


def test_add_hook(analyzer):
    events = []

    def callback(*args, **kwargs):
        events.append((args, kwargs))

    result = analyzer.add_hook(
        "test",
        callback,
    )

    assert result is analyzer


def test_add_hook_requires_callable(analyzer):
    with pytest.raises(
        TypeError,
        match="callback must be callable",
    ):
        analyzer.add_hook(
            "test",
            None,
        )


def test_emit_records_event(analyzer):
    result = analyzer.emit(
        "test",
        value=123,
    )

    assert result is analyzer
    assert len(analyzer._events) == 1
    assert analyzer._events[-1]["event"] == "test"
    assert analyzer._events[-1]["payload"]["value"] == 123


def test_emit_calls_hook(analyzer):
    received = []

    def callback(instance, **payload):
        received.append(
            (instance, payload)
        )

    analyzer.add_hook(
        "test",
        callback,
    )

    analyzer.emit(
        "test",
        value=123,
    )

    assert len(received) == 1
    assert received[0][0] is analyzer
    assert received[0][1]["value"] == 123


def test_remove_hook(analyzer):
    calls = []

    def callback(instance, **payload):
        calls.append(1)

    analyzer.add_hook(
        "test",
        callback,
    )

    analyzer.remove_hook(
        "test",
        callback,
    )

    analyzer.emit(
        "test"
    )

    assert calls == []


def test_remove_all_hooks_for_event(analyzer):
    calls = []

    def callback(instance, **payload):
        calls.append(1)

    analyzer.add_hook(
        "test",
        callback,
    )

    analyzer.remove_hook("test")

    analyzer.emit("test")

    assert calls == []


def test_subscribe(analyzer):
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    result = analyzer.subscribe(
        "test",
        callback,
    )

    assert result is analyzer

    analyzer.emit(
        "test",
        value=42,
    )

    assert calls == [{"value": 42}]


# ==========================================================
# Part 18. Built-in Analysis Events
# ==========================================================


def test_before_analyze_event(analyzer, metrics):
    events = []

    def callback(instance, **payload):
        events.append(payload)

    analyzer.subscribe(
        "before_analyze",
        callback,
    )

    analyzer.analyze(metrics)

    assert len(events) == 1
    assert events[0]["metrics"] == metrics
    assert events[0]["method"] == "overall"


def test_after_analyze_event(analyzer, metrics):
    events = []

    def callback(instance, **payload):
        events.append(payload)

    analyzer.subscribe(
        "after_analyze",
        callback,
    )

    analyzer.analyze(metrics)

    assert len(events) == 1
    assert events[0]["method"] == "overall"
    assert "result" in events[0]


def test_before_algorithm_event(analyzer, metrics):
    algorithms = []

    def callback(instance, **payload):
        algorithms.append(
            payload["algorithm"]
        )

    analyzer.subscribe(
        "before_algorithm",
        callback,
    )

    analyzer.analyze(
        metrics,
        method="availability",
    )

    assert algorithms == ["availability"]


def test_after_algorithm_event(analyzer, metrics):
    algorithms = []

    def callback(instance, **payload):
        algorithms.append(
            payload["algorithm"]
        )

    analyzer.subscribe(
        "after_algorithm",
        callback,
    )

    analyzer.analyze(
        metrics,
        method="availability",
    )

    assert algorithms == ["availability"]


# ==========================================================
# Part 19. Hook Failure Semantics
# ==========================================================


def test_hook_failure_does_not_break_analysis(
    analyzer,
    metrics,
):
    def broken_hook(instance, **payload):
        raise RuntimeError("hook failure")

    analyzer.subscribe(
        "before_analyze",
        broken_hook,
    )

    # Current expected runtime contract:
    # hook failures should not prevent analysis.
    result = analyzer.analyze(metrics)

    assert result["algorithm"] == "overall"


# ==========================================================
# Part 20. Python Protocols
# ==========================================================


def test_repr(analyzer):
    text = repr(analyzer)

    assert "MetricHealthAnalyzer" in text
    assert "algorithms=" in text
    assert "analyses=" in text


def test_str(analyzer):
    text = str(analyzer)

    assert analyzer.name in text
    assert "algorithms=" in text


def test_len(analyzer):
    assert len(analyzer) == analyzer.algorithm_count


def test_iter(analyzer):
    items = list(iter(analyzer))

    assert len(items) == analyzer.algorithm_count

    name, entry = items[0]

    assert isinstance(name, str)
    assert isinstance(entry, dict)


def test_contains(analyzer):
    assert "overall" in analyzer
    assert "missing" not in analyzer


def test_callable(analyzer, metrics):
    result = analyzer(metrics)

    assert isinstance(result, dict)
    assert result["algorithm"] == "overall"


# ==========================================================
# Part 21. Edge Cases
# ==========================================================


def test_availability_default(analyzer):
    result = analyzer.availability({})

    assert result["metric"] == pytest.approx(1.0)
    assert result["healthy"] is True


def test_reliability_default(analyzer):
    result = analyzer.reliability({})

    assert result["metric"] == pytest.approx(1.0)
    assert result["healthy"] is True


def test_latency_default(analyzer):
    result = analyzer.latency({})

    assert result["metric"] == pytest.approx(0.0)
    assert result["healthy"] is True


def test_throughput_default(analyzer):
    result = analyzer.throughput({})

    assert result["metric"] == pytest.approx(0.0)
    assert result["healthy"] is False


def test_utilization_default(analyzer):
    result = analyzer.utilization({})

    assert result["metric"] == pytest.approx(0.0)
    assert result["healthy"] is True


def test_saturation_default(analyzer):
    result = analyzer.saturation({})

    assert result["metric"] == pytest.approx(0.0)
    assert result["healthy"] is True


def test_numeric_values_are_converted(analyzer):
    result = analyzer.availability(
        {"availability": "0.99"}
    )

    assert result["metric"] == pytest.approx(0.99)


def test_analysis_preserves_result_structure(
    analyzer,
    metrics,
):
    result = analyzer.analyze(metrics)

    assert isinstance(result["score"], float)
    assert isinstance(result["results"], list)

    for item in result["results"]:
        assert "algorithm" in item
        assert "metric" in item
        assert "threshold" in item
        assert "healthy" in item
        assert "score" in item


# ==========================================================
# Part 22. Runtime Consistency
# ==========================================================


def test_analysis_updates_updated_at(
    analyzer,
    metrics,
):
    before = analyzer.updated_at

    time.sleep(0.001)

    analyzer.analyze(metrics)

    assert analyzer.updated_at >= before


def test_configuration_updates_updated_at(analyzer):
    before = analyzer.updated_at

    time.sleep(0.001)

    analyzer.configure(
        healthy_score=91.0
    )

    assert analyzer.updated_at >= before


def test_register_updates_updated_at(analyzer):
    before = analyzer.updated_at

    time.sleep(0.001)

    analyzer.register_algorithm(
        "temporary",
        lambda metrics: {},
    )

    assert analyzer.updated_at >= before


# ==========================================================
# Part 23. Identity Contract
# ==========================================================


def test_clone_identity_is_preserved(analyzer):
    cloned = analyzer.clone()

    assert cloned.id == analyzer.id


def test_deepcopy_identity_is_preserved(analyzer):
    cloned = copy.deepcopy(analyzer)

    assert cloned.id == analyzer.id


def test_serialization_identity_is_new(analyzer):
    restored = MetricHealthAnalyzer.from_dict(
        analyzer.to_dict()
    )

    assert restored.id != analyzer.id


def test_json_roundtrip_identity_is_new(analyzer):
    restored = MetricHealthAnalyzer.from_json(
        analyzer.to_json()
    )

    assert restored.id != analyzer.id