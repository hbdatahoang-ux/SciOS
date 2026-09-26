"""
Kernel Benchmarks

Run with:

pytest benchmarks/benchmark_kernel.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.kernel.kernel import Kernel


@pytest.fixture
def kernel() -> Kernel:
    return Kernel()


def test_kernel_creation(benchmark):
    """
    Benchmark Kernel construction.
    """

    benchmark(Kernel)


def test_kernel_boot(kernel: Kernel, benchmark):
    """
    Benchmark boot sequence.
    """

    benchmark(kernel.boot)


def test_kernel_shutdown(kernel: Kernel, benchmark):
    """
    Benchmark shutdown.
    """

    kernel.boot()

    benchmark(kernel.shutdown)


def test_kernel_status(kernel: Kernel, benchmark):
    """
    Benchmark status query.
    """

    kernel.boot()

    benchmark(kernel.status)


def test_kernel_restart(kernel: Kernel, benchmark):
    """
    Benchmark restart.
    """

    kernel.boot()

    benchmark(kernel.restart)
