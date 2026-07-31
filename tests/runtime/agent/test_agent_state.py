from scios.runtime.agent.state import AgentState


def test_default_state():

    state = AgentState()

    assert state.status == "idle"


def test_state_update():

    state = AgentState()

    state.update(
        status="running"
    )

    assert state.status == "running"