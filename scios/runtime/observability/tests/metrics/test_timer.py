"""
SciOS Observability - Timer Tests
=================================

Unit tests for Timer metric.

Coverage
--------
- Construction
- Start / Stop
- Context manager
- Decorator
- Manual recording
- Statistics
- Reset
- Snapshot / Restore
- Thread safety
- Representation
"""

from __future__ import annotations

import threading
import time

import pytest

from scios.runtime.observability.metrics.timer import Timer


# ==========================================================
# Construction
# ==========================================================


def test_timer_starts_empty():
    timer = Timer("runtime")

    assert timer.count == 0
    assert timer.sum == 0


def test_timer_name():
    timer = Timer("runtime")

    assert timer.name == "runtime"


def test_timer_description():
    timer = Timer(
        "runtime",
        description="Runtime execution timer",
    )

    assert timer.description == "Runtime execution timer"


def test_timer_unit():
    timer = Timer(
        "runtime",
        unit="seconds",
    )

    assert timer.unit == "seconds"


# ==========================================================
# Manual Recording
# ==========================================================


@pytest.mark.parametrize(
    "duration",
    [
        0.0,
        0.001,
        0.1,
        1.0,
        2.5,
    ],
)
def test_record_duration(duration):
    timer = Timer("runtime")

    timer.record(duration)

    assert timer.count == 1
    assert timer.sum == pytest.approx(duration)


def test_multiple_recordings():
    timer = Timer("runtime")

    timer.record(1.0)
    timer.record(2.0)
    timer.record(3.0)

    assert timer.count == 3
    assert timer.sum == pytest.approx(6.0)


# ==========================================================
# Start / Stop
# ==========================================================


def test_start_stop():
    timer = Timer("runtime")

    timer.start()

    time.sleep(0.01)

    elapsed = timer.stop()

    assert elapsed > 0
    assert timer.count == 1


def test_stop_without_start_rejected():
    timer = Timer("runtime")

    with pytest.raises(RuntimeError):
        timer.stop()


def test_double_start_rejected():
    timer = Timer("runtime")

    timer.start()

    with pytest.raises(RuntimeError):
        timer.start()


# ==========================================================
# Context Manager
# ==========================================================


def test_context_manager():
    timer = Timer("runtime")

    with timer:

        time.sleep(0.01)

    assert timer.count == 1
    assert timer.sum > 0


# ==========================================================
# Decorator
# ==========================================================


def test_decorator():

    timer = Timer("runtime")

    @timer
    def work():

        time.sleep(0.01)

    work()

    assert timer.count == 1


# ==========================================================
# Statistics
# ==========================================================


def test_average():

    timer = Timer("runtime")

    timer.record(1)
    timer.record(2)
    timer.record(3)

    assert timer.average == pytest.approx(2)


def test_minimum():

    timer = Timer("runtime")

    timer.record(5)
    timer.record(2)
    timer.record(9)

    assert timer.minimum == 2


def test_maximum():

    timer = Timer("runtime")

    timer.record(5)
    timer.record(2)
    timer.record(9)

    assert timer.maximum == 9


# ==========================================================
# Reset
# ==========================================================


def test_reset():

    timer = Timer("runtime")

    timer.record(5)

    timer.reset()

    assert timer.count == 0
    assert timer.sum == 0


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot_restore():

    timer = Timer("runtime")

    timer.record(2)
    timer.record(3)

    snapshot = timer.snapshot()

    timer.record(10)

    timer.restore(snapshot)

    assert timer.count == 2
    assert timer.sum == pytest.approx(5)


# ==========================================================
# Thread Safety
# ==========================================================


def test_thread_safe_recording():

    timer = Timer("runtime")

    def worker():

        for _ in range(1000):
            timer.record(0.001)

    threads = [
        threading.Thread(target=worker)
        for _ in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert timer.count == 8000
    assert timer.sum == pytest.approx(
        8.0,
        rel=1e-3,
    )


# ==========================================================
# Representation
# ==========================================================


def test_repr_contains_name():

    timer = Timer("runtime")

    representation = repr(timer)

    assert "Timer" in representation
    assert "runtime" in representation