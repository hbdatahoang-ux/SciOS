# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.metric_state import (
    __version__,
    MetricHealth,
    MetricLifecycle,
    MetricState,
    MetricStatus,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_state():
    state = MetricState()

    assert isinstance(state, MetricState)


def test_custom_state():
    state = MetricState(
        enabled=False,
        active=False,
        lifecycle=MetricLifecycle.ACTIVE,
        health=MetricHealth.WARNING,
        status=MetricStatus.RUNNING,
    )

    assert state.enabled is False
    assert state.active is False
    assert state.lifecycle is MetricLifecycle.ACTIVE
    assert state.health is MetricHealth.WARNING
    assert state.status is MetricStatus.RUNNING


# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_default_enabled():
    assert MetricState().enabled is True


def test_default_active():
    assert MetricState().active is True


def test_default_health():
    assert MetricState().health is MetricHealth.HEALTHY


def test_default_status():
    assert MetricState().status is MetricStatus.IDLE


# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_health():
    with pytest.raises(TypeError):
        MetricState(
            health="bad",
        )


def test_invalid_status():
    with pytest.raises(TypeError):
        MetricState(
            status="bad",
        )


def test_invalid_lifecycle():
    with pytest.raises(TypeError):
        MetricState(
            lifecycle="bad",
        )


# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_enabled():
    state = MetricState()

    assert state.enabled is True
    assert state.is_enabled() is True


def test_active():
    state = MetricState()

    assert state.active is True
    assert state.is_active() is True


def test_health():
    state = MetricState()

    assert state.health is MetricHealth.HEALTHY
    assert state.healthy is True
    assert state.is_healthy() is True


def test_status():
    state = MetricState()

    assert state.status is MetricStatus.IDLE

# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_enable():
    state = MetricState(enabled=False)

    state.enable()

    assert state.enabled is True


def test_disable():
    state = MetricState()

    state.disable()

    assert state.enabled is False
    assert state.active is False
    assert state.lifecycle is MetricLifecycle.DISABLED


def test_activate():
    state = MetricState(
        enabled=True,
        active=False,
    )

    state.activate()

    assert state.active is True
    assert state.lifecycle is MetricLifecycle.ACTIVE


def test_deactivate():
    state = MetricState()

    state.deactivate()

    assert state.active is False


def test_reset():
    state = MetricState(
        enabled=False,
        active=False,
        lifecycle=MetricLifecycle.ARCHIVED,
        health=MetricHealth.ERROR,
        status=MetricStatus.RUNNING,
    )

    state.reset()

    assert state.enabled is True
    assert state.active is True
    assert state.lifecycle is MetricLifecycle.CREATED
    assert state.health is MetricHealth.HEALTHY
    assert state.status is MetricStatus.IDLE


def test_archive():
    state = MetricState()

    state.archive()

    assert state.lifecycle is MetricLifecycle.ARCHIVED
    assert state.active is False


def test_restore():
    state = MetricState()

    state.archive()
    state.restore()

    assert state.enabled is True
    assert state.active is True
    assert state.lifecycle is MetricLifecycle.ACTIVE


# ==============================================================================
# Part 7. Health
# ==============================================================================


def test_mark_healthy():
    state = MetricState(
        health=MetricHealth.ERROR,
    )

    state.mark_healthy()

    assert state.health is MetricHealth.HEALTHY


def test_mark_warning():
    state = MetricState()

    state.mark_warning()

    assert state.health is MetricHealth.WARNING


def test_mark_error():
    state = MetricState()

    state.mark_error()

    assert state.health is MetricHealth.ERROR


def test_mark_stale():
    state = MetricState()

    state.mark_stale()

    assert state.health is MetricHealth.STALE


# ==============================================================================
# Part 8. Queries
# ==============================================================================


def test_is_enabled():
    assert MetricState().is_enabled() is True


def test_is_active():
    assert MetricState().is_active() is True


def test_is_healthy():
    assert MetricState().is_healthy() is True


def test_is_warning():
    state = MetricState()

    state.mark_warning()

    assert state.is_warning() is True


def test_is_error():
    state = MetricState()

    state.mark_error()

    assert state.is_error() is True


def test_is_stale():
    state = MetricState()

    state.mark_stale()

    assert state.is_stale() is True


# ==============================================================================
# Part 9. Serialization
# ==============================================================================


def test_to_dict():
    state = MetricState()

    data = state.to_dict()

    assert data["enabled"] is True
    assert data["health"] == MetricHealth.HEALTHY.value


def test_from_dict():
    state = MetricState.from_dict(
        {
            "enabled": False,
            "active": False,
            "lifecycle": MetricLifecycle.ACTIVE.value,
            "health": MetricHealth.WARNING.value,
            "status": MetricStatus.RUNNING.value,
        }
    )

    assert state.health is MetricHealth.WARNING
    assert state.status is MetricStatus.RUNNING


def test_to_json():
    assert isinstance(
        MetricState().to_json(),
        str,
    )


def test_from_json():
    state = MetricState.from_json(
        MetricState().to_json()
    )

    assert isinstance(state, MetricState)


# ==============================================================================
# Part 10. Copy
# ==============================================================================


def test_copy():
    state = MetricState()

    copied = state.copy()

    assert copied == state
    assert copied is not state


def test_clone():
    state = MetricState()

    cloned = state.clone()

    assert cloned == state
    assert cloned is not state


# ==============================================================================
# Part 11. Equality
# ==============================================================================


def test_eq():
    assert MetricState() == MetricState()


def test_hash():
    assert isinstance(
        hash(MetricState()),
        int,
    )


# ==============================================================================
# Part 12. Representation
# ==============================================================================


def test_repr():
    assert "MetricState" in repr(MetricState())


def test_str():
    assert isinstance(str(MetricState()), str)


# ==============================================================================
# Part 13. Public API
# ==============================================================================


def test_all():
    from scios.runtime.observability.metrics.core.metric_state import __all__

    assert "MetricState" in __all__


def test_version():
    assert isinstance(__version__, str)


# ==============================================================================
# Part 14. Regression
# ==============================================================================


def test_json_roundtrip():
    state = MetricState()

    assert MetricState.from_json(
        state.to_json()
    ) == state


def test_dict_roundtrip():
    state = MetricState()

    assert MetricState.from_dict(
        state.to_dict()
    ) == state


def test_clone_independence():
    state = MetricState()

    cloned = state.clone()

    cloned.disable()

    assert cloned != state
    assert state.enabled is True


def test_reset_restores_defaults():
    state = MetricState()

    state.disable()
    state.mark_error()
    state.reset()

    assert state == MetricState()    