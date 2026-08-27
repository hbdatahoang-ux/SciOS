"""
SciOS-NG Runtime Metrics Middleware

Public API for the Runtime Metrics Middleware subsystem.

SciOS-NG v0.2
"""

from __future__ import annotations


# ============================================================
# Core Middleware Components
# ============================================================

from .middleware import (
    MetricMiddleware,
)

from .async_middleware import (
    MetricAsyncMiddleware,
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


# ============================================================
# Aliases
# ============================================================

Middleware = MetricMiddleware

AsyncMiddleware = MetricAsyncMiddleware

MiddlewareStage = MetricMiddlewareStage

MiddlewareTask = MetricMiddlewareTask

MiddlewarePipeline = MetricMiddlewarePipeline


# ============================================================
# Registry
# ============================================================

MIDDLEWARE_COMPONENTS = {
    "middleware": MetricMiddleware,
    "async_middleware": MetricAsyncMiddleware,
    "stage": MetricMiddlewareStage,
    "task": MetricMiddlewareTask,
    "pipeline": MetricMiddlewarePipeline,
}


# ============================================================
# Factory API
# ============================================================

def create_middleware(
    handler=None,
    **kwargs,
) -> MetricMiddleware:
    """
    Create a synchronous metric middleware.
    """

    return MetricMiddleware(
        handler=handler,
        **kwargs,
    )


def create_async_middleware(
    handler=None,
    **kwargs,
) -> MetricAsyncMiddleware:
    """
    Create an asynchronous metric middleware.
    """

    return MetricAsyncMiddleware(
        handler=handler,
        **kwargs,
    )


def create_stage(
    name: str,
    handler=None,
    **kwargs,
) -> MetricMiddlewareStage:
    """
    Create a middleware stage.
    """

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
    """
    Create a middleware task.
    """

    return MetricMiddlewareTask(
        name=name,
        handler=handler,
        **kwargs,
    )


def create_pipeline(
    **kwargs,
) -> MetricMiddlewarePipeline:
    """
    Create a middleware pipeline.
    """

    return MetricMiddlewarePipeline(
        **kwargs,
    )


# ============================================================
# Utilities
# ============================================================

def available_components() -> tuple[str, ...]:
    """
    Return registered middleware component names.
    """

    return tuple(
        MIDDLEWARE_COMPONENTS.keys()
    )


def component_count() -> int:
    """
    Return number of registered middleware components.
    """

    return len(
        MIDDLEWARE_COMPONENTS
    )


def get_component(
    name: str,
):
    """
    Return a middleware component class by name.

    Returns None when the component is unknown.
    """

    return MIDDLEWARE_COMPONENTS.get(
        name
    )


# ============================================================
# Public API
# ============================================================

__all__ = [

    # Core classes

    "MetricMiddleware",
    "MetricAsyncMiddleware",
    "MetricMiddlewareStage",
    "MetricMiddlewareTask",
    "MetricMiddlewarePipeline",

    # Aliases

    "Middleware",
    "AsyncMiddleware",
    "MiddlewareStage",
    "MiddlewareTask",
    "MiddlewarePipeline",

    # Registry

    "MIDDLEWARE_COMPONENTS",

    # Factories

    "create_middleware",
    "create_async_middleware",
    "create_stage",
    "create_task",
    "create_pipeline",

    # Utilities

    "available_components",
    "component_count",
    "get_component",
]