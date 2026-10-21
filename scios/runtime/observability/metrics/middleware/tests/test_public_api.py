"""
Tests for SciOS Runtime Metrics Middleware public API.
"""

from __future__ import annotations

from .. import (
    AsyncMiddleware,
    MIDDLEWARE_COMPONENTS,
    MetricAsyncMiddleware,
    MetricMiddleware,
    MetricMiddlewarePipeline,
    MetricMiddlewareStage,
    MetricMiddlewareTask,
    Middleware,
    MiddlewarePipeline,
    MiddlewareStage,
    MiddlewareTask,
    available_components,
    component_count,
    create_async_middleware,
    create_middleware,
    create_pipeline,
    create_stage,
    create_task,
    get_component,
)


# ==============================================================
# Public Classes
# ==============================================================


def test_metric_middleware_exported():
    assert MetricMiddleware is not None


def test_metric_async_middleware_exported():
    assert MetricAsyncMiddleware is not None


def test_metric_stage_exported():
    assert MetricMiddlewareStage is not None


def test_metric_task_exported():
    assert MetricMiddlewareTask is not None


def test_metric_pipeline_exported():
    assert MetricMiddlewarePipeline is not None


# ==============================================================
# Aliases
# ==============================================================


def test_middleware_alias():
    assert Middleware is MetricMiddleware


def test_async_middleware_alias():
    assert AsyncMiddleware is MetricAsyncMiddleware


def test_stage_alias():
    assert MiddlewareStage is MetricMiddlewareStage


def test_task_alias():
    assert MiddlewareTask is MetricMiddlewareTask


def test_pipeline_alias():
    assert MiddlewarePipeline is MetricMiddlewarePipeline


# ==============================================================
# Registry
# ==============================================================


def test_registry():
    assert MIDDLEWARE_COMPONENTS == {
        "middleware": MetricMiddleware,
        "async_middleware": MetricAsyncMiddleware,
        "stage": MetricMiddlewareStage,
        "task": MetricMiddlewareTask,
        "pipeline": MetricMiddlewarePipeline,
    }


def test_component_count():
    assert component_count() == 5


def test_available_components():
    assert available_components() == (
        "middleware",
        "async_middleware",
        "stage",
        "task",
        "pipeline",
    )


def test_get_component():
    assert get_component("middleware") is MetricMiddleware
    assert get_component("async_middleware") is MetricAsyncMiddleware
    assert get_component("stage") is MetricMiddlewareStage
    assert get_component("task") is MetricMiddlewareTask
    assert get_component("pipeline") is MetricMiddlewarePipeline


def test_get_unknown_component():
    assert get_component("unknown") is None


# ==============================================================
# Factories
# ==============================================================


def test_create_middleware():
    middleware = create_middleware()

    assert isinstance(
        middleware,
        MetricMiddleware,
    )


def test_create_middleware_with_handler():
    handler = lambda metric: metric

    middleware = create_middleware(
        handler=handler,
    )

    assert isinstance(
        middleware,
        MetricMiddleware,
    )
    assert middleware.handler() is handler


def test_create_async_middleware():
    middleware = create_async_middleware()

    assert isinstance(
        middleware,
        MetricAsyncMiddleware,
    )


def test_create_async_middleware_with_handler():
    handler = lambda metric: metric

    middleware = create_async_middleware(
        handler=handler,
    )

    assert isinstance(
        middleware,
        MetricAsyncMiddleware,
    )
    assert middleware.handler() is handler


def test_create_stage():
    stage = create_stage(
        "test",
    )

    assert isinstance(
        stage,
        MetricMiddlewareStage,
    )
    assert stage.name == "test"


def test_create_stage_with_handler():
    handler = lambda metric: metric

    stage = create_stage(
        "test",
        handler=handler,
    )

    assert stage.handler() is handler


def test_create_task():
    task = create_task(
        "test",
    )

    assert isinstance(
        task,
        MetricMiddlewareTask,
    )
    assert task.name == "test"


def test_create_task_with_handler():
    handler = lambda metric: metric

    task = create_task(
        "test",
        handler=handler,
    )

    assert task.handler() is handler


def test_create_pipeline():
    pipeline = create_pipeline()

    assert isinstance(
        pipeline,
        MetricMiddlewarePipeline,
    )


# ==============================================================
# Factory Configuration
# ==============================================================


def test_create_middleware_forwards_kwargs():
    middleware = create_middleware(
        name="custom",
        description="test",
    )

    assert middleware.name == "custom"
    assert middleware.description == "test"


def test_create_async_middleware_forwards_kwargs():
    middleware = create_async_middleware(
        name="custom",
        description="test",
    )

    assert middleware.name == "custom"
    assert middleware.description == "test"


def test_create_stage_forwards_kwargs():
    stage = create_stage(
        "custom",
        description="test",
    )

    assert stage.name == "custom"
    assert stage.description == "test"


def test_create_task_forwards_kwargs():
    task = create_task(
        "custom",
        priority=10,
        description="test",
    )

    assert task.name == "custom"
    assert task.priority == 10
    assert task.description == "test"


def test_create_pipeline_forwards_kwargs():
    pipeline = create_pipeline(
        name="custom",
        description="test",
    )

    assert pipeline.name == "custom"
    assert pipeline.description == "test"


# ==============================================================
# Public API Consistency
# ==============================================================


def test_all_components_are_classes():
    for component in MIDDLEWARE_COMPONENTS.values():
        assert isinstance(
            component,
            type,
        )


def test_registry_matches_factories():
    assert get_component("middleware") is MetricMiddleware
    assert get_component("async_middleware") is MetricAsyncMiddleware
    assert get_component("stage") is MetricMiddlewareStage
    assert get_component("task") is MetricMiddlewareTask
    assert get_component("pipeline") is MetricMiddlewarePipeline