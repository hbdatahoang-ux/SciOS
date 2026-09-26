"""
Tests for MetricRegistry.

Coverage
--------
- registration
- duplicate handling
- lookup
- iteration
- removal
- reset
- snapshot / restore
- thread safety
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.counter import Counter
from scios.runtime.observability.metrics.gauge import Gauge
from scios.runtime.observability.metrics.histogram import Histogram
from scios.runtime.observability.metrics.registry import MetricRegistry
from scios.runtime.observability.metrics.summary import Summary
from scios.runtime.observability.metrics.timer import Timer


# ==========================================================
# Construction
# ==========================================================


def test_registry_initially_empty():
    registry = MetricRegistry()

    assert len(registry) == 0


def test_registry_repr():
    registry = MetricRegistry()

    assert "MetricRegistry" in repr(registry)


# ==========================================================
# Registration
# ==========================================================


def test_register_counter():
    registry = MetricRegistry()

    metric = Counter("requests")

    registry.register(metric)

    assert registry.get("requests") is metric


def test_register_gauge():
    registry = MetricRegistry()

    metric = Gauge("cpu")

    registry.register(metric)

    assert registry.get("cpu") is metric


def test_register_histogram():
    registry = MetricRegistry()

    metric = Histogram("latency")

    registry.register(metric)

    assert registry.get("latency") is metric


def test_register_summary():
    registry = MetricRegistry()

    metric = Summary("response")

    registry.register(metric)

    assert registry.get("response") is metric


def test_register_timer():
    registry = MetricRegistry()

    metric = Timer("runtime")

    registry.register(metric)

    assert registry.get("runtime") is metric


# ==========================================================
# Duplicate registration
# ==========================================================


def test_duplicate_registration_rejected():
    registry = MetricRegistry()

    registry.register(Counter("requests"))

    with pytest.raises(Exception):
        registry.register(Counter("requests"))


# ==========================================================
# Lookup
# ==========================================================


def test_get_existing_metric():
    registry = MetricRegistry()

    metric = Counter("requests")

    registry.register(metric)

    assert registry.get("requests") is metric


def test_get_unknown_metric():
    registry = MetricRegistry()

    assert registry.get("missing") is None


def test_contains_metric():
    registry = MetricRegistry()

    registry.register(Counter("requests"))

    assert "requests" in registry


def test_missing_metric_not_contains():
    registry = MetricRegistry()

    assert "cpu" not in registry


# ==========================================================
# Remove
# ==========================================================


def test_remove_metric():
    registry = MetricRegistry()

    registry.register(Counter("requests"))

    registry.remove("requests")

    assert registry.get("requests") is None


def test_remove_missing_metric():
    registry = MetricRegistry()

    registry.remove("missing")

    assert len(registry) == 0


# ==========================================================
# Iteration
# ==========================================================


def test_iter_metrics():
    registry = MetricRegistry()

    registry.register(Counter("a"))
    registry.register(Gauge("b"))

    names = {m.name for m in registry}

    assert names == {"a", "b"}


def test_registry_len():
    registry = MetricRegistry()

    registry.register(Counter("a"))
    registry.register(Gauge("b"))
    registry.register(Histogram("c"))

    assert len(registry) == 3


# ==========================================================
# Reset
# ==========================================================


def test_reset_registry():
    registry = MetricRegistry()

    c = Counter("counter")
    g = Gauge("gauge")

    registry.register(c)
    registry.register(g)

    c.inc(5)
    g.set(42)

    registry.reset()

    assert c.value == 0
    assert g.value == 0


# ==========================================================
# Snapshot / Restore
# ==========================================================


def test_snapshot_restore():
    registry = MetricRegistry()

    counter = Counter("requests")

    registry.register(counter)

    counter.inc(5)

    snapshot = registry.snapshot()

    counter.inc(10)

    registry.restore(snapshot)

    assert counter.value == 5


# ==========================================================
# Clear
# ==========================================================


def test_clear_registry():
    registry = MetricRegistry()

    registry.register(Counter("a"))
    registry.register(Counter("b"))

    registry.clear()

    assert len(registry) == 0


# ==========================================================
# Names
# ==========================================================


def test_registry_names():
    registry = MetricRegistry()

    registry.register(Counter("requests"))
    registry.register(Gauge("cpu"))

    assert set(registry.names()) == {
        "requests",
        "cpu",
    }


# ==========================================================
# Values
# ==========================================================


def test_registry_values():
    registry = MetricRegistry()

    c = Counter("requests")
    g = Gauge("cpu")

    registry.register(c)
    registry.register(g)

    values = list(registry.values())

    assert c in values
    assert g in values


# ==========================================================
# Items
# ==========================================================


def test_registry_items():
    registry = MetricRegistry()

    counter = Counter("requests")

    registry.register(counter)

    items = dict(registry.items())

    assert items["requests"] is counter


# ==========================================================
# Thread safety
# ==========================================================


def test_thread_safe_registration():
    registry = MetricRegistry()

    def worker(idx: int):

        registry.register(
            Counter(f"metric_{idx}")
        )

    threads = [
        threading.Thread(
            target=worker,
            args=(i,),
        )
        for i in range(100)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert len(registry) == 100


def test_thread_safe_lookup():
    registry = MetricRegistry()

    for i in range(50):
        registry.register(
            Counter(f"metric_{i}")
        )

    errors = []

    def worker():

        for i in range(50):

            metric = registry.get(
                f"metric_{i}"
            )

            if metric is None:
                errors.append(i)

    threads = [
        threading.Thread(
            target=worker
        )
        for _ in range(20)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert errors == []


# ==========================================================
# Mixed metrics
# ==========================================================


def test_registry_accepts_multiple_metric_types():
    registry = MetricRegistry()

    registry.register(Counter("counter"))
    registry.register(Gauge("gauge"))
    registry.register(Histogram("histogram"))
    registry.register(Summary("summary"))
    registry.register(Timer("timer"))

    assert len(registry) == 5