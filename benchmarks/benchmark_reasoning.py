"""
SciOS Reasoning Benchmarks

Run:

pytest benchmarks/benchmark_reasoning.py --benchmark-only
"""

from __future__ import annotations

from scios.cognitive_core.reasoning.core import ReasoningProblem
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.engine import ReasoningEngine
from scios.cognitive_core.reasoning.manager import ReasoningManager


def _problem(
    query: str = "benchmark reasoning query",
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE,
) -> ReasoningProblem:
    return ReasoningProblem(
        query=query,
        reasoning_type=reasoning_type,
    )


def test_benchmark_engine_creation(benchmark) -> None:
    benchmark(ReasoningEngine)


def test_benchmark_engine_execute(benchmark) -> None:
    engine = ReasoningEngine()
    problem = _problem()

    benchmark(engine.execute, problem)


def test_benchmark_engine_execute_inductive(benchmark) -> None:
    engine = ReasoningEngine()
    problem = _problem(
        reasoning_type=ReasoningType.INDUCTIVE,
    )

    benchmark(engine.execute, problem)


def test_benchmark_engine_execute_abductive(benchmark) -> None:
    engine = ReasoningEngine()
    problem = _problem(
        reasoning_type=ReasoningType.ABDUCTIVE,
    )

    benchmark(engine.execute, problem)


def test_benchmark_engine_get_strategy(benchmark) -> None:
    engine = ReasoningEngine()

    benchmark(
        engine.get_strategy,
        ReasoningType.DEDUCTIVE,
    )


def test_benchmark_manager_execute(benchmark) -> None:
    manager = ReasoningManager()
    problem = _problem()

    benchmark(manager.execute, problem)


def test_benchmark_manager_execute_inductive(benchmark) -> None:
    manager = ReasoningManager()
    problem = _problem(
        reasoning_type=ReasoningType.INDUCTIVE,
    )

    benchmark(manager.execute, problem)