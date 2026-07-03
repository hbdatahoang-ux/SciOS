"""
Tests for SciOS Reasoning Engine
"""

from __future__ import annotations

import pytest

from scios.reasoning.engine import ReasoningEngine


@pytest.fixture
def engine() -> ReasoningEngine:
    """
    Create a fresh reasoning engine.
    """
    return ReasoningEngine()


def test_reasoning_creation(engine: ReasoningEngine):
    """
    Engine can be instantiated.
    """
    assert engine is not None


def test_reasoning_infer(engine: ReasoningEngine):
    """
    Engine performs inference.
    """
    state = {
        "value": 42,
    }

    result = engine.infer(state)

    assert result is not None


def test_reasoning_hypothesis(engine: ReasoningEngine):
    """
    Engine generates hypotheses.
    """
    hypotheses = engine.generate_hypotheses(
        {"goal": "optimize"}
    )

    assert isinstance(hypotheses, list)


def test_reasoning_verify(engine: ReasoningEngine):
    """
    Engine verifies a hypothesis.
    """
    hypothesis = {
        "statement": "A implies B"
    }

    result = engine.verify(hypothesis)

    assert isinstance(result, bool)


def test_reasoning_plan(engine: ReasoningEngine):
    """
    Engine generates an execution plan.
    """
    plan = engine.plan(
        {
            "goal": "solve"
        }
    )

    assert plan is not None


def test_reasoning_reset(engine: ReasoningEngine):
    """
    Reset engine state.
    """
    engine.reset()

    assert engine.state() == {}


def test_reasoning_status(engine: ReasoningEngine):
    """
    Engine exposes status.
    """
    status = engine.status()

    assert isinstance(status, dict)

    assert "running" in status


def test_reasoning_multiple_calls(engine: ReasoningEngine):
    """
    Multiple inference calls are supported.
    """
    for i in range(5):

        result = engine.infer(
            {
                "step": i
            }
        )

        assert result is not None