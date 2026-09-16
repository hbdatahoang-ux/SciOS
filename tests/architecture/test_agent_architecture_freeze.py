from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCIOS = ROOT / "scios"


def test_canonical_agent_is_agents_agent():
    from scios.agents.base import Agent

    assert Agent.__module__ == "scios.agents.base"


def test_runtime_agent_is_distinct_concrete_runtime_agent():
    from scios.agents.base import Agent as CanonicalAgent
    from scios.runtime.agent.agent import Agent as RuntimeAgent

    assert RuntimeAgent is not CanonicalAgent
    assert RuntimeAgent.__module__ == "scios.runtime.agent.agent"


def test_cognitive_planner_is_distinct_from_runtime_planner():
    from scios.cognitive_core.planner import Planner as CognitivePlanner
    from scios.runtime.agent.planner import Planner as RuntimePlanner

    assert CognitivePlanner is not RuntimePlanner


def test_runtime_agent_owns_runtime_state():
    from scios.runtime.agent.agent import Agent
    from scios.runtime.agent.state import AgentState

    agent = Agent()

    assert isinstance(agent.state, AgentState)


def test_runtime_agent_exposes_runtime_capabilities():
    from scios.runtime.agent.agent import Agent
    from scios.runtime.agent.memory import Memory
    from scios.runtime.agent.tool_router import ToolRouter

    agent = Agent()

    assert isinstance(agent.memory, Memory)
    assert isinstance(agent.tool_router, ToolRouter)


def test_cognitive_planner_does_not_depend_on_runtime_agent():
    planner_path = (
        SCIOS
        / "cognitive_core"
        / "planner"
    )

    forbidden = (
        "scios.runtime.agent",
        "runtime.agent",
        "ToolRouter",
        "AgentState",
    )

    for path in planner_path.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path}: forbidden dependency {token}"


def test_runtime_agent_does_not_replace_cognitive_planner():
    from scios.cognitive_core.planner import Planner as CognitivePlanner
    from scios.runtime.agent.agent import Agent

    agent = Agent()

    assert agent.planner.__class__ is not CognitivePlanner


def test_runtime_agent_adapter_is_not_canonical_agent():
    from scios.agents.base import Agent
    from scios.agents.adapters.runtime import RuntimeAgentAdapter

    assert RuntimeAgentAdapter is not Agent
    assert RuntimeAgentAdapter.__module__ == "scios.agents.adapters.runtime"
