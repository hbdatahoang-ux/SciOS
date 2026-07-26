"""
SciOS Observability - Gauge Tests
================================

Unit tests for Gauge metric.

Coverage
--------
- Construction
- Value updates
- Increment / Decrement
- Labels
- Reset
- Snapshot / Restore
- Thread safety
- Representation
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.gauge import Gauge


# ==========================================================
# Construction
# ==========================================================


def test_gauge_starts_at_zero():
    gauge = Gauge("temperature")

    assert gauge.value == 0


def test_gauge_name():
    gauge = Gauge("temperature")

    assert gauge.name == "temperature"


def test_gauge_description():
    gauge = Gauge(
        "temperature",
        description="CPU temperature",
    )

    assert gauge.description == "CPU temperature"


def test_gauge_unit():
    gauge = Gauge(
        "temperature",
        unit="°C",
    )

    assert gauge.unit == "°C"


# ==========================================================
# Set Value
# ==========================================================


@pytest.mark.parametrize(
    "value",
    [
        -100,
        -10,
        0,
        5,
        25,
        36.5,
        100,
    ],
)
def test_set_value(value):
    gauge = Gauge("temperature")

    gauge.set(value)

    assert gauge.value == value


# ==========================================================
# Increment
# ==========================================================


def test_increment():
    gauge = Gauge("temperature")

    gauge.inc()

    assert gauge.value == 1


@pytest.mark.parametrize(
    "amount",
    [1, 2, 5, 10],
)
def test_increment_by_value(amount):
    gauge = Gauge("temperature")

    gauge.inc(amount)

    assert gauge.value == amount


# ==========================================================
# Decrement
# ==========================================================


def test_decrement():
    gauge = Gauge("temperature")

    gauge.dec()

    assert gauge.value == -1


@pytest.mark.parametrize(
    "amount",
    [1, 2, 5, 10],
)
def test_decrement_by_value(amount):
    gauge = Gauge("temperature")

    gauge.dec(amount)

    assert gauge.value == -amount


# ==========================================================
# Reset
# ==========================================================


def test_reset():
    gauge = Gauge("temperature")

    gauge.set(42)

    gauge.reset()

    assert gauge.value == 0


# ==========================================================
# Labels
# ==========================================================


def test_labels_preserved():
    gauge = Gauge(
        "temperature",
        labels={
            "room": "A",
            "sensor": "cpu",
        },
    )

    gauge.set(30)

    assert gauge.labels["room"] == "A"
    assert gauge.labels["sensor"] == "cpu"


def test_independent_label_sets():
    room_a = Gauge(
        "temperature",
        labels={"room": "A"},
    )

    room_b = Gauge(
        "temperature",
        labels={"room": "B"},
    )

    room_a.set(20)
    room_b.set(35)

    assert room_a.value == 20
    assert room_b.value == 35


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot_restore():
    gauge = Gauge("temperature")

    gauge.set(55)

    snapshot = gauge.snapshot()

    gauge.set(99)

    gauge.restore(snapshot)

    assert gauge.value == 55


# ==========================================================
# Thread Safety
# ==========================================================


def test_thread_safe_updates():
    gauge = Gauge("temperature")

    def worker():

        for _ in range(1000):
            gauge.inc()
            gauge.dec()

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert gauge.value == 0


# ==========================================================
# Representation
# ==========================================================


def test_repr_contains_name():
    gauge = Gauge("temperature")

    representation = repr(gauge)

    assert "Gauge" in representation
    assert "temperature" in representation