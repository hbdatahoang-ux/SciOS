"""
Runtime Benchmarks

Run with:

pytest benchmarks/benchmark_runtime.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.kernel.runtime.engine import RuntimeEngine


@pytest.fixture
def runtime() -> RuntimeEngine:
    """
    Create a fresh runtime instance.
    """
    return RuntimeEngine()


def test_runtime_creation(benchmark):
    """
    Benchmark Runtime construction.
    """
    benchmark(RuntimeEngine)


def test_runtime_start(runtime: RuntimeEngine, benchmark):
    """
    Benchmark runtime startup.
    """
    benchmark(runtime.start)


def test_runtime_stop(runtime: RuntimeEngine, benchmark):
    """
    Benchmark runtime shutdown.
    """
    runtime.start()

    benchmark(runtime.stop)


def test_runtime_execute(runtime: RuntimeEngine, benchmark):
    """
    Benchmark execution of a lightweight task.
    """
    runtime.start()

    benchmark(runtime.execute, lambda: 42)


def test_runtime_status(runtime: RuntimeEngine, benchmark):
    """
    Benchmark status retrieval.
    """
    runtime.start()

    benchmark(runtime.status)


def test_runtime_restart(runtime: RuntimeEngine, benchmark):
    """
    Benchmark runtime restart.
    """
    runtime.start()

    benchmark(runtime.restart)