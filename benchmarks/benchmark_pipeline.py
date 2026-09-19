"""
SciOS End-to-End Pipeline Benchmark

Run:

pytest benchmarks/benchmark_pipeline.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios import SciOS


@pytest.fixture(scope="session")
def system():
    """
    Create a booted SciOS instance once per benchmark session.
    """
    os = SciOS()
    os.boot()
    yield os
    os.shutdown()


def test_pipeline_small(system, benchmark):
    """
    Lightweight end-to-end request.
    """

    benchmark(
        system.run,
        "Summarize Newton's laws."
    )


def test_pipeline_medium(system, benchmark):
    """
    Medium reasoning workload.
    """

    benchmark(
        system.run,
        "Compare TCP and QUIC with advantages and disadvantages."
    )


def test_pipeline_large(system, benchmark):
    """
    Larger cognitive workload.
    """

    benchmark(
        system.run,
        """
        Design an autonomous multi-agent scheduling system
        with memory, planning, reasoning,
        observability and fault tolerance.
        """
    )
