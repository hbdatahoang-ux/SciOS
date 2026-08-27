"""
Tests for MetricRuntimeIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..runtime import MetricRuntimeIntegration


# ==============================================================
# Helpers
# ==============================================================


class Processor:

    def __init__(self):
        self.calls = 0

    def process(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            "processor": True,
        }


class Middleware:

    def __init__(self):
        self.calls = 0

    def execute(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            "middleware": True,
        }


class Pipeline:

    def __init__(self):
        self.calls = 0

    def execute(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            "pipeline": True,
        }


class Exporter:

    def __init__(self):
        self.calls = 0

    def export(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            "exporter": True,
        }


class RunComponent:

    def run(self, metric, **kwargs):
        return {
            **metric,
            "run": True,
        }


class ExecuteComponent:

    def execute(self, metric, **kwargs):
        return {
            **metric,
            "execute": True,
        }


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def processor():
    return Processor()


@pytest.fixture
def middleware():
    return Middleware()


@pytest.fixture
def pipeline():
    return Pipeline()


@pytest.fixture
def exporter():
    return Exporter()


@pytest.fixture
def runtime(
    processor,
    middleware,
    pipeline,
    exporter,
):
    return MetricRuntimeIntegration(
        processor=processor,
        middleware=middleware,
        pipeline=pipeline,
        exporter=exporter,
    )


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    runtime = MetricRuntimeIntegration()

    assert runtime.name == "MetricRuntimeIntegration"
    assert runtime.description == ""

    assert runtime.processor is None
    assert runtime.middleware is None
    assert runtime.pipeline is None
    assert runtime.exporter is None

    assert runtime.enabled is True
    assert runtime.running is False
    assert runtime.closed is False
    assert runtime.active is True

    assert runtime.last_result is None
    assert runtime.last_error is None


def test_constructor_components(
    runtime,
    processor,
    middleware,
    pipeline,
    exporter,
):

    assert runtime.processor is processor
    assert runtime.middleware is middleware
    assert runtime.pipeline is pipeline
    assert runtime.exporter is exporter

    assert len(runtime) == 4


# ==============================================================
# Component Management
# ==============================================================


def test_set_processor():

    runtime = MetricRuntimeIntegration()
    processor = Processor()

    assert runtime.set_processor(processor) is runtime
    assert runtime.processor is processor


def test_set_middleware():

    runtime = MetricRuntimeIntegration()
    middleware = Middleware()

    assert runtime.set_middleware(middleware) is runtime
    assert runtime.middleware is middleware


def test_set_pipeline():

    runtime = MetricRuntimeIntegration()
    pipeline = Pipeline()

    assert runtime.set_pipeline(pipeline) is runtime
    assert runtime.pipeline is pipeline


def test_set_exporter():

    runtime = MetricRuntimeIntegration()
    exporter = Exporter()

    assert runtime.set_exporter(exporter) is runtime
    assert runtime.exporter is exporter


def test_clear_components(runtime):

    assert runtime.clear_components() is runtime

    assert runtime.processor is None
    assert runtime.middleware is None
    assert runtime.pipeline is None
    assert runtime.exporter is None

    assert len(runtime) == 0


def test_invalid_processor():

    with pytest.raises(
        TypeError,
        match="supported execution API",
    ):
        MetricRuntimeIntegration(
            processor=object()
        )


def test_invalid_middleware():

    with pytest.raises(
        TypeError,
        match="supported execution API",
    ):
        MetricRuntimeIntegration(
            middleware=object()
        )


def test_invalid_pipeline():

    with pytest.raises(
        TypeError,
        match="supported execution API",
    ):
        MetricRuntimeIntegration(
            pipeline=object()
        )


def test_invalid_exporter():

    with pytest.raises(
        TypeError,
        match="supported execution API",
    ):
        MetricRuntimeIntegration(
            exporter=object()
        )


# ==============================================================
# Execution
# ==============================================================


def test_execute(
    runtime,
    processor,
    middleware,
    pipeline,
    exporter,
):

    result = runtime.execute(
        {"value": 1}
    )

    assert result == {
        "value": 1,
        "processor": True,
        "middleware": True,
        "pipeline": True,
        "exporter": True,
    }

    assert processor.calls == 1
    assert middleware.calls == 1
    assert pipeline.calls == 1
    assert exporter.calls == 1

    stats = runtime.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_execution_order(runtime):

    calls = []

    class OrderedProcessor:

        def process(self, metric, **kwargs):
            calls.append("processor")

            return metric

    class OrderedMiddleware:

        def execute(self, metric, **kwargs):
            calls.append("middleware")

            return metric

    class OrderedPipeline:

        def execute(self, metric, **kwargs):
            calls.append("pipeline")

            return metric

    class OrderedExporter:

        def export(self, metric, **kwargs):
            calls.append("exporter")

            return metric

    runtime.set_processor(
        OrderedProcessor()
    )

    runtime.set_middleware(
        OrderedMiddleware()
    )

    runtime.set_pipeline(
        OrderedPipeline()
    )

    runtime.set_exporter(
        OrderedExporter()
    )

    runtime.execute({})

    assert calls == [
        "processor",
        "middleware",
        "pipeline",
        "exporter",
    ]


def test_empty_runtime():

    runtime = MetricRuntimeIntegration()

    metric = {
        "value": 42,
    }

    assert runtime.execute(metric) == metric

    stats = runtime.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_execute_with_kwargs():

    received = {}

    class Component:

        def execute(self, metric, **kwargs):
            received.update(kwargs)

            return metric

    runtime = MetricRuntimeIntegration(
        middleware=Component()
    )

    runtime.execute(
        {},
        source="test",
        batch=3,
    )

    assert received == {
        "source": "test",
        "batch": 3,
    }


# ==============================================================
# Aliases
# ==============================================================


def test_run(runtime):

    result = runtime.run(
        {"value": 1}
    )

    assert result["exporter"] is True


def test_process(runtime):

    result = runtime.process(
        {"value": 1}
    )

    assert result["exporter"] is True


def test_call(runtime):

    result = runtime(
        {"value": 1}
    )

    assert result["exporter"] is True


# ==============================================================
# Component API Compatibility
# ==============================================================


def test_run_component():

    runtime = MetricRuntimeIntegration(
        middleware=RunComponent()
    )

    result = runtime.execute(
        {"value": 1}
    )

    assert result["run"] is True


def test_execute_component():

    runtime = MetricRuntimeIntegration(
        middleware=ExecuteComponent()
    )

    result = runtime.execute(
        {"value": 1}
    )

    assert result["execute"] is True


def test_callable_component():

    runtime = MetricRuntimeIntegration(
        middleware=lambda metric, **kwargs: {
            **metric,
            "callable": True,
        }
    )

    result = runtime.execute(
        {"value": 1}
    )

    assert result["callable"] is True


# ==============================================================
# Batch Execution
# ==============================================================


def test_execute_many(runtime):

    results = runtime.execute_many(
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

    assert runtime.statistics()["executions"] == 3


def test_run_many(runtime):

    results = runtime.run_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


def test_process_many(runtime):

    results = runtime.process_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


# ==============================================================
# Error Handling
# ==============================================================


def test_execution_failure():

    error = RuntimeError("boom")

    class FailingMiddleware:

        def execute(self, metric, **kwargs):
            raise error

    runtime = MetricRuntimeIntegration(
        middleware=FailingMiddleware()
    )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        runtime.execute({})

    stats = runtime.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1

    assert runtime.last_error is error
    assert runtime.last_result is None


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty():

    runtime = MetricRuntimeIntegration()

    assert runtime.validate() is True


def test_validate_full(runtime):

    assert runtime.validate() is True


def test_status(runtime):

    status = runtime.status()

    assert status["enabled"] is True
    assert status["running"] is False
    assert status["closed"] is False
    assert status["active"] is True
    assert status["valid"] is True

    assert status["processor"] is True
    assert status["middleware"] is True
    assert status["pipeline"] is True
    assert status["exporter"] is True


# ==============================================================
# Lifecycle
# ==============================================================


def test_disable(runtime):

    assert runtime.disable() is runtime
    assert runtime.enabled is False
    assert runtime.active is False

    with pytest.raises(
        RuntimeError,
        match="disabled",
    ):
        runtime.execute({})


def test_enable(runtime):

    runtime.disable()

    assert runtime.enable() is runtime
    assert runtime.enabled is True
    assert runtime.active is True


def test_close(runtime):

    assert runtime.close() is runtime
    assert runtime.closed is True
    assert runtime.active is False

    with pytest.raises(
        RuntimeError,
        match="closed",
    ):
        runtime.execute({})


def test_reopen(runtime):

    runtime.close()

    assert runtime.reopen() is runtime
    assert runtime.closed is False
    assert runtime.active is True


# ==============================================================
# Diagnostics
# ==============================================================


def test_last_result(runtime):

    result = runtime.execute(
        {"value": 42}
    )

    assert runtime.last_result == result


def test_reset(runtime):

    runtime.execute(
        {"value": 1}
    )

    assert runtime.statistics()["executions"] == 1
    assert runtime.last_result is not None

    assert runtime.reset() is runtime

    assert runtime.statistics()["executions"] == 0
    assert runtime.statistics()["success"] == 0
    assert runtime.statistics()["failures"] == 0

    assert runtime.last_result is None
    assert runtime.last_error is None


def test_statistics_initial(runtime):

    stats = runtime.statistics()

    assert stats["name"] == "MetricRuntimeIntegration"
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


# ==============================================================
# Protocols
# ==============================================================


def test_len(runtime):

    assert len(runtime) == 4


def test_repr(runtime):

    value = repr(runtime)

    assert "MetricRuntimeIntegration" in value
    assert "components=4" in value


def test_str(runtime):

    assert str(runtime) == "MetricRuntimeIntegration"
