"""
SciOS Memory Benchmarks

Run:

pytest benchmarks/benchmark_memory.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.memory.working import WorkingMemory


@pytest.fixture
def memory():
    return WorkingMemory()


def test_memory_creation(benchmark):
    """
    Benchmark memory construction.
    """
    benchmark(WorkingMemory)


def test_memory_store(memory, benchmark):
    """
    Benchmark store().
    """
    benchmark(
        memory.store,
        "key",
        "value",
    )


def test_memory_retrieve(memory, benchmark):
    """
    Benchmark retrieve().
    """
    memory.store("key", "value")

    benchmark(
        memory.retrieve,
        "key",
    )


def test_memory_update(memory, benchmark):
    """
    Benchmark update().
    """
    memory.store("key", "old")

    def workload():
        memory.store("key", "new")

    benchmark(workload)


def test_memory_delete(memory, benchmark):
    """
    Benchmark delete().
    """
    memory.store("key", "value")

    benchmark(
        memory.delete,
        "key",
    )


def test_memory_clear(memory, benchmark):
    """
    Benchmark clear().
    """
    for i in range(1000):
        memory.store(f"k{i}", i)

    benchmark(memory.clear)


def test_memory_bulk_insert(memory, benchmark):
    """
    Benchmark bulk insertion.
    """

    def workload():

        for i in range(1000):
            memory.store(f"key-{i}", i)

    benchmark(workload)


def test_memory_status(memory, benchmark):
    """
    Benchmark status().
    """
    benchmark(memory.status)
