"""
SciOS Scheduler Tests
=====================

Unit tests for the SciOS task scheduler.

The scheduler is responsible for managing queued tasks and selecting
the next task for execution. These tests validate only the scheduler
contract and are independent of the runtime and kernel.
"""

from __future__ import annotations

import pytest

from scios.kernel.scheduler import Scheduler


# ==========================================================
# Construction
# ==========================================================

def test_scheduler_construction() -> None:
    """
    Scheduler should be constructible.
    """

    scheduler = Scheduler()

    assert scheduler is not None


# ==========================================================
# Initial State
# ==========================================================

def test_scheduler_initial_state() -> None:
    """
    Scheduler should start empty.
    """

    scheduler = Scheduler()

    assert scheduler.empty()
    assert len(scheduler) == 0


# ==========================================================
# Submit Task
# ==========================================================

def test_submit_task() -> None:
    """
    A submitted task should appear in the queue.
    """

    scheduler = Scheduler()

    scheduler.submit("task-1")

    assert not scheduler.empty()
    assert len(scheduler) == 1


# ==========================================================
# FIFO Order
# ==========================================================

def test_fifo_order() -> None:
    """
    Default scheduler should execute FIFO.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")
    scheduler.submit("C")

    assert scheduler.next() == "A"
    assert scheduler.next() == "B"
    assert scheduler.next() == "C"

    assert scheduler.empty()


# ==========================================================
# Queue Length
# ==========================================================

def test_queue_length() -> None:
    """
    Queue length should be updated correctly.
    """

    scheduler = Scheduler()

    for i in range(10):
        scheduler.submit(i)

    assert len(scheduler) == 10


# ==========================================================
# Clear Queue
# ==========================================================

def test_clear_queue() -> None:
    """
    Clearing the scheduler should remove all tasks.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")

    scheduler.clear()

    assert scheduler.empty()
    assert len(scheduler) == 0


# ==========================================================
# Next On Empty Queue
# ==========================================================

def test_next_empty_queue() -> None:
    """
    Requesting the next task from an empty queue should fail.
    """

    scheduler = Scheduler()

    with pytest.raises(Exception):
        scheduler.next()


# ==========================================================
# Status
# ==========================================================

def test_scheduler_status() -> None:
    """
    Scheduler should expose a stable status schema.
    """

    scheduler = Scheduler()

    scheduler.submit("task")

    status = scheduler.status()

    assert isinstance(status, dict)

    required = {
        "queued",
        "policy",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Reuse After Clear
# ==========================================================

def test_reuse_after_clear() -> None:
    """
    Scheduler should remain usable after clearing.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.clear()

    scheduler.submit("B")

    assert scheduler.next() == "B"


# ==========================================================
# Multiple Operations
# ==========================================================

def test_multiple_submit_pop() -> None:
    """
    Scheduler should remain consistent after many operations.
    """

    scheduler = Scheduler()

    for i in range(100):
        scheduler.submit(i)

    for i in range(100):
        assert scheduler.next() == i

    assert scheduler.empty()


# ==========================================================
# Queue Size Property
# ==========================================================

def test_queue_size_property() -> None:
    """
    Queue size should match __len__().
    """

    scheduler = Scheduler()

    for i in range(7):
        scheduler.submit(i)

    assert scheduler.status()["queued"] == len(scheduler)