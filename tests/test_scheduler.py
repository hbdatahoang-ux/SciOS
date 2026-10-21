"""
SciOS Runtime Scheduler Tests
=============================

Unit tests for the SciOS Runtime scheduler.

The scheduler is responsible for managing queued execution contexts
and selecting the next context for execution. These tests validate
the runtime scheduler contract independently from the execution engine,
worker, pipeline, and kernel scheduler.

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.exceptions import QueueEmptyError
from scios.runtime.scheduler import Scheduler


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
    Scheduler should start with an empty queue and zero statistics.
    """

    scheduler = Scheduler()

    assert scheduler.empty()
    assert scheduler.pending == 0
    assert scheduler.submitted == 0
    assert scheduler.completed == 0
    assert len(scheduler) == 0


# ==========================================================
# Submit Task
# ==========================================================


def test_submit_task() -> None:
    """
    A submitted execution context should appear in the queue.
    """

    scheduler = Scheduler()

    scheduler.submit("task-1")

    assert not scheduler.empty()
    assert scheduler.pending == 1
    assert len(scheduler) == 1
    assert scheduler.submitted == 1


# ==========================================================
# FIFO Order
# ==========================================================


def test_fifo_order() -> None:
    """
    Runtime scheduler should execute tasks in FIFO order.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")
    scheduler.submit("C")

    assert scheduler.next() == "A"
    assert scheduler.next() == "B"
    assert scheduler.next() == "C"

    assert scheduler.empty()
    assert scheduler.pending == 0
    assert scheduler.submitted == 3


# ==========================================================
# Queue Length
# ==========================================================


def test_queue_length() -> None:
    """
    Queue length should be updated correctly after submissions.
    """

    scheduler = Scheduler()

    for i in range(10):
        scheduler.submit(i)

    assert len(scheduler) == 10
    assert scheduler.pending == 10
    assert scheduler.size() == 10
    assert scheduler.submitted == 10


# ==========================================================
# Clear Queue
# ==========================================================


def test_clear_queue() -> None:
    """
    Clearing the scheduler should remove all queued tasks.

    Clearing the queue must not erase submission statistics.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")

    scheduler.clear()

    assert scheduler.empty()
    assert scheduler.pending == 0
    assert len(scheduler) == 0
    assert scheduler.submitted == 2


# ==========================================================
# Next On Empty Queue
# ==========================================================


def test_next_empty_queue() -> None:
    """
    Requesting the next task from an empty queue should raise
    QueueEmptyError.
    """

    scheduler = Scheduler()

    with pytest.raises(QueueEmptyError):
        scheduler.next()


# ==========================================================
# Peek
# ==========================================================


def test_peek_does_not_remove_task() -> None:
    """
    peek() should return the next task without removing it.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")

    assert scheduler.peek() == "A"
    assert scheduler.pending == 2
    assert len(scheduler) == 2

    assert scheduler.next() == "A"
    assert scheduler.next() == "B"


def test_peek_empty_queue() -> None:
    """
    peek() should return None for an empty queue.
    """

    scheduler = Scheduler()

    assert scheduler.peek() is None


# ==========================================================
# Complete
# ==========================================================


def test_complete_updates_completed_count() -> None:
    """
    Completing a scheduled context should increment the completed
    execution counter.
    """

    scheduler = Scheduler()

    scheduler.submit("task")

    context = scheduler.next()

    assert scheduler.completed == 0

    scheduler.complete(context)

    assert scheduler.completed == 1
    assert scheduler.pending == 0


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
        "submitted",
        "completed",
        "pending",
        "queue_size",
    }

    assert required.issubset(status.keys())

    assert status["submitted"] == 1
    assert status["completed"] == 0
    assert status["pending"] == 1
    assert status["queue_size"] == 1


# ==========================================================
# Reuse After Clear
# ==========================================================


def test_reuse_after_clear() -> None:
    """
    Scheduler should remain usable after clearing its queue.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.clear()

    scheduler.submit("B")

    assert scheduler.next() == "B"
    assert scheduler.empty()
    assert scheduler.submitted == 2


# ==========================================================
# Multiple Operations
# ==========================================================


def test_multiple_submit_pop() -> None:
    """
    Scheduler should remain consistent after many FIFO operations.
    """

    scheduler = Scheduler()

    for i in range(100):
        scheduler.submit(i)

    assert scheduler.pending == 100
    assert scheduler.submitted == 100

    for i in range(100):
        assert scheduler.next() == i

    assert scheduler.empty()
    assert scheduler.pending == 0
    assert scheduler.submitted == 100


# ==========================================================
# Queue Size
# ==========================================================


def test_queue_size_property() -> None:
    """
    size() and pending should match __len__().
    """

    scheduler = Scheduler()

    for i in range(7):
        scheduler.submit(i)

    assert scheduler.size() == len(scheduler)
    assert scheduler.pending == len(scheduler)
    assert scheduler.status()["queue_size"] == len(scheduler)


# ==========================================================
# Iteration
# ==========================================================


def test_scheduler_iteration() -> None:
    """
    Iteration should expose queued tasks without consuming them.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")
    scheduler.submit("C")

    assert list(scheduler) == [
        "A",
        "B",
        "C",
    ]

    assert scheduler.pending == 3


# ==========================================================
# Membership
# ==========================================================


def test_scheduler_contains_queued_task() -> None:
    """
    Membership checks should reflect queued tasks.
    """

    scheduler = Scheduler()

    scheduler.submit("A")

    assert "A" in scheduler
    assert "B" not in scheduler

    scheduler.next()

    assert "A" not in scheduler


# ==========================================================
# Boolean State
# ==========================================================


def test_scheduler_bool_state() -> None:
    """
    Scheduler should be truthy when tasks are pending and falsy when
    the queue is empty.
    """

    scheduler = Scheduler()

    assert not scheduler

    scheduler.submit("A")

    assert scheduler

    scheduler.next()

    assert not scheduler


# ==========================================================
# FIFO After Peek
# ==========================================================


def test_fifo_order_after_peek() -> None:
    """
    Peeking should not alter FIFO ordering.
    """

    scheduler = Scheduler()

    scheduler.submit("A")
    scheduler.submit("B")
    scheduler.submit("C")

    assert scheduler.peek() == "A"
    assert scheduler.next() == "A"

    assert scheduler.peek() == "B"
    assert scheduler.next() == "B"

    assert scheduler.next() == "C"

    assert scheduler.empty()