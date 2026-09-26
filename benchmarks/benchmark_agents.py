"""
SciOS Agent Runtime Benchmarks

Run:

pytest benchmarks/benchmark_agents.py --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.agents.base import BaseAgent


class DummyAgent(BaseAgent):
    """
    Lightweight concrete agent for benchmarks.
    """

    def run(self, task, *args, **kwargs):
        return task


@pytest.fixture
def agent():
    return DummyAgent(name="benchmark-agent")


def test_agent_creation(benchmark):
    """
    Benchmark agent construction.
    """
    benchmark(
        DummyAgent,
        name="benchmark",
    )


def test_agent_execute(agent, benchmark):
    """
    Benchmark framework execution wrapper.
    """
    benchmark(
        agent.execute,
        {"task": "demo"},
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
    Benchmark repeated framework execution.
    """

    def workload():
        for i in range(100):
            agent.execute(i)

    benchmark(workload)