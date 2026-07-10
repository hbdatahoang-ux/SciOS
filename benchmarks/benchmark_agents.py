"""
SciOS Agent Runtime Benchmarks

Run:

pytest benchmarks/benchmark_agents.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.agents.base import BaseAgent


class DummyAgent(BaseAgent):
    """
    Lightweight benchmark agent.
    """

    def execute(self, task):
        return task


@pytest.fixture
def agent():
    return DummyAgent(name="benchmark-agent")


def test_agent_creation(benchmark):
    """
    Benchmark agent construction.
    """

    benchmark(
        lambda: DummyAgent(name="benchmark")
    )


def test_agent_execute(agent, benchmark):
    """
    Benchmark task execution.
    """

    benchmark(
        agent.execute,
        {"task": "demo"}
    )


def test_agent_status(agent, benchmark):
    """
    Benchmark status lookup.
    """

    benchmark(agent.status)


def test_agent_reset(agent, benchmark):
    """
    Benchmark state reset.
    """

    benchmark(agent.reset)


def test_agent_multiple_execution(agent, benchmark):
    """
    Benchmark repeated execution.
    """

    def workload():

        for i in range(100):
            agent.execute(i)

    benchmark(workload)
