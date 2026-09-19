"""
SciOS Observability - Counter Tests
==================================

Unit tests for Counter metric.

Coverage
--------
- Construction
- Increment semantics
- Labels
- Metadata
- Reset
- Snapshot / Restore
- Thread safety
- Validation
"""

from __future__ import annotations

import threading

import pytest

from scios.runtime.observability.metrics.counter import Counter


# ==========================================================
# Construction
# ==========================================================


def test_counter_starts_at_zero():
    counter = Counter("requests_total")

    assert counter.value == 0


def test_counter_name():
    counter = Counter("requests_total")

    assert counter.name == "requests_total"


def test_counter_description():
    counter = Counter(
        "requests_total",
        description="HTTP requests",
    )

    assert counter.description == "HTTP requests"


def test_counter_unit():
    counter = Counter(
        "requests_total",
        unit="requests",
    )

    assert counter.unit == "requests"


# ==========================================================
# Increment
# ==========================================================


def test_increment_by_one():
    counter = Counter("requests_total")

    counter.inc()

    assert counter.value == 1


@pytest.mark.parametrize(
    "amount",
    [1, 2, 5, 10, 100],
)
def test_increment_by_value(amount):
    counter = Counter("requests_total")

    counter.inc(amount)

    assert counter.value == amount


def test_multiple_increment():
    counter = Counter("requests_total")

    counter.inc()
    counter.inc(2)
    counter.inc(3)

    assert counter.value == 6


def test_zero_increment():
    counter = Counter("requests_total")

    counter.inc(0)

    assert counter.value == 0


def test_negative_increment_rejected():
    counter = Counter("requests_total")

    with pytest.raises(ValueError):
        counter.inc(-1)


# ==========================================================
# Labels
# ==========================================================


def test_labels_preserved():
    counter = Counter(
        "requests_total",
        labels={
            "method": "GET",
            "status": "200",
        },
    )

    counter.inc()

    assert counter.labels["method"] == "GET"
    assert counter.labels["status"] == "200"


def test_independent_label_sets():
    get_counter = Counter(
        "requests_total",
        labels={"method": "GET"},
    )

    post_counter = Counter(
        "requests_total",
        labels={"method": "POST"},
    )

    get_counter.inc()

    post_counter.inc(2)

    assert get_counter.value == 1
    assert post_counter.value == 2


# ==========================================================
# Reset
# ==========================================================


def test_reset():
    counter = Counter("requests_total")

    counter.inc(15)

    counter.reset()

    assert counter.value == 0


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot_restore():
    counter = Counter("requests_total")

    counter.inc(7)

    snapshot = counter.snapshot()

    counter.inc(5)

    counter.restore(snapshot)

    assert counter.value == 7


# ==========================================================
# Thread Safety
# ==========================================================


def test_thread_safe_increment():
    counter = Counter("requests_total")

    def worker():

        for _ in range(1000):
            counter.inc()

    threads = [
        threading.Thread(target=worker)
        for _ in range(5)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert counter.value == 5000


# ==========================================================
# Representation
# ==========================================================


def test_repr_contains_counter_name():
    counter = Counter("requests_total")

    representation = repr(counter)

    assert "Counter" in representation
    assert "requests_total" in representation