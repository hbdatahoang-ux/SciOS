"""
SciOS Observability - Summary Tests
==================================

Unit tests for Summary metric.

Coverage
--------
- Construction
- Observations
- Count / Sum
- Average
- Quantiles
- Labels
- Reset
- Snapshot / Restore
- Thread safety
- Representation
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.summary import Summary


# ==========================================================
# Construction
# ==========================================================


def test_summary_starts_empty():
    summary = Summary("request_duration")

    assert summary.count == 0
    assert summary.sum == 0


def test_summary_name():
    summary = Summary("request_duration")

    assert summary.name == "request_duration"


def test_summary_description():
    summary = Summary(
        "request_duration",
        description="HTTP latency summary",
    )

    assert summary.description == "HTTP latency summary"


def test_summary_unit():
    summary = Summary(
        "request_duration",
        unit="ms",
    )

    assert summary.unit == "ms"


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
        50,
        100,
    ],
)
def test_single_observation(value):
    summary = Summary("request_duration")

    summary.observe(value)

    assert summary.count == 1
    assert summary.sum == value


def test_multiple_observations():
    summary = Summary("request_duration")

    summary.observe(10)
    summary.observe(20)
    summary.observe(30)

    assert summary.count == 3
    assert summary.sum == 60


def test_zero_observation():
    summary = Summary("request_duration")

    summary.observe(0)

    assert summary.count == 1
    assert summary.sum == 0


def test_negative_observation_allowed():
    summary = Summary("temperature_delta")

    summary.observe(-5)

    assert summary.count == 1
    assert summary.sum == -5


# ==========================================================
# Statistics
# ==========================================================


def test_average():
    summary = Summary("request_duration")

    summary.observe(10)
    summary.observe(20)
    summary.observe(30)

    assert summary.average == pytest.approx(20)


# ==========================================================
# Quantiles
# ==========================================================


@pytest.fixture
def populated_summary():

    s = Summary("latency")

    for value in [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
    ]:
        s.observe(value)

    return s


def test_p50(populated_summary):

    assert populated_summary.quantile(0.50) == pytest.approx(
        55,
        abs=5,
    )


def test_p90(populated_summary):

    assert populated_summary.quantile(0.90) == pytest.approx(
        90,
        abs=5,
    )


def test_p95(populated_summary):

    assert populated_summary.quantile(0.95) == pytest.approx(
        95,
        abs=5,
    )


def test_p99(populated_summary):

    assert populated_summary.quantile(0.99) == pytest.approx(
        100,
        abs=5,
    )


@pytest.mark.parametrize(
    "q",
    [-0.1, 1.1],
)
def test_invalid_quantile_rejected(q):

    summary = Summary("latency")

    with pytest.raises(ValueError):
        summary.quantile(q)


# ==========================================================
# Labels
# ==========================================================


def test_labels_preserved():

    summary = Summary(
        "request_duration",
        labels={
            "endpoint": "/predict",
            "method": "POST",
        },
    )

    summary.observe(50)

    assert summary.labels["endpoint"] == "/predict"
    assert summary.labels["method"] == "POST"


# ==========================================================
# Reset
# ==========================================================


def test_reset():

    summary = Summary("latency")

    summary.observe(10)
    summary.observe(20)

    summary.reset()

    assert summary.count == 0
    assert summary.sum == 0


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot_restore():

    summary = Summary("latency")

    summary.observe(10)
    summary.observe(20)

    snapshot = summary.snapshot()

    summary.observe(100)

    summary.restore(snapshot)

    assert summary.count == 2
    assert summary.sum == 30


# ==========================================================
# Thread Safety
# ==========================================================


def test_thread_safe_observe():

    summary = Summary("latency")

    def worker():

        for _ in range(1000):
            summary.observe(1)

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert summary.count == 8000
    assert summary.sum == 8000


# ==========================================================
# Representation
# ==========================================================


def test_repr_contains_name():

    summary = Summary("latency")

    representation = repr(summary)

    assert "Summary" in representation
    assert "latency" in representation