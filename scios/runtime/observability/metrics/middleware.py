"""
SciOS-NG Metrics Middleware
===========================

Middleware layer for runtime metrics integration.

Responsibilities
-----------------
- Intercept runtime execution lifecycle.
- Collect metrics automatically.
- Wrap execution functions.
- Connect Runtime with Metrics subsystem.

Design
------
Middleware does NOT store metric data.
It delegates to:

- MetricRegistry
- Collector
- Recorder
- Plugin

Python 3.11+
"""

from __future__ import annotations


from functools import wraps
from typing import Any, Callable


__all__ = [
    "MetricsMiddleware",
    "metric_middleware",
]



# ==========================================================
# Metrics Middleware
# ==========================================================


class MetricsMiddleware:
    """
    Runtime metrics middleware.

    Example
    -------

        middleware = MetricsMiddleware(
            registry
        )

        wrapped = middleware.wrap(
            function
        )

    """


    def __init__(
        self,
        registry: Any,
        collector: Any | None = None,
    ):
        self.registry = registry

        self.collector = collector



    # ======================================================
    # Execution Wrapper
    # ======================================================


    def wrap(
        self,
        func: Callable,
    ) -> Callable:
        """
        Wrap callable with metrics collection.
        """


        @wraps(func)
        def wrapper(
            *args,
            **kwargs,
        ):

            metric = self._before(
                func
            )


            try:

                result = func(
                    *args,
                    **kwargs,
                )


                self._success(
                    metric,
                    result,
                )


                return result



            except Exception as exc:

                self._failure(
                    metric,
                    exc,
                )

                raise



            finally:

                self._finish(
                    metric
                )



        return wrapper



    # ======================================================
    # Lifecycle Hooks
    # ======================================================


    def _before(
        self,
        func: Callable,
    ):

        if self.collector:

            return self.collector.start(
                func.__name__
            )


        return None



    def _success(
        self,
        metric,
        result,
    ):

        if self.collector:

            self.collector.complete(
                metric,
                result,
            )



    def _failure(
        self,
        metric,
        error: Exception,
    ):

        if self.collector:

            self.collector.fail(
                metric,
                error,
            )



    def _finish(
        self,
        metric,
    ):

        if self.collector:

            self.collector.finish(
                metric
            )



    # ======================================================
    # Runtime Integration
    # ======================================================


    def before_execute(
        self,
        context,
        *args,
        **kwargs,
    ):

        if self.collector:

            return self.collector.start(
                context
            )



    def execution_completed(
        self,
        context,
        result,
        *args,
        **kwargs,
    ):

        if self.collector:

            self.collector.complete(
                context,
                result,
            )



    def execution_failed(
        self,
        context,
        error,
        *args,
        **kwargs,
    ):

        if self.collector:

            self.collector.fail(
                context,
                error,
            )



    def snapshot(
        self,
    ):

        if self.registry:

            return self.registry.snapshot()

        return {}



    def reset(
        self,
    ):

        if self.registry:

            return self.registry.reset()



# ==========================================================
# Decorator API
# ==========================================================


def metric_middleware(
    middleware: MetricsMiddleware,
):

    """
    Function decorator.

    Example:

        @metric_middleware(metrics)
        def compute():
            ...

    """


    def decorator(
        func: Callable,
    ):

        return middleware.wrap(
            func
        )


    return decorator