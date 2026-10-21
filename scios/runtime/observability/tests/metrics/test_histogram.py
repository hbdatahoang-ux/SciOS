"""
SciOS Observability - Histogram Tests
====================================

Unit tests for Histogram metric.

Coverage
--------
- Construction
- Observations
- Bucket assignment
- Statistics
- Snapshot / Restore
- Reset
- Thread safety
- Representation
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.histogram import Histogram


# ==========================================================
# Construction
# ==========================================================


def test_histogram_starts_empty():
    histogram = Histogram("request_duration")

    assert histogram.count == 0
    assert histogram.sum == 0


def test_histogram_name():
    histogram = Histogram("request_duration")

    assert histogram.name == "request_duration"


def test_histogram_description():
    histogram = Histogram(
        "request_duration",
        description="HTTP request latency",
    )

    assert histogram.description == "HTTP request latency"


def test_histogram_unit():
    histogram = Histogram(
        "request_duration",
        unit="ms",
    )

    assert histogram.unit == "ms"


# ==========================================================
# Observe
# ==========================================================


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        5,
        10,
        25,
        100,
        1000,
    ],
)
def test_single_observation(value):
    histogram = Histogram("request_duration")

    histogram.observe(value)

    assert histogram.count == 1
    assert histogram.sum == value


def test_multiple_observations():
    histogram = Histogram("request_duration")

    histogram.observe(10)
    histogram.observe(20)
    histogram.observe(30)

    assert histogram.count == 3
    assert histogram.sum == 60


def test_zero_observation():
    histogram = Histogram("request_duration")

    histogram.observe(0)

    assert histogram.count == 1
    assert histogram.sum == 0


def test_negative_observation_allowed():
    histogram = Histogram("temperature_delta")

    histogram.observe(-5)

    assert histogram.count == 1
    assert histogram.sum == -5


# ==========================================================
# Statistics
# ==========================================================


def test_average():
    histogram = Histogram("request_duration")

    histogram.observe(10)
    histogram.observe(20)
    histogram.observe(30)

    assert histogram.average == pytest.approx(20)


def test_min():
    histogram = Histogram("request_duration")

    histogram.observe(50)
    histogram.observe(10)
    histogram.observe(30)

    assert histogram.minimum == 10


def test_max():
    histogram = Histogram("request_duration")

    histogram.observe(50)
    histogram.observe(10)
    histogram.observe(30)

    assert histogram.maximum == 50


# ==========================================================
# Buckets
# ==========================================================


def test_bucket_assignment():
    histogram = Histogram(
        "request_duration",
        buckets=[10, 50, 100],
    )

    histogram.observe(7)
    histogram.observe(25)
    histogram.observe(80)

    assert histogram.bucket_count(10) == 1
    assert histogram.bucket_count(50) == 1
    assert histogram.bucket_count(100) == 1


def test_custom_buckets():
    histogram = Histogram(
        "payload",
        buckets=[1, 5, 10, 20],
    )

    histogram.observe(2)
    histogram.observe(8)
    histogram.observe(19)

    assert histogram.count == 3


# ==========================================================
# Labels
# ==========================================================


def test_labels_preserved():
    histogram = Histogram(
        "request_duration",
        labels={
            "endpoint": "/login",
            "method": "GET",
        },
    )

    histogram.observe(20)

    assert histogram.labels["endpoint"] == "/login"
    assert histogram.labels["method"] == "GET"


# ==========================================================
# Reset
# ==========================================================


def test_reset():
    histogram = Histogram("request_duration")

    histogram.observe(10)
    histogram.observe(20)

    histogram.reset()

    assert histogram.count == 0
    assert histogram.sum == 0


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot_restore():
    histogram = Histogram("request_duration")

    histogram.observe(5)
    histogram.observe(15)

    snapshot = histogram.snapshot()

    histogram.observe(50)

    histogram.restore(snapshot)

    assert histogram.count == 2
    assert histogram.sum == 20


# ==========================================================
# Thread Safety
# ==========================================================


def test_thread_safe_observe():
    histogram = Histogram("request_duration")

    def worker():

        for _ in range(1000):
            histogram.observe(1)

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert histogram.count == 8000
    assert histogram.sum == 8000


# ==========================================================
# Representation
# ==========================================================


def test_repr_contains_name():
    histogram = Histogram("request_duration")

    representation = repr(histogram)

    assert "Histogram" in representation
    assert "request_duration" in representation