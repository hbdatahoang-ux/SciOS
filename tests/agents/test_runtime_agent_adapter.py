from __future__ import annotations

import pytest

from scios.agents.adapters.runtime import RuntimeAgentAdapter
from scios.runtime.agent.agent import Agent as RuntimeAgent
from scios.runtime.agent.memory import Memory
from scios.runtime.agent.tool_router import ToolRouter


def make_adapter(**kwargs):
    return RuntimeAgentAdapter(
        name="adapter-test",
        **kwargs,
    )


def test_runtime_agent_adapter_identity_and_dependencies():
    memory = Memory()
    router = ToolRouter()
    runtime_agent = RuntimeAgent(
        name="runtime-test",
        memory=memory,
        router=router,
    )

    agent = make_adapter(
        memory=memory,
        router=router,
        runtime_agent=runtime_agent,
    )

    assert agent.name == "adapter-test"
    assert agent.version == "0.3.0"
    assert agent.memory is memory
    assert agent.router is router
    assert agent.tool_router is router
    assert agent.runtime_agent is runtime_agent


def test_initial_agency_state():
    agent = make_adapter()

    assert agent.state == "idle"
    assert agent.enabled is True
    assert agent.executions == 0


def test_execute_owns_agency_execution_counter():
    agent = make_adapter()

    result = agent.execute("hello")

    assert result["status"] in {"completed", "failed"}
    assert agent.executions == 1
    assert agent.state == "idle"


def test_call_delegates_through_execute():
    agent = make_adapter()

    result = agent("hello")

    assert result["status"] in {"completed", "failed"}
    assert agent.executions == 1
    assert agent.state == "idle"


def test_execute_tool_does_not_increment_agent_executions():
    agent = make_adapter()

    before = agent.executions
    result = agent.execute_tool("missing")

    assert result is not None
    assert agent.executions == before


def test_memory_delegation():
    memory = Memory()
    agent = make_adapter(memory=memory)

    agent.remember("key", "value")

    assert agent.memory is memory
    assert agent.recall("key") == "value"
    assert agent.recall("missing", "default") == "default"


def test_disable_rejects_execute():
    agent = make_adapter()

    agent.disable()

    assert agent.enabled is False

    with pytest.raises(RuntimeError):
        agent.execute("hello")

    assert agent.executions == 0
    assert agent.state == "idle"


def test_enable_restores_execution():
    agent = make_adapter()

    agent.disable()
    agent.enable()

    assert agent.enabled is True

    result = agent.execute("hello")

    assert result["status"] in {"completed", "failed"}
    assert agent.executions == 1
    assert agent.state == "idle"


def test_reset_restores_agency_state_and_execution_counter():
    agent = make_adapter()

    agent.execute("hello")
    assert agent.executions == 1

    agent.reset()

    assert agent.state == "idle"
    assert agent.executions == 0
    assert agent.enabled is True


def test_status_has_canonical_agency_schema():
    agent = make_adapter()

    status = agent.status()

    assert set(status) == {
        "id",
        "name",
        "version",
        "state",
        "enabled",
        "executions",
        "created_at",
    }


def test_runtime_runs_are_not_agency_executions():
    agent = make_adapter()

    assert agent.executions == 0
    assert agent.runtime_agent.runs == 0

    agent.execute("hello")

    assert agent.executions == 1
    assert agent.runtime_agent.runs == 1


def test_tool_execution_does_not_count_as_agency_execution():
    agent = make_adapter()

    agent.execute_tool("missing")

    assert agent.executions == 0
    assert agent.runtime_agent.runs == 0


def test_id_is_string_compatible_with_base_agent():
    agent = make_adapter()

    assert isinstance(agent.id, str)


def test_repr_is_stable_and_informative():
    agent = make_adapter()

    value = repr(agent)

    assert "RuntimeAgentAdapter" in value
    assert "adapter-test" in value
    assert "0.3.0" in value
    assert "idle" in value


def test_positional_execution_arguments_are_explicitly_rejected():
    agent = make_adapter()

    with pytest.raises(
        TypeError,
        match="does not support positional execution arguments",
    ):
        agent.execute("hello", 1, 2)

    assert agent.executions == 1
    assert agent.state == "idle"
