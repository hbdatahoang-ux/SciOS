"""
Tests for MetricTracingIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..tracing import MetricTracingIntegration


# ==============================================================
# Helpers
# ==============================================================


class Span:

    def __init__(self):
        self.attributes = {}
        self.events = []

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def add_event(self, name, attributes=None):
        self.events.append(
            (
                name,
                attributes,
            )
        )


class SpanContext(Span):

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False


class Tracer:

    def __init__(self):
        self.span = SpanContext()
        self.started = []

    def start_as_current_span(
        self,
        name,
        **kwargs,
    ):
        self.started.append(name)
        return self.span

    def current_span(self):
        return self.span


class StartSpanTracer:

    def __init__(self):
        self.span = SpanContext()

    def start_span(
        self,
        name,
        **kwargs,
    ):
        return self.span


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    integration = MetricTracingIntegration()

    assert integration.name == "MetricTracingIntegration"
    assert integration.description == ""
    assert integration.tracer is None
    assert integration.configured is False
    assert integration.last_result is None
    assert integration.last_error is None


def test_constructor_tracer():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    assert integration.tracer is tracer
    assert integration.configured is True


# ==============================================================
# Tracer Management
# ==============================================================


def test_set_tracer():

    integration = MetricTracingIntegration()
    tracer = Tracer()

    assert integration.set_tracer(tracer) is integration
    assert integration.tracer is tracer
    assert integration.configured is True


def test_clear_tracer():

    integration = MetricTracingIntegration(
        tracer=Tracer(),
    )

    assert integration.clear_tracer() is integration
    assert integration.tracer is None
    assert integration.configured is False


# ==============================================================
# Context
# ==============================================================


def test_current_span_without_tracer():

    integration = MetricTracingIntegration()

    assert integration.current_span() is None


def test_current_span():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    assert integration.current_span() is tracer.span


def test_current_trace_without_api():

    integration = MetricTracingIntegration(
        tracer=Tracer(),
    )

    assert integration.current_trace() is None


# ==============================================================
# Span
# ==============================================================


def test_start_span_without_tracer():

    integration = MetricTracingIntegration()

    assert integration.start_span("metric") is None


def test_start_span():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    span = integration.start_span(
        "metric",
    )

    assert span is tracer.span


def test_start_span_fallback():

    tracer = StartSpanTracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    span = integration.start_span(
        "metric",
    )

    assert span is tracer.span


# ==============================================================
# Attributes
# ==============================================================


def test_set_attribute_without_span():

    integration = MetricTracingIntegration()

    assert integration.set_attribute(
        "key",
        "value",
    ) is integration


def test_set_attribute():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    assert integration.set_attribute(
        "key",
        "value",
    ) is integration

    assert tracer.span.attributes["key"] == "value"


def test_add_event():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    assert integration.add_event(
        "metric.updated",
        {"value": 42},
    ) is integration

    assert tracer.span.events == [
        (
            "metric.updated",
            {"value": 42},
        )
    ]


# ==============================================================
# Execution
# ==============================================================


def test_execute_without_tracer():

    integration = MetricTracingIntegration()

    metric = {
        "value": 42,
    }

    result = integration.execute(
        metric,
    )

    assert result == metric
    assert integration.last_result == metric

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_execute_with_handler():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    result = integration.execute(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "processed": True,
        },
        span_name="metric.process",
    )

    assert result == {
        "value": 1,
        "processed": True,
    }

    assert tracer.started == [
        "metric.process",
    ]

    assert tracer.span.attributes[
        "metrics.type"
    ] == "mapping"

    assert tracer.span.attributes[
        "metrics.result_type"
    ] == "dict"


def test_trace_alias():

    integration = MetricTracingIntegration()

    result = integration.trace(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "trace": True,
        },
    )

    assert result["trace"] is True


def test_run_alias():

    integration = MetricTracingIntegration()

    result = integration.run(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "run": True,
        },
    )

    assert result["run"] is True


def test_call():

    integration = MetricTracingIntegration()

    result = integration(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


# ==============================================================
# Error Handling
# ==============================================================


def test_execute_failure():

    error = RuntimeError("boom")

    def failing(metric):
        raise error

    integration = MetricTracingIntegration()

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        integration.execute(
            {},
            handler=failing,
        )

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1

    assert integration.last_error is error
    assert integration.last_result is None


# ==============================================================
# Diagnostics
# ==============================================================


def test_statistics():

    integration = MetricTracingIntegration()

    stats = integration.statistics()

    assert stats["name"] == "MetricTracingIntegration"
    assert stats["configured"] is False
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


def test_status_without_tracer():

    integration = MetricTracingIntegration()

    status = integration.status()

    assert status["configured"] is False
    assert status["active"] is False


def test_status_with_tracer():

    tracer = Tracer()

    integration = MetricTracingIntegration(
        tracer=tracer,
    )

    status = integration.status()

    assert status["configured"] is True
    assert status["active"] is True


def test_reset():

    integration = MetricTracingIntegration()

    integration.execute(
        {"value": 1},
    )

    assert integration.statistics()["executions"] == 1

    assert integration.reset() is integration

    assert integration.statistics()["executions"] == 0
    assert integration.statistics()["success"] == 0
    assert integration.statistics()["failures"] == 0

    assert integration.last_result is None
    assert integration.last_error is None


# ==============================================================
# Protocols
# ==============================================================


def test_repr():

    integration = MetricTracingIntegration()

    value = repr(integration)

    assert "MetricTracingIntegration" in value
    assert "configured=False" in value


def test_str():

    integration = MetricTracingIntegration()

    assert str(integration) == "MetricTracingIntegration"