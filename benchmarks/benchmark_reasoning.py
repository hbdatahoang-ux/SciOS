"""
SciOS Reasoning Benchmarks

Run:

pytest benchmarks/benchmark_reasoning.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.reasoning.engine import ReasoningEngine
from scios.reasoning.state import ReasoningState


@pytest.fixture
def engine():
    return ReasoningEngine()


@pytest.fixture
def state():
    return ReasoningState()


def test_reasoning_engine_creation(benchmark):
    """
    Benchmark engine construction.
    """
    benchmark(ReasoningEngine)


def test_reasoning_initialize(engine, benchmark):
    """
    Benchmark engine initialization.
    """
    benchmark(engine.initialize)


def test_reasoning_inference(engine, state, benchmark):
    """
    Benchmark inference.
    """
    benchmark(
        engine.infer,
        state,
    )


def test_reasoning_verification(engine, state, benchmark):
    """
    Benchmark verification.
    """
    benchmark(
        engine.verify,
        state,
    )


def test_reasoning_step(engine, state, benchmark):
    """
    Benchmark one reasoning iteration.
    """
    benchmark(
        engine.step,
        state,
    )


def test_reasoning_pipeline(engine, state, benchmark):
    """
    Benchmark complete reasoning pipeline.
    """

    def workload():

        engine.initialize()

        hypothesis = engine.infer(state)

        engine.verify(hypothesis)

    benchmark(workload)