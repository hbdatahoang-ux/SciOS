"""
SciOS Runtime Benchmarks
========================

Run with:

    pytest benchmarks/benchmark_runtime.py --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.runtime import (
    ExecutionContext,
    ExecutionEngine,
    Pipeline,
    Stage,
)


class NoOpStage(Stage):
    """
    Minimal pipeline stage for benchmarking.
    """

    def execute(self, context: ExecutionContext) -> None:
        context.log("NoOpStage executed")
        context.set_result("ok")


@pytest.fixture
def engine() -> ExecutionEngine:
    """
    Create an execution engine with a minimal pipeline.
    """
    pipeline = Pipeline()
    pipeline.add_stage(NoOpStage())

    return ExecutionEngine(
        pipeline=pipeline,
    )


@pytest.fixture
def context() -> ExecutionContext:
    """
    Create a reusable execution context.
    """
    return ExecutionContext(
        task="benchmark task",
    )


# ----------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------

def test_execution_context_creation(benchmark):
    benchmark(
        ExecutionContext,
        "benchmark task",
    )


def test_execution_engine_creation(benchmark):
    benchmark(
        ExecutionEngine,
    )


# ----------------------------------------------------------------------
# Context operations
# ----------------------------------------------------------------------

def test_context_logging(context, benchmark):
    benchmark(
        context.log,
        "benchmark log message",
    )


def test_context_set_result(context, benchmark):
    benchmark(
        context.set_result,
        "result",
    )


# ----------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------

def test_pipeline_execution(engine, benchmark):
    benchmark(
        engine.pipeline.execute,
        ExecutionContext("pipeline benchmark"),
    )


# ----------------------------------------------------------------------
# Engine
# ----------------------------------------------------------------------

def test_engine_run(engine, benchmark):
    benchmark(
        engine.run,
        "runtime benchmark",
    )


def test_engine_execute(engine, benchmark):
    benchmark(
        engine.execute,
        "runtime benchmark",
    )