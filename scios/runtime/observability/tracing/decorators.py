"""
SciOS Observability - Tracing Decorators
========================================

High-level decorators for automatic tracing.

Example
-------
@trace()
def foo():
    ...

@trace(name="database.query")
def query():
    ...

@trace_async()
async def download():
    ...

@trace_class()
class Planner:
    ...
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import time
from typing import Any, Callable, Optional

from .manager import TraceManager
from .status import SpanStatus


__all__ = [
    "trace",
    "trace_async",
    "trace_method",
    "trace_class",
    "trace_generator",
    "measure",
    "record_exceptions",
]


# ==========================================================
# Helpers
# ==========================================================


def _manager() -> TraceManager:
    return TraceManager.get_global()


def _function_name(fn: Callable[..., Any]) -> str:
    return f"{fn.__module__}.{fn.__qualname__}"


# ==========================================================
# Trace decorator
# ==========================================================


def trace(
    name: Optional[str] = None,
    **attributes: Any,
):
    """
    Trace any synchronous function.
    """

    def decorator(func: Callable[..., Any]):

        if inspect.iscoroutinefunction(func):
            return trace_async(
                name=name,
                **attributes,
            )(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            manager = _manager()

            span = manager.start_span(
                name=name or _function_name(func),
                attributes=attributes,
            )

            try:

                result = func(*args, **kwargs)

                span.set_status(
                    SpanStatus.OK
                )

                return result

            except Exception as exc:

                span.record_exception(exc)

                span.set_status(
                    SpanStatus.ERROR
                )

                raise

            finally:

                manager.end_span(span)

        return wrapper

    return decorator


# ==========================================================
# Async decorator
# ==========================================================


def trace_async(
    name: Optional[str] = None,
    **attributes: Any,
):
    """
    Trace async coroutine.
    """

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            manager = _manager()

            span = manager.start_span(
                name=name or _function_name(func),
                attributes=attributes,
            )

            try:

                result = await func(
                    *args,
                    **kwargs,
                )

                span.set_status(
                    SpanStatus.OK
                )

                return result

            except Exception as exc:

                span.record_exception(exc)

                span.set_status(
                    SpanStatus.ERROR
                )

                raise

            finally:

                manager.end_span(span)

        return wrapper

    return decorator


# ==========================================================
# Method decorator
# ==========================================================


def trace_method(
    name: Optional[str] = None,
    **attributes: Any,
):
    """
    Same as trace(), intended for class methods.
    """

    return trace(
        name=name,
        **attributes,
    )


# ==========================================================
# Generator decorator
# ==========================================================


def trace_generator(
    name: Optional[str] = None,
):
    """
    Trace generators.
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            manager = _manager()

            span = manager.start_span(
                name=name or _function_name(func),
            )

            try:

                for value in func(
                    *args,
                    **kwargs,
                ):
                    yield value

                span.set_status(
                    SpanStatus.OK
                )

            except Exception as exc:

                span.record_exception(exc)

                span.set_status(
                    SpanStatus.ERROR
                )

                raise

            finally:

                manager.end_span(span)

        return wrapper

    return decorator


# ==========================================================
# Class decorator
# ==========================================================


def trace_class():

    """
    Automatically instrument all public methods.
    """

    def decorator(cls):

        for name, member in vars(cls).items():

            if name.startswith("_"):
                continue

            if inspect.isfunction(member):

                setattr(
                    cls,
                    name,
                    trace_method()(member),
                )

            elif inspect.iscoroutinefunction(member):

                setattr(
                    cls,
                    name,
                    trace_async()(member),
                )

        return cls

    return decorator


# ==========================================================
# Exception recorder
# ==========================================================


def record_exceptions(func):

    """
    Record exceptions into current active span.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:

            return func(*args, **kwargs)

        except Exception as exc:

            span = _manager().current_span()

            if span is not None:

                span.record_exception(exc)

                span.set_status(
                    SpanStatus.ERROR
                )

            raise

    return wrapper


# ==========================================================
# Measure execution time
# ==========================================================


def measure(name: Optional[str] = None):

    """
    Lightweight execution timer.
    """

    def decorator(func):

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                t0 = time.perf_counter()

                try:
                    return await func(
                        *args,
                        **kwargs,
                    )

                finally:

                    dt = (
                        time.perf_counter()
                        - t0
                    )

                    manager = _manager()

                    span = manager.current_span()

                    if span is not None:

                        span.set_attribute(
                            "execution.seconds",
                            dt,
                        )

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            t0 = time.perf_counter()

            try:

                return func(
                    *args,
                    **kwargs,
                )

            finally:

                dt = (
                    time.perf_counter()
                    - t0
                )

                span = _manager().current_span()

                if span is not None:

                    span.set_attribute(
                        "execution.seconds",
                        dt,
                    )

        return wrapper

    return decorator