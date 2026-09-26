"""
Tests for Aggregator.

SciOS Observability
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.aggregator import Aggregator
from scios.runtime.observability.metrics.counter import Counter
from scios.runtime.observability.metrics.gauge import Gauge


# ============================================================================
# Construction
# ============================================================================


def test_empty_aggregator():

    agg = Aggregator()

    assert len(agg) == 0


def test_repr():

    agg = Aggregator()

    assert "Aggregator" in repr(agg)


# ============================================================================
# Registration
# ============================================================================


def test_add_metric():

    agg = Aggregator()

    c = Counter("requests")

    agg.add(c)

    assert len(agg) == 1


def test_add_multiple_metrics():

    agg = Aggregator()

    agg.add(Counter("a"))
    agg.add(Gauge("b"))

    assert len(agg) == 2


def test_duplicate_metric_rejected():

    agg = Aggregator()

    c = Counter("requests")

    agg.add(c)

    with pytest.raises(Exception):
        agg.add(c)


def test_contains_metric():

    agg = Aggregator()

    c = Counter("requests")

    agg.add(c)

    assert c in agg


# ============================================================================
# Remove
# ============================================================================


def test_remove_metric():

    agg = Aggregator()

    c = Counter("requests")

    agg.add(c)

    agg.remove(c)

    assert len(agg) == 0


def test_remove_unknown_metric():

    agg = Aggregator()

    c = Counter("requests")

    agg.remove(c)

    assert len(agg) == 0


def test_clear():

    agg = Aggregator()

    agg.add(Counter("a"))
    agg.add(Counter("b"))

    agg.clear()

    assert len(agg) == 0


# ============================================================================
# Iteration
# ============================================================================


def test_iteration():

    agg = Aggregator()

    agg.add(Counter("a"))
    agg.add(Counter("b"))

    names = [m.name for m in agg]

    assert names == ["a", "b"]


def test_getitem():

    agg = Aggregator()

    c = Counter("requests")

    agg.add(c)

    assert agg["requests"] is c


def test_unknown_metric_lookup():

    agg = Aggregator()

    with pytest.raises(KeyError):
        agg["missing"]


# ============================================================================
# Snapshot
# ============================================================================


def test_snapshot():

    agg = Aggregator()

    c = Counter("requests")

    c.inc(5)

    agg.add(c)

    snap = agg.snapshot()

    assert isinstance(snap, dict)

    assert "requests" in snap


def test_restore_snapshot():

    agg = Aggregator()

    c = Counter("requests")

    c.inc(5)

    agg.add(c)

    snap = agg.snapshot()

    c.inc(10)

    agg.restore(snap)

    assert c.value == 5


# ============================================================================
# Aggregation
# ============================================================================


def test_total_counter_value():

    agg = Aggregator()

    c1 = Counter("a")
    c2 = Counter("b")

    c1.inc(3)
    c2.inc(7)

    agg.add(c1)
    agg.add(c2)

    assert agg.total() == 10


def test_empty_total():

    agg = Aggregator()

    assert agg.total() == 0


# ============================================================================
# Export
# ============================================================================


def test_export():

    agg = Aggregator()

    c = Counter("requests")

    c.inc(2)

    agg.add(c)

    data = agg.export()

    assert isinstance(data, dict)


def test_export_empty():

    agg = Aggregator()

    assert agg.export() == {}


# ============================================================================
# Thread Safety
# ============================================================================


def test_concurrent_registration():

    agg = Aggregator()

    def worker(i):

        agg.add(
            Counter(f"metric_{i}")
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

    assert len(agg) == 100


def test_concurrent_snapshot():

    agg = Aggregator()

    for i in range(50):
        agg.add(Counter(f"m{i}"))

    def worker():

        for _ in range(100):
            agg.snapshot()

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert len(agg) == 50


# ============================================================================
# Robustness
# ============================================================================


def test_reset():

    agg = Aggregator()

    c = Counter("requests")

    c.inc(10)

    agg.add(c)

    agg.reset()

    assert c.value == 0


def test_bool():

    agg = Aggregator()

    assert not agg

    agg.add(Counter("a"))

    assert agg


def test_len():

    agg = Aggregator()

    assert len(agg) == 0

    agg.add(Counter("a"))

    assert len(agg) == 1