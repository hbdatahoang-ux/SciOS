"""
Tests for scios.cognitive_core.kernel.state.
"""

from scios.cognitive_core.kernel.state import (
    KernelState,
    KernelStatus,
    PipelineState,
    pipeline_state_from_value,
)


# ==========================================================
# PipelineState
# ==========================================================


def test_pipeline_state_values():
    assert PipelineState.CREATED.value == "created"
    assert PipelineState.INITIALIZED.value == "initialized"
    assert PipelineState.RUNNING.value == "running"
    assert PipelineState.PAUSED.value == "paused"
    assert PipelineState.COMPLETED.value == "completed"
    assert PipelineState.FAILED.value == "failed"
    assert PipelineState.CANCELLED.value == "cancelled"
    assert PipelineState.STOPPED.value == "stopped"
    assert PipelineState.CLOSED.value == "closed"
    assert PipelineState.RESET.value == "reset"


def test_pipeline_state_from_value_accepts_enum():
    assert (
        pipeline_state_from_value(PipelineState.RUNNING)
        is PipelineState.RUNNING
    )


def test_pipeline_state_from_value_accepts_string():
    assert (
        pipeline_state_from_value("running")
        is PipelineState.RUNNING
    )


def test_pipeline_state_from_value_rejects_invalid_value():
    try:
        pipeline_state_from_value("invalid")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid pipeline state must raise ValueError"
        )


def test_pipeline_state_terminal_states():
    terminal_states = {
        PipelineState.COMPLETED,
        PipelineState.FAILED,
        PipelineState.CANCELLED,
        PipelineState.STOPPED,
        PipelineState.CLOSED,
    }

    for state in PipelineState:
        assert state.terminal is (state in terminal_states)


def test_pipeline_state_running_states():
    assert PipelineState.INITIALIZED.running is True
    assert PipelineState.RUNNING.running is True

    assert PipelineState.CREATED.running is False
    assert PipelineState.PAUSED.running is False
    assert PipelineState.COMPLETED.running is False
    assert PipelineState.FAILED.running is False
    assert PipelineState.CANCELLED.running is False
    assert PipelineState.STOPPED.running is False
    assert PipelineState.CLOSED.running is False
    assert PipelineState.RESET.running is False


def test_pipeline_state_to_dict():
    state = PipelineState.RUNNING

    assert state.to_dict() == {
        "state": "running",
    }


def test_pipeline_state_is_string_enum():
    state = PipelineState.RUNNING

    assert isinstance(state, str)
    assert state == "running"


# ==========================================================
# KernelStatus
# ==========================================================


def test_kernel_status_values():
    assert KernelStatus.IDLE.value == "idle"
    assert KernelStatus.INITIALIZING.value == "initializing"
    assert KernelStatus.RUNNING.value == "running"
    assert KernelStatus.PAUSED.value == "paused"
    assert KernelStatus.ERROR.value == "error"
    assert KernelStatus.STOPPED.value == "stopped"
    assert KernelStatus.CLOSED.value == "closed"


def test_kernel_status_terminal():
    assert KernelStatus.STOPPED.terminal is True
    assert KernelStatus.CLOSED.terminal is True

    assert KernelStatus.IDLE.terminal is False
    assert KernelStatus.INITIALIZING.terminal is False
    assert KernelStatus.RUNNING.terminal is False
    assert KernelStatus.PAUSED.terminal is False
    assert KernelStatus.ERROR.terminal is False


def test_kernel_status_is_string_enum():
    assert isinstance(KernelStatus.RUNNING, str)
    assert KernelStatus.RUNNING == "running"


# ==========================================================
# KernelState construction
# ==========================================================


def test_kernel_state_defaults_to_idle():
    state = KernelState()

    assert state.status is KernelStatus.IDLE
    assert state.message is None


def test_kernel_state_accepts_status():
    state = KernelState(
        status=KernelStatus.RUNNING,
    )

    assert state.status is KernelStatus.RUNNING
    assert state.message is None


def test_kernel_state_accepts_message():
    state = KernelState(
        message="Kernel booted",
    )

    assert state.status is KernelStatus.IDLE
    assert state.message == "Kernel booted"


def test_kernel_state_accepts_status_and_message():
    state = KernelState(
        status=KernelStatus.ERROR,
        message="Something failed",
    )

    assert state.status is KernelStatus.ERROR
    assert state.message == "Something failed"


# ==========================================================
# KernelState mutation
# ==========================================================


def test_set_status_updates_status():
    state = KernelState()

    result = state.set_status(
        KernelStatus.RUNNING,
    )

    assert result is state
    assert state.status is KernelStatus.RUNNING


def test_set_status_updates_message():
    state = KernelState()

    state.set_status(
        KernelStatus.ERROR,
        "Execution failed",
    )

    assert state.status is KernelStatus.ERROR
    assert state.message == "Execution failed"


def test_set_status_clears_previous_message_by_default():
    state = KernelState(
        status=KernelStatus.ERROR,
        message="old error",
    )

    state.set_status(
        KernelStatus.RUNNING,
    )

    assert state.status is KernelStatus.RUNNING
    assert state.message is None


# ==========================================================
# KernelState checks
# ==========================================================


def test_is_idle():
    state = KernelState(KernelStatus.IDLE)

    assert state.is_idle() is True
    assert state.is_running() is False
    assert state.is_paused() is False
    assert state.is_error() is False
    assert state.is_stopped() is False
    assert state.is_closed() is False


def test_is_running():
    state = KernelState(KernelStatus.RUNNING)

    assert state.is_idle() is False
    assert state.is_running() is True
    assert state.is_paused() is False
    assert state.is_error() is False
    assert state.is_stopped() is False
    assert state.is_closed() is False


def test_is_paused():
    state = KernelState(KernelStatus.PAUSED)

    assert state.is_paused() is True
    assert state.is_running() is False


def test_is_error():
    state = KernelState(KernelStatus.ERROR)

    assert state.is_error() is True
    assert state.is_running() is False


def test_is_stopped():
    state = KernelState(KernelStatus.STOPPED)

    assert state.is_stopped() is True
    assert state.is_closed() is False


def test_is_closed():
    state = KernelState(KernelStatus.CLOSED)

    assert state.is_closed() is True
    assert state.is_stopped() is False


# ==========================================================
# Serialization
# ==========================================================


def test_kernel_state_to_dict():
    state = KernelState(
        status=KernelStatus.RUNNING,
        message="Kernel executing",
    )

    result = state.to_dict()

    assert result == {
        "status": "running",
        "message": "Kernel executing",
    }


def test_kernel_state_to_dict_without_message():
    state = KernelState(
        status=KernelStatus.IDLE,
    )

    assert state.to_dict() == {
        "status": "idle",
        "message": None,
    }


def test_kernel_state_from_dict():
    state = KernelState.from_dict(
        {
            "status": "running",
            "message": "active",
        }
    )

    assert state.status is KernelStatus.RUNNING
    assert state.message == "active"


def test_kernel_state_from_dict_defaults_status():
    state = KernelState.from_dict({})

    assert state.status is KernelStatus.IDLE
    assert state.message is None


def test_kernel_state_from_dict_preserves_none_message():
    state = KernelState.from_dict(
        {
            "status": "idle",
            "message": None,
        }
    )

    assert state.status is KernelStatus.IDLE
    assert state.message is None


def test_kernel_state_from_dict_rejects_invalid_status():
    try:
        KernelState.from_dict(
            {
                "status": "invalid",
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid kernel status must raise ValueError"
        )


# ==========================================================
# Snapshot / Restore
# ==========================================================


def test_snapshot_matches_to_dict():
    state = KernelState(
        status=KernelStatus.RUNNING,
        message="running",
    )

    assert state.snapshot() == state.to_dict()


def test_restore_updates_state():
    state = KernelState(
        status=KernelStatus.IDLE,
    )

    result = state.restore(
        {
            "status": "running",
            "message": "restored",
        }
    )

    assert result is state
    assert state.status is KernelStatus.RUNNING
    assert state.message == "restored"


def test_restore_replaces_previous_state():
    state = KernelState(
        status=KernelStatus.ERROR,
        message="old error",
    )

    state.restore(
        {
            "status": "paused",
            "message": "paused execution",
        }
    )

    assert state.status is KernelStatus.PAUSED
    assert state.message == "paused execution"


def test_restore_can_restore_idle_state():
    state = KernelState(
        status=KernelStatus.ERROR,
        message="failure",
    )

    state.restore(
        {
            "status": "idle",
            "message": None,
        }
    )

    assert state.status is KernelStatus.IDLE
    assert state.message is None


# ==========================================================
# Round-trip
# ==========================================================


def test_kernel_state_round_trip():
    original = KernelState(
        status=KernelStatus.RUNNING,
        message="round trip",
    )

    restored = KernelState.from_dict(
        original.to_dict()
    )

    assert restored.status is original.status
    assert restored.message == original.message
    assert restored.to_dict() == original.to_dict()


def test_kernel_state_snapshot_restore_round_trip():
    original = KernelState(
        status=KernelStatus.ERROR,
        message="test error",
    )

    snapshot = original.snapshot()

    restored = KernelState()

    result = restored.restore(snapshot)

    assert result is restored
    assert restored.snapshot() == snapshot


# ==========================================================
# Representation
# ==========================================================


def test_kernel_state_repr_contains_status():
    state = KernelState(
        status=KernelStatus.RUNNING,
    )

    result = repr(state)

    assert "running" in result


def test_kernel_state_repr_contains_message():
    state = KernelState(
        status=KernelStatus.ERROR,
        message="failure",
    )

    result = repr(state)

    assert "failure" in result


def test_kernel_state_repr_format():
    state = KernelState(
        status=KernelStatus.IDLE,
        message=None,
    )

    assert repr(state) == (
        "<KernelState status='idle' message=None>"
    )
