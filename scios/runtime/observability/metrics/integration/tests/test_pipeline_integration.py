"""
Tests for SciOS-NG Runtime Metrics Pipeline Integration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..pipeline_integration import (
    MetricPipelineIntegration,
)


# ==============================================================
# Helpers
# ==============================================================


class DummyPipeline:
    def __init__(
        self,
        name: str = "pipeline",
        prefix: str = "",
    ):
        self.name = name
        self.prefix = prefix
        self.calls = 0

    def execute(
        self,
        metric,
        **kwargs,
    ):
        self.calls += 1
        return f"{self.prefix}{metric}"


class ProcessPipeline:

    def __init__(self):
        self.calls = 0

    def process(
        self,
        metric,
        **kwargs,
    ):
        self.calls += 1
        return metric + 1


class RunPipeline:

    def __init__(self):
        self.calls = 0

    def run(
        self,
        metric,
        **kwargs,
    ):
        self.calls += 1
        return metric * 2


@pytest.fixture
def pipeline():
    return DummyPipeline()


@pytest.fixture
def integration():
    return MetricPipelineIntegration()


# ==============================================================
# Constructor
# ==============================================================


def test_constructor():
    integration = MetricPipelineIntegration()

    assert integration.name == "MetricPipelineIntegration"
    assert integration.description == ""
    assert integration.pipelines_count == 0
    assert len(integration) == 0


def test_constructor_with_pipelines():
    first = DummyPipeline()
    second = DummyPipeline()

    integration = MetricPipelineIntegration(
        pipelines=[
            first,
            second,
        ]
    )

    assert integration.pipelines_count == 2
    assert integration.get_pipeline(0) is first
    assert integration.get_pipeline(1) is second


# ==============================================================
# Properties
# ==============================================================


def test_properties():
    integration = MetricPipelineIntegration(
        name="custom",
        description="test integration",
    )

    assert integration.name == "custom"
    assert integration.description == "test integration"
    assert integration.last_result is None
    assert integration.last_error is None


# ==============================================================
# Pipeline Management
# ==============================================================


def test_add_pipeline(integration, pipeline):
    result = integration.add_pipeline(pipeline)

    assert result is integration
    assert integration.pipelines_count == 1
    assert pipeline in integration


def test_add_pipeline_rejects_none(integration):
    with pytest.raises(ValueError):
        integration.add_pipeline(None)


def test_add_pipeline_rejects_invalid_object(integration):
    with pytest.raises(TypeError):
        integration.add_pipeline(object())


def test_remove_pipeline(integration, pipeline):
    integration.add_pipeline(pipeline)

    assert integration.remove_pipeline(pipeline) is integration
    assert integration.pipelines_count == 0


def test_remove_missing_pipeline(integration, pipeline):
    assert integration.remove_pipeline(pipeline) is integration
    assert integration.pipelines_count == 0


def test_clear_pipelines(integration):
    first = DummyPipeline()
    second = DummyPipeline()

    integration.add_pipeline(first)
    integration.add_pipeline(second)

    assert integration.clear_pipelines() is integration
    assert integration.pipelines() == []
    assert len(integration) == 0


def test_pipelines_returns_copy(integration, pipeline):
    integration.add_pipeline(pipeline)

    pipelines = integration.pipelines()

    assert pipelines == [pipeline]

    pipelines.clear()

    assert integration.pipelines_count == 1


def test_get_pipeline(integration, pipeline):
    integration.add_pipeline(pipeline)

    assert integration.get_pipeline(0) is pipeline


def test_get_pipeline_invalid_index(integration):
    with pytest.raises(IndexError):
        integration.get_pipeline(0)


# ==============================================================
# Execution
# ==============================================================


def test_execute(integration):
    pipeline = DummyPipeline(
        prefix="processed:"
    )

    integration.add_pipeline(pipeline)

    result = integration.execute("metric")

    assert result == "processed:metric"
    assert pipeline.calls == 1


def test_execute_chains_pipelines():
    first = DummyPipeline(
        prefix="first:"
    )
    second = DummyPipeline(
        prefix="second:"
    )

    integration = MetricPipelineIntegration(
        pipelines=[
            first,
            second,
        ]
    )

    result = integration.execute("metric")

    assert result == "second:first:metric"
    assert first.calls == 1
    assert second.calls == 1


def test_execute_process_api():
    pipeline = ProcessPipeline()

    integration = MetricPipelineIntegration(
        pipelines=[pipeline]
    )

    assert integration.execute(10) == 11
    assert pipeline.calls == 1


def test_execute_run_api():
    pipeline = RunPipeline()

    integration = MetricPipelineIntegration(
        pipelines=[pipeline]
    )

    assert integration.execute(10) == 20
    assert pipeline.calls == 1


def test_execute_callable():
    integration = MetricPipelineIntegration(
        pipelines=[
            lambda metric: metric + 5,
        ]
    )

    assert integration.execute(10) == 15


def test_execute_empty_chain():
    integration = MetricPipelineIntegration()

    result = integration.execute(
        {"value": 42}
    )

    assert result == {"value": 42}


def test_execute_kwargs():
    class Pipeline:
        def execute(self, metric, **kwargs):
            return metric + kwargs["value"]

    integration = MetricPipelineIntegration(
        pipelines=[Pipeline()]
    )

    assert integration.execute(
        10,
        value=5,
    ) == 15


# ==============================================================
# Failure Handling
# ==============================================================


def test_execute_failure():
    error = RuntimeError("boom")

    def failing_pipeline(metric):
        raise error

    integration = MetricPipelineIntegration(
        pipelines=[failing_pipeline]
    )

    with pytest.raises(RuntimeError) as exc_info:
        integration.execute({})

    assert exc_info.value is error
    assert integration.last_error is error
    assert integration.last_result is None


def test_statistics_after_success(integration):
    integration.add_pipeline(
        lambda metric: metric + 1
    )

    assert integration.execute(1) == 2

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0
    assert stats["pipelines"] == 1


def test_statistics_after_failure(integration):
    def failing(metric):
        raise ValueError("failure")

    integration.add_pipeline(failing)

    with pytest.raises(ValueError):
        integration.execute(1)

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


# ==============================================================
# Aliases
# ==============================================================


def test_process_alias(integration):
    integration.add_pipeline(
        lambda metric: metric + 1
    )

    assert integration.process(10) == 11


def test_run_alias(integration):
    integration.add_pipeline(
        lambda metric: metric + 1
    )

    assert integration.run(10) == 11


def test_call_protocol(integration):
    integration.add_pipeline(
        lambda metric: metric + 1
    )

    assert integration(10) == 11


# ==============================================================
# Batch Execution
# ==============================================================


def test_execute_many(integration):
    integration.add_pipeline(
        lambda metric: metric * 2
    )

    result = integration.execute_many(
        [1, 2, 3]
    )

    assert result == [2, 4, 6]


def test_process_many(integration):
    integration.add_pipeline(
        lambda metric: metric + 10
    )

    result = integration.process_many(
        [1, 2, 3]
    )

    assert result == [11, 12, 13]


def test_execute_many_updates_statistics(integration):
    integration.add_pipeline(
        lambda metric: metric * 2
    )

    result = integration.execute_many(
        [1, 2, 3]
    )

    assert result == [2, 4, 6]

    stats = integration.statistics()

    assert stats["executions"] == 3
    assert stats["success"] == 3
    assert stats["failures"] == 0


# ==============================================================
# Validation
# ==============================================================


def test_validate_chain_empty(integration):
    assert integration.validate_chain() is True


def test_validate_chain_valid(integration):
    integration.add_pipeline(
        lambda metric: metric
    )

    assert integration.validate_chain() is True


def test_status_empty(integration):
    status = integration.status()

    assert status["pipelines"] == 0
    assert status["active"] is False
    assert status["valid"] is True


def test_status_active(integration):
    integration.add_pipeline(
        lambda metric: metric
    )

    status = integration.status()

    assert status["pipelines"] == 1
    assert status["active"] is True
    assert status["valid"] is True


# ==============================================================
# Reset
# ==============================================================


def test_reset(integration):
    integration.add_pipeline(
        lambda metric: metric + 1
    )

    integration.execute(1)

    assert integration.statistics()["executions"] == 1
    assert integration.last_result == 2

    assert integration.reset() is integration

    assert integration.statistics()["executions"] == 0
    assert integration.statistics()["success"] == 0
    assert integration.statistics()["failures"] == 0
    assert integration.last_result is None
    assert integration.last_error is None

    # Configuration must remain.
    assert integration.pipelines_count == 1


# ==============================================================
# Protocols
# ==============================================================


def test_len(integration, pipeline):
    integration.add_pipeline(pipeline)

    assert len(integration) == 1


def test_iter(integration):
    first = DummyPipeline()
    second = DummyPipeline()

    integration.add_pipeline(first)
    integration.add_pipeline(second)

    assert list(iter(integration)) == [
        first,
        second,
    ]


def test_contains(integration, pipeline):
    integration.add_pipeline(pipeline)

    assert pipeline in integration


# ==============================================================
# Representation
# ==============================================================


def test_repr(integration):
    text = repr(integration)

    assert "MetricPipelineIntegration" in text
    assert "pipelines=0" in text
    assert "executions=0" in text


def test_str(integration):
    assert str(integration) == "MetricPipelineIntegration"