"""
Tests for MetricRuntimeIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..runtime_integration import (
    MetricRuntimeIntegration,
)


# ==============================================================
# Helpers
# ==============================================================


class Runtime:

    def __init__(self):
        self.calls = 0
        self.closed = False

    def execute(self, metric, **kwargs):
        self.calls += 1
        return {
            **metric,
            "runtime": True,
        }

    def close(self):
        self.closed = True

    def reopen(self):
        self.closed = False


class Middleware:

    def __init__(self):
        self.calls = 0
        self.closed = False

    def execute(self, metric, **kwargs):
        self.calls += 1
        return {
            **metric,
            "middleware": True,
        }

    def close(self):
        self.closed = True

    def reopen(self):
        self.closed = False


class Pipeline:

    def __init__(self):
        self.calls = 0
        self.closed = False

    def execute(self, metric, **kwargs):
        self.calls += 1
        return {
            **metric,
            "pipeline": True,
        }

    def close(self):
        self.closed = True

    def reopen(self):
        self.closed = False


@pytest.fixture
def runtime():
    return Runtime()


@pytest.fixture
def middleware():
    return Middleware()


@pytest.fixture
def pipeline():
    return Pipeline()


@pytest.fixture
def integration(
    runtime,
    middleware,
    pipeline,
):
    return MetricRuntimeIntegration(
        runtime=runtime,
        middleware=middleware,
        pipeline=pipeline,
    )


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():
    integration = MetricRuntimeIntegration()

    assert integration.name == "MetricRuntimeIntegration"
    assert integration.description == ""
    assert integration.runtime is None
    assert integration.middleware is None
    assert integration.pipeline is None
    assert integration.enabled is True
    assert integration.closed is False
    assert integration.active is True


def test_constructor_components(
    integration,
    runtime,
    middleware,
    pipeline,
):
    assert integration.runtime is runtime
    assert integration.middleware is middleware
    assert integration.pipeline is pipeline
    assert integration.component_count() == 3


# ==============================================================
# Configuration
# ==============================================================


def test_set_runtime(runtime):
    integration = MetricRuntimeIntegration()

    assert integration.set_runtime(runtime) is integration
    assert integration.runtime is runtime


def test_set_middleware(middleware):
    integration = MetricRuntimeIntegration()

    assert integration.set_middleware(middleware) is integration
    assert integration.middleware is middleware


def test_set_pipeline(pipeline):
    integration = MetricRuntimeIntegration()

    assert integration.set_pipeline(pipeline) is integration
    assert integration.pipeline is pipeline


def test_components(integration):
    assert integration.components() == [
        integration.runtime,
        integration.middleware,
        integration.pipeline,
    ]


def test_len(integration):
    assert len(integration) == 3


def test_contains(integration):
    assert integration.runtime in integration
    assert integration.middleware in integration
    assert integration.pipeline in integration


# ==============================================================
# Execution
# ==============================================================


def test_execute(integration):
    result = integration.execute(
        {"value": 1}
    )

    assert result == {
        "value": 1,
        "runtime": True,
        "middleware": True,
        "pipeline": True,
    }

    assert integration.statistics()["executions"] == 1
    assert integration.statistics()["success"] == 1
    assert integration.statistics()["failures"] == 0


def test_execution_order(
    integration,
    runtime,
    middleware,
    pipeline,
):
    integration.execute({"value": 1})

    assert runtime.calls == 1
    assert middleware.calls == 1
    assert pipeline.calls == 1


def test_process_alias(integration):
    result = integration.process(
        {"value": 1}
    )

    assert result["pipeline"] is True


def test_run_alias(integration):
    result = integration.run(
        {"value": 1}
    )

    assert result["pipeline"] is True


def test_call(integration):
    result = integration(
        {"value": 1}
    )

    assert result["pipeline"] is True


def test_execute_many(integration):
    results = integration.execute_many(
        [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ]
    )

    assert len(results) == 3
    assert results[0]["value"] == 1
    assert results[1]["value"] == 2
    assert results[2]["value"] == 3
    assert integration.statistics()["executions"] == 3


def test_process_many(integration):
    results = integration.process_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


# ==============================================================
# Errors
# ==============================================================


def test_execution_failure():

    def failing(metric):
        raise RuntimeError("boom")

    integration = MetricRuntimeIntegration(
        runtime=failing
    )

    with pytest.raises(RuntimeError, match="boom"):
        integration.execute({})

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1

    assert isinstance(
        integration.last_error,
        RuntimeError,
    )

    assert integration.last_result is None


def test_disabled(integration):
    integration.disable()

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        integration.execute({})


def test_closed(integration):
    integration.close()

    with pytest.raises(
        RuntimeError,
        match="closed",
    ):
        integration.execute({})


# ==============================================================
# Lifecycle
# ==============================================================


def test_enable_disable(integration):
    assert integration.disable() is integration
    assert integration.enabled is False
    assert integration.active is False

    assert integration.enable() is integration
    assert integration.enabled is True
    assert integration.active is True


def test_close_propagates(
    integration,
    runtime,
    middleware,
    pipeline,
):
    integration.close()

    assert integration.closed is True
    assert runtime.closed is True
    assert middleware.closed is True
    assert pipeline.closed is True


def test_reopen_propagates(
    integration,
    runtime,
    middleware,
    pipeline,
):
    integration.close()
    integration.reopen()

    assert integration.closed is False
    assert runtime.closed is False
    assert middleware.closed is False
    assert pipeline.closed is False


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty():
    integration = MetricRuntimeIntegration()

    assert integration.validate() is True


def test_validate_components(integration):
    assert integration.validate() is True


def test_invalid_component():
    integration = MetricRuntimeIntegration(
        runtime=object()
    )

    assert integration.validate() is False


# ==============================================================
# Statistics
# ==============================================================


def test_statistics_initial(integration):
    stats = integration.statistics()

    assert stats["name"] == "MetricRuntimeIntegration"
    assert stats["components"] == 3
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


def test_status(integration):
    status = integration.status()

    assert status["enabled"] is True
    assert status["running"] is False
    assert status["closed"] is False
    assert status["active"] is True
    assert status["components"] == 3
    assert status["valid"] is True


def test_reset(integration):
    integration.execute({"value": 1})

    assert integration.statistics()["executions"] == 1

    assert integration.reset() is integration

    assert integration.statistics()["executions"] == 0
    assert integration.statistics()["success"] == 0
    assert integration.statistics()["failures"] == 0
    assert integration.last_result is None
    assert integration.last_error is None


# ==============================================================
# Representation
# ==============================================================


def test_repr(integration):
    value = repr(integration)

    assert "MetricRuntimeIntegration" in value
    assert "components=3" in value


def test_str(integration):
    assert str(integration) == "MetricRuntimeIntegration"