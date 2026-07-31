"""
SciOS Runtime Agent Integration Tests
=====================================

Tests Agent runtime integration:

- Agent creation
- Task execution
- Response contract
- Memory lifecycle
- Status diagnostics
- Run counter

Python 3.11+
"""


from scios.runtime.agent.agent import (
    Agent,
)



# ==========================================================
# Agent Run
# ==========================================================


def test_agent_run():

    agent = Agent()


    result = agent.run(
        "hello",
    )


    assert result is not None


    assert isinstance(
        result,
        dict,
    )


    assert result["task"] == (
        "hello"
    )


    assert result["status"] == (
        "completed"
    )


    assert result["agent"] == (
        "default-agent"
    )



# ==========================================================
# Agent Memory
# ==========================================================


def test_agent_memory():

    agent = Agent()


    agent.remember(
        "fact",
        "SciOS Runtime",
    )


    result = agent.recall(
        "fact",
    )


    assert result == (
        "SciOS Runtime"
    )



# ==========================================================
# Agent Status
# ==========================================================


def test_agent_status():

    agent = Agent()


    status = agent.status()


    assert isinstance(
        status,
        dict,
    )


    assert status["name"] == (
        "default-agent"
    )


    assert "state" in status


    assert "memory" in status


    assert "tools" in status


    assert "runs" in status



# ==========================================================
# Run Counter
# ==========================================================


def test_agent_run_counter():

    agent = Agent()


    assert agent.runs == 0



    agent.run(
        "task-1",
    )


    agent.run(
        "task-2",
    )


    assert agent.runs == 2



# ==========================================================
# Callable API
# ==========================================================


def test_agent_callable():

    agent = Agent()


    result = agent(
        "callable-task",
    )


    assert isinstance(
        result,
        dict,
    )


    assert result["task"] == (
        "callable-task"
    )


    assert result["status"] == (
        "completed"
    )