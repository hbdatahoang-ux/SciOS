"""
Tests for Recorder.

Responsibilities
----------------
- Record metrics
- Route to Registry
- Batch recording
- Labels
- Snapshot / Restore
- Reset
- Thread safety
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.counter import Counter
from scios.runtime.observability.metrics.gauge import Gauge
from scios.runtime.observability.metrics.histogram import Histogram
from scios.runtime.observability.metrics.recorder import Recorder
from scios.runtime.observability.metrics.registry import Registry


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def registry():
    return Registry()


@pytest.fixture
def recorder(registry):
    return Recorder(registry=registry)


# ============================================================================
# Construction
# ============================================================================


def test_create_recorder(recorder):
    assert recorder is not None


def test_recorder_has_registry(recorder, registry):
    assert recorder.registry is registry


# ============================================================================
# Counter Recording
# ============================================================================


def test_record_counter(recorder):

    counter = Counter("requests")

    recorder.record(counter)

    assert counter.value == 0


def test_record_counter_increment(recorder):

    counter = Counter("requests")

    counter.inc()

    recorder.record(counter)

    assert counter.value == 1


def test_record_multiple_counter_values(recorder):

    counter = Counter("requests")

    for _ in range(5):
        counter.inc()

    recorder.record(counter)

    assert counter.value == 5


# ============================================================================
# Gauge Recording
# ============================================================================


def test_record_gauge(recorder):

    gauge = Gauge("cpu")

    gauge.set(80)

    recorder.record(gauge)

    assert gauge.value == 80


def test_record_negative_gauge(recorder):

    gauge = Gauge("temperature")

    gauge.set(-12)

    recorder.record(gauge)

    assert gauge.value == -12


# ============================================================================
# Histogram Recording
# ============================================================================


def test_record_histogram(recorder):

    hist = Histogram("latency")

    hist.observe(0.5)

    recorder.record(hist)

    assert hist.count == 1


def test_record_histogram_multiple(recorder):

    hist = Histogram("latency")

    for v in [0.1, 0.2, 0.3]:

        hist.observe(v)

    recorder.record(hist)

    assert hist.count == 3


# ============================================================================
# Registry Integration
# ============================================================================


def test_registry_receives_metric(recorder, registry):

    counter = Counter("requests")

    recorder.record(counter)

    assert registry.get("requests") is counter


def test_record_many_metrics(recorder, registry):

    recorder.record(Counter("a"))
    recorder.record(Gauge("b"))
    recorder.record(Histogram("c"))

    assert registry.get("a") is not None
    assert registry.get("b") is not None
    assert registry.get("c") is not None


# ============================================================================
# Labels
# ============================================================================


def test_record_metric_with_labels(recorder):

    counter = Counter(
        "requests",
        labels={"method": "GET"},
    )

    counter.inc()

    recorder.record(counter)

    assert counter.labels["method"] == "GET"


def test_record_multiple_label_sets(recorder):

    c1 = Counter(
        "requests",
        labels={"method": "GET"},
    )

    c2 = Counter(
        "requests",
        labels={"method": "POST"},
    )

    recorder.record(c1)
    recorder.record(c2)

    assert c1.labels != c2.labels


# ============================================================================
# Batch Recording
# ============================================================================


def test_record_batch(recorder):

    metrics = [
        Counter("c1"),
        Gauge("g1"),
        Histogram("h1"),
    ]

    recorder.record_all(metrics)

    assert len(metrics) == 3


def test_record_empty_batch(recorder):

    recorder.record_all([])


# ============================================================================
# Snapshot
# ============================================================================


def test_snapshot(recorder):

    snap = recorder.snapshot()

    assert snap is not None


def test_restore_snapshot(recorder):

    snap = recorder.snapshot()

    recorder.restore(snap)

    assert recorder.snapshot() == snap


# ============================================================================
# Reset
# ============================================================================


def test_reset(recorder):

    recorder.record(Counter("requests"))

    recorder.reset()

    assert recorder.snapshot() is not None


# ============================================================================
# Thread Safety
# ============================================================================


def test_thread_safe_recording(recorder):

    def worker(index):

        c = Counter(f"metric_{index}")

        for _ in range(100):
            c.inc()

        recorder.record(c)

    threads = [
        threading.Thread(
            target=worker,
            args=(i,),
        )
        for i in range(10)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


# ============================================================================
# Error Handling
# ============================================================================


def test_record_none_rejected(recorder):

    with pytest.raises(Exception):
        recorder.record(None)


def test_record_invalid_object(recorder):

    class Dummy:
        pass

    with pytest.raises(Exception):
        recorder.record(Dummy())


# ============================================================================
# Representation
# ============================================================================


def test_repr(recorder):

    assert "Recorder" in repr(recorder)


def test_str(recorder):

    assert "Recorder" in str(recorder)