import pytest

from scios.cognitive_core.reflection.state import ReflectionState


def test_reflection_state_initialization():
    state = ReflectionState()

    assert state.get_state() == "idle"
    assert state.is_idle()
    assert not state.is_reflecting()
    assert not state.is_completed()
    assert not state.is_error()


@pytest.mark.parametrize(
    "value",
    ["idle", "reflecting", "completed", "error"],
)
def test_reflection_state_valid_states(value):
    state = ReflectionState()

    state.set_state(value)

    assert state.get_state() == value


def test_reflection_state_invalid_state():
    state = ReflectionState()

    with pytest.raises(ValueError, match="Invalid reflection state: invalid"):
        state.set_state("invalid")


def test_reflection_state_reset():
    state = ReflectionState()

    state.set_state("completed")
    state.reset()

    assert state.get_state() == "idle"
    assert state.is_idle()


def test_reflection_state_predicates():
    state = ReflectionState()

    state.set_state("reflecting")
    assert state.is_reflecting()

    state.set_state("completed")
    assert state.is_completed()

    state.set_state("error")
    assert state.is_error()


def test_reflection_state_repr():
    state = ReflectionState()
    state.set_state("reflecting")

    assert "ReflectionState" in repr(state)
    assert "reflecting" in repr(state)
