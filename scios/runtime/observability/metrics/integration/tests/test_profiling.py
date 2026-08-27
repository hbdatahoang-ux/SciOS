"""
Tests for MetricProfilingIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..profiling import MetricProfilingIntegration


# ==============================================================
# Helpers
# ==============================================================


class ProfilerContext:

    def __init__(self, profiler, name):
        self.profiler = profiler
        self.name = name

    def __enter__(self):
        self.profiler.entered.append(self.name)
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.profiler.exited.append(self.name)
        return False


class Profiler:

    def __init__(self):
        self.entered = []
        self.exited = []
        self.started = []
        self.stopped = []
        self.records = []

    def profile(self, name, **kwargs):
        return ProfilerContext(
            self,
            name,
        )

    def start(self, name, **kwargs):
        self.started.append(name)
        return name

    def stop(self, **kwargs):
        self.stopped.append(True)
        return True

    def record(self, key, value):
        self.records.append(
            (
                key,
                value,
            )
        )


class ContextProfiler:

    def __init__(self):
        self.names = []

    def context(self, name, **kwargs):
        self.names.append(name)
        return ProfilerContext(
            _ContextRecorder(self),
            name,
        )


class _ContextRecorder:

    def __init__(self, owner):
        self.owner = owner
        self.entered = []
        self.exited = []

    def __enter__(self):
        self.entered.append(True)
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.exited.append(True)
        return False


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    integration = MetricProfilingIntegration()

    assert integration.name == "MetricProfilingIntegration"
    assert integration.description == ""
    assert integration.profiler is None
    assert integration.configured is False
    assert integration.last_result is None
    assert integration.last_error is None


def test_constructor_profiler():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    assert integration.profiler is profiler
    assert integration.configured is True


# ==============================================================
# Profiler Management
# ==============================================================


def test_set_profiler():

    integration = MetricProfilingIntegration()
    profiler = Profiler()

    assert integration.set_profiler(
        profiler
    ) is integration

    assert integration.profiler is profiler
    assert integration.configured is True


def test_clear_profiler():

    integration = MetricProfilingIntegration(
        profiler=Profiler(),
    )

    assert integration.clear_profiler() is integration

    assert integration.profiler is None
    assert integration.configured is False


# ==============================================================
# Lifecycle
# ==============================================================


def test_start_without_profiler():

    integration = MetricProfilingIntegration()

    assert integration.start() is None


def test_start():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    result = integration.start(
        "metric",
    )

    assert result == "metric"
    assert profiler.started == [
        "metric",
    ]


def test_stop_without_profiler():

    integration = MetricProfilingIntegration()

    assert integration.stop() is None


def test_stop():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    assert integration.stop() is True
    assert profiler.stopped == [True]


# ==============================================================
# Context
# ==============================================================


def test_profile_without_profiler():

    integration = MetricProfilingIntegration()

    with integration.profile("metric"):
        pass


def test_profile():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    with integration.profile(
        "metric",
    ):
        pass

    assert profiler.entered == [
        "metric",
    ]

    assert profiler.exited == [
        "metric",
    ]


# ==============================================================
# Execution
# ==============================================================


def test_execute_without_profiler():

    integration = MetricProfilingIntegration()

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


def test_execute_with_profiler():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    result = integration.execute(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "processed": True,
        },
        profile_name="metric.process",
    )

    assert result == {
        "value": 1,
        "processed": True,
    }

    assert profiler.entered == [
        "metric.process",
    ]

    assert profiler.exited == [
        "metric.process",
    ]


def test_profile_metric_alias():

    integration = MetricProfilingIntegration()

    result = integration.profile_metric(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "profiled": True,
        },
    )

    assert result["profiled"] is True


def test_run_alias():

    integration = MetricProfilingIntegration()

    result = integration.run(
        {"value": 1},
        handler=lambda metric: {
            **metric,
            "run": True,
        },
    )

    assert result["run"] is True


def test_call():

    integration = MetricProfilingIntegration()

    result = integration(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


# ==============================================================
# Record
# ==============================================================


def test_record_without_profiler():

    integration = MetricProfilingIntegration()

    assert integration.record(
        "key",
        42,
    ) is integration


def test_record():

    profiler = Profiler()

    integration = MetricProfilingIntegration(
        profiler=profiler,
    )

    assert integration.record(
        "metric.value",
        42,
    ) is integration

    assert profiler.records == [
        (
            "metric.value",
            42,
        )
    ]


# ==============================================================
# Error Handling
# ==============================================================


def test_execute_failure():

    error = RuntimeError("boom")

    def failing(metric):
        raise error

    integration = MetricProfilingIntegration()

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

    integration = MetricProfilingIntegration()

    stats = integration.statistics()

    assert stats["name"] == "MetricProfilingIntegration"
    assert stats["configured"] is False
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


def test_status_without_profiler():

    integration = MetricProfilingIntegration()

    status = integration.status()

    assert status["configured"] is False
    assert status["active"] is False


def test_status_with_profiler():

    integration = MetricProfilingIntegration(
        profiler=Profiler(),
    )

    status = integration.status()

    assert status["configured"] is True
    assert status["active"] is True


def test_reset():

    integration = MetricProfilingIntegration()

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

    integration = MetricProfilingIntegration()

    value = repr(integration)

    assert "MetricProfilingIntegration" in value
    assert "configured=False" in value


def test_str():

    integration = MetricProfilingIntegration()

    assert str(integration) == "MetricProfilingIntegration"