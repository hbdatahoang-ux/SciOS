"""
SciOS Runtime Agent Tests
=========================

Python 3.11+
"""

from scios.runtime.agent.agent import Agent


# ==========================================================
# Creation
# ==========================================================


def test_agent_creation():

    agent = Agent(
        name="test-agent"
    )

    assert agent.name == "test-agent"



# ==========================================================
# Run
# ==========================================================


def test_agent_run():

    agent = Agent(
        name="test-agent"
    )

    result = agent.run(
        "hello"
    )

    assert result is not None



# ==========================================================
# Status
# ==========================================================


def test_agent_status():

    agent = Agent(
        name="test-agent"
    )

    status = agent.status()

    assert status["name"] == "test-agent"



# ==========================================================
# Memory Integration
# ==========================================================


def test_agent_memory():

    agent = Agent(
        name="memory-agent"
    )


    agent.remember(
        "key",
        "value",
    )


    result = agent.recall(
        "key"
    )


    assert result is not None