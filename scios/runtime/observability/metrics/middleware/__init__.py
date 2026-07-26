"""
SciOS-NG Runtime Metrics Middleware

Public API for the Runtime Metrics Middleware subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations


# ============================================================
# Core Middleware Components
# ============================================================

from .runtime import (
    MetricMiddlewareRuntime,
)

from .stage import (
    MetricMiddlewareStage,
)

from .task import (
    MetricMiddlewareTask,
)

from .pipeline import (
    MetricMiddlewarePipeline,
)

from .async_runtime import (
    MetricAsyncMiddlewareRuntime,
)



# ============================================================
# Aliases
# ============================================================

RuntimeMiddleware = MetricMiddlewareRuntime

MiddlewareStage = MetricMiddlewareStage

MiddlewareTask = MetricMiddlewareTask

MiddlewarePipeline = MetricMiddlewarePipeline

AsyncMiddlewareRuntime = MetricAsyncMiddlewareRuntime



# ============================================================
# Registry
# ============================================================

MIDDLEWARE_COMPONENTS = {

    "runtime":
        MetricMiddlewareRuntime,

    "stage":
        MetricMiddlewareStage,

    "task":
        MetricMiddlewareTask,

    "pipeline":
        MetricMiddlewarePipeline,

    "async_runtime":
        MetricAsyncMiddlewareRuntime,

}



# ============================================================
# Factory API
# ============================================================

def create_runtime(
    **kwargs,
) -> MetricMiddlewareRuntime:

    return MetricMiddlewareRuntime(
        **kwargs
    )


def create_stage(
    name: str,
    handler=None,
    **kwargs,
) -> MetricMiddlewareStage:

    return MetricMiddlewareStage(
        name=name,
        handler=handler,
        **kwargs,
    )


def create_task(
    name: str,
    handler=None,
    **kwargs,
) -> MetricMiddlewareTask:

    return MetricMiddlewareTask(
        name=name,
        handler=handler,
        **kwargs,
    )


def create_pipeline(
    **kwargs,
) -> MetricMiddlewarePipeline:

    return MetricMiddlewarePipeline(
        **kwargs,
    )


def create_async_runtime(
    **kwargs,
) -> MetricAsyncMiddlewareRuntime:

    return MetricAsyncMiddlewareRuntime(
        **kwargs,
    )



# ============================================================
# Utilities
# ============================================================

def available_components():

    return tuple(
        MIDDLEWARE_COMPONENTS.keys()
    )


def component_count():

    return len(
        MIDDLEWARE_COMPONENTS
    )


def get_component(
    name: str,
):

    return MIDDLEWARE_COMPONENTS.get(
        name
    )



# ============================================================
# Public API
# ============================================================

__all__ = [

    # Core Classes

    "MetricMiddlewareRuntime",

    "MetricMiddlewareStage",

    "MetricMiddlewareTask",

    "MetricMiddlewarePipeline",

    "MetricAsyncMiddlewareRuntime",



    # Aliases

    "RuntimeMiddleware",

    "MiddlewareStage",

    "MiddlewareTask",

    "MiddlewarePipeline",

    "AsyncMiddlewareRuntime",



    # Registry

    "MIDDLEWARE_COMPONENTS",



    # Factory

    "create_runtime",

    "create_stage",

    "create_task",

    "create_pipeline",

    "create_async_runtime",



    # Utilities

    "available_components",

    "component_count",

    "get_component",

]