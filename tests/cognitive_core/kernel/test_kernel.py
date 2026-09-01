"""
Contract tests for scios.cognitive_core.kernel.kernel.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.kernel import CognitiveKernel
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.response import CognitiveResponse
from scios.cognitive_core.kernel.state import KernelStatus


def test_kernel_can_be_created() -> None:
    kernel = CognitiveKernel()

    assert isinstance(kernel, CognitiveKernel)
    assert kernel.config is None
    assert kernel._booted is False


def test_kernel_version() -> None:
    kernel = CognitiveKernel()

    assert kernel.VERSION == "0.1.0"


def test_kernel_initial_status() -> None:
    kernel = CognitiveKernel()

    status = kernel.status()

    assert isinstance(status, dict)
    assert status["booted"] is False
    assert status["version"] == kernel.VERSION
    assert status["state"] == kernel.state.status.name


def test_kernel_initial_state_is_idle() -> None:
    kernel = CognitiveKernel()

    assert kernel.state.status == KernelStatus.IDLE


def test_kernel_has_core_components() -> None:
    kernel = CognitiveKernel()

    assert kernel.registry is not None
    assert kernel.dispatcher is not None
    assert kernel.middleware is not None
    assert kernel.event_bus is not None
    assert kernel.pipeline is not None
    assert kernel.state is not None


def test_kernel_pipeline_uses_kernel_event_bus() -> None:
    kernel = CognitiveKernel()

    assert kernel.pipeline.event_bus is kernel.event_bus


def test_boot_returns_true() -> None:
    kernel = CognitiveKernel()

    result = kernel.boot()

    assert result is True


def test_boot_sets_booted_flag() -> None:
    kernel = CognitiveKernel()

    kernel.boot()

    assert kernel._booted is True


def test_boot_sets_running_status() -> None:
    kernel = CognitiveKernel()

    kernel.boot()

    assert kernel.state.status == KernelStatus.RUNNING


def test_boot_status() -> None:
    kernel = CognitiveKernel()

    kernel.boot()

    status = kernel.status()

    assert status["booted"] is True
    assert status["state"] == KernelStatus.RUNNING.name


def test_boot_is_idempotent() -> None:
    kernel = CognitiveKernel()

    assert kernel.boot() is True
    assert kernel.boot() is True

    assert kernel._booted is True
    assert kernel.state.status == KernelStatus.RUNNING


def test_shutdown_returns_true() -> None:
    kernel = CognitiveKernel()

    result = kernel.shutdown()

    assert result is True


def test_shutdown_clears_booted_flag() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.shutdown()

    assert kernel._booted is False


def test_shutdown_sets_stopped_status() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.shutdown()

    assert kernel.state.status == KernelStatus.STOPPED


def test_shutdown_status() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.shutdown()

    status = kernel.status()

    assert status["booted"] is False
    assert status["state"] == KernelStatus.STOPPED.name


def test_shutdown_is_safe_before_boot() -> None:
    kernel = CognitiveKernel()

    assert kernel.shutdown() is True
    assert kernel._booted is False
    assert kernel.state.status == KernelStatus.STOPPED


def test_reset_returns_none() -> None:
    kernel = CognitiveKernel()

    result = kernel.reset()

    assert result is None


def test_reset_sets_idle_status() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.reset()

    assert kernel.state.status == KernelStatus.IDLE


def test_reset_keeps_kernel_booted() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.reset()

    assert kernel._booted is True


def test_run_requires_boot() -> None:
    kernel = CognitiveKernel()

    cognitive_request = CognitiveRequest(
        query="hello",
    )

    with pytest.raises(Exception, match="Kernel not booted"):
        kernel.run(cognitive_request)


def test_run_rejects_invalid_request() -> None:
    kernel = CognitiveKernel()
    kernel.boot()

    with pytest.raises(TypeError, match="CognitiveRequest"):
        kernel.run("hello")  # type: ignore[arg-type]


def test_run_returns_cognitive_response() -> None:
    kernel = CognitiveKernel()
    kernel.boot()

    cognitive_request = CognitiveRequest(
        query="hello",
    )

    result = kernel.run(cognitive_request)

    assert isinstance(result, CognitiveResponse)


def test_run_creates_context() -> None:
    kernel = CognitiveKernel()
    kernel.boot()

    cognitive_request = CognitiveRequest(
        query="hello",
    )

    context = CognitiveContext(cognitive_request)

    assert isinstance(context, CognitiveContext)


def test_kernel_repr_before_boot() -> None:
    kernel = CognitiveKernel()

    result = repr(kernel)

    assert "CognitiveKernel" in result
    assert "booted=False" in result
    assert "IDLE" in result


def test_kernel_repr_after_boot() -> None:
    kernel = CognitiveKernel()

    kernel.boot()

    result = repr(kernel)

    assert "CognitiveKernel" in result
    assert "booted=True" in result
    assert "RUNNING" in result


def test_kernel_repr_after_shutdown() -> None:
    kernel = CognitiveKernel()

    kernel.boot()
    kernel.shutdown()

    result = repr(kernel)

    assert "CognitiveKernel" in result
    assert "booted=False" in result
    assert "STOPPED" in result


def test_custom_config_is_preserved() -> None:
    config = {
        "environment": "test",
        "debug": True,
    }

    kernel = CognitiveKernel(config=config)

    assert kernel.config is config


def test_kernel_components_are_unique_per_instance() -> None:
    first = CognitiveKernel()
    second = CognitiveKernel()

    assert first.registry is not second.registry
    assert first.dispatcher is not second.dispatcher
    assert first.middleware is not second.middleware
    assert first.event_bus is not second.event_bus
    assert first.pipeline is not second.pipeline
    assert first.state is not second.state


def test_kernel_status_is_snapshot() -> None:
    kernel = CognitiveKernel()

    first = kernel.status()

    kernel.boot()

    second = kernel.status()

    assert first["booted"] is False
    assert second["booted"] is True
    assert first is not second


def test_kernel_lifecycle_boot_shutdown_boot() -> None:
    kernel = CognitiveKernel()

    kernel.boot()

    assert kernel.state.status == KernelStatus.RUNNING
    assert kernel._booted is True

    kernel.shutdown()

    assert kernel.state.status == KernelStatus.STOPPED
    assert kernel._booted is False

    kernel.boot()

    assert kernel.state.status == KernelStatus.RUNNING
    assert kernel._booted is True