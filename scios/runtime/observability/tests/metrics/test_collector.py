"""
SciOS Observability Tests
=========================

Tests for MetricCollector.

Coverage
--------
- Registration
- Recording
- Lookup
- Snapshot
- Reset
- Merge
- Thread safety
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.collector import MetricCollector
from scios.runtime.observability.metrics.counter import Counter
from scios.runtime.observability.metrics.gauge import Gauge
from scios.runtime.observability.metrics.histogram import Histogram


# ============================================================
# Construction
# ============================================================


def test_collector_initial_state():
    collector = MetricCollector()

    assert len(collector) == 0


def test_collector_is_empty():
    collector = MetricCollector()

    assert collector.empty


# ============================================================
# Registration
# ============================================================


def test_register_counter():
    collector = MetricCollector()

    counter = Counter("requests")

    collector.register(counter)

    assert collector.get("requests") is counter


def test_register_gauge():
    collector = MetricCollector()

    gauge = Gauge("temperature")

    collector.register(gauge)

    assert collector.get("temperature") is gauge


def test_register_histogram():
    collector = MetricCollector()

    hist = Histogram("latency")

    collector.register(hist)

    assert collector.get("latency") is hist


def test_register_duplicate_rejected():
    collector = MetricCollector()

    collector.register(Counter("requests"))

    with pytest.raises(ValueError):
        collector.register(Counter("requests"))


# ============================================================
# Lookup
# ============================================================


def test_get_existing_metric():
    collector = MetricCollector()

    counter = Counter("hits")

    collector.register(counter)

    assert collector.get("hits") is counter


def test_get_unknown_metric_returns_none():
    collector = MetricCollector()

    assert collector.get("missing") is None


def test_contains_metric():
    collector = MetricCollector()

    collector.register(Counter("hits"))

    assert "hits" in collector


# ============================================================
# Remove
# ============================================================


def test_remove_metric():
    collector = MetricCollector()

    collector.register(Counter("hits"))

    assert collector.remove("hits")

    assert collector.get("hits") is None


def test_remove_unknown_metric():
    collector = MetricCollector()

    assert collector.remove("abc") is False


# ============================================================
# Iteration
# ============================================================


def test_iteration():
    collector = MetricCollector()

    collector.register(Counter("a"))
    collector.register(Counter("b"))

    names = {
        metric.name
        for metric in collector
    }

    assert names == {
        "a",
        "b",
    }


# ============================================================
# Snapshot
# ============================================================


def test_snapshot():
    collector = MetricCollector()

    c = Counter("requests")

    collector.register(c)

    c.inc(5)

    snap = collector.snapshot()

    assert "requests" in snap


def test_restore_snapshot():
    collector = MetricCollector()

    c = Counter("requests")

    collector.register(c)

    c.inc(3)

    snap = collector.snapshot()

    c.inc(10)

    collector.restore(snap)

    restored = collector.get("requests")

    assert restored.value == 3


# ============================================================
# Reset
# ============================================================


def test_reset():
    collector = MetricCollector()

    c = Counter("requests")

    collector.register(c)

    c.inc(100)

    collector.reset()

    assert collector.get("requests").value == 0


def test_clear():
    collector = MetricCollector()

    collector.register(Counter("a"))
    collector.register(Counter("b"))

    collector.clear()

    assert len(collector) == 0


# ============================================================
# Merge
# ============================================================


def test_merge_collectors():
    left = MetricCollector()
    right = MetricCollector()

    left.register(Counter("a"))
    right.register(Counter("b"))

    left.merge(right)

    assert left.get("a") is not None
    assert left.get("b") is not None


# ============================================================
# Thread Safety
# ============================================================


def test_concurrent_registration():
    collector = MetricCollector()

    def worker(idx: int):
        collector.register(
            Counter(f"metric_{idx}")
        )

    threads = [
        threading.Thread(
            target=worker,
            args=(i,),
        )
        for i in range(50)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert len(collector) == 50


def test_concurrent_updates():
    collector = MetricCollector()

    counter = Counter("requests")

    collector.register(counter)

    def worker():
        for _ in range(1000):
            collector.get("requests").inc()

    threads = [
        threading.Thread(target=worker)
        for _ in range(5)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert counter.value == 5000


# ============================================================
# Representation
# ============================================================


def test_repr():
    collector = MetricCollector()

    collector.register(Counter("requests"))

    text = repr(collector)

    assert "MetricCollector" in text
    assert "requests" in text


# ============================================================
# Robustness
# ============================================================


def test_register_none_rejected():
    collector = MetricCollector()

    with pytest.raises(TypeError):
        collector.register(None)


def test_merge_empty_collector():
    left = MetricCollector()
    right = MetricCollector()

    left.merge(right)

    assert len(left) == 0


def test_snapshot_empty():
    collector = MetricCollector()

    snap = collector.snapshot()

    assert snap == {}