"""
SciOS-NG Runtime Metrics Async Middleware Runtime

Asynchronous middleware execution engine.

SciOS-NG v0.2
"""

from __future__ import annotations

import asyncio
import threading
import time
import uuid

from datetime import datetime
from typing import Any, Awaitable, Callable



# ==============================================================
# MetricAsyncMiddlewareRuntime
# ==============================================================


class MetricAsyncMiddlewareRuntime:
    """
    Asynchronous Runtime Middleware Engine.

    Responsibilities
    ----------------
    - Execute async middleware chain
    - Execute concurrent middleware
    - Async task scheduling
    - Runtime coordination
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricAsyncMiddlewareRuntime",
        description: str = "",
    ) -> None:

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self._id = str(uuid.uuid4())
        self._name = name
        self._description = description

        # ------------------------------------------------------
        # Middleware
        # ------------------------------------------------------

        self._middlewares: list[Any] = []
        self._registry: dict[str, Any] = {}

        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True
        self._running = False
        self._closed = False

        # ------------------------------------------------------
        # Synchronization
        # ------------------------------------------------------

        self._lock = threading.RLock()

        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------

        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at

        # ------------------------------------------------------
        # Runtime Context
        # ------------------------------------------------------

        self._context: dict[str, Any] = {}

        # ------------------------------------------------------
        # Statistics
        # ------------------------------------------------------

        self._executions = 0
        self._success = 0
        self._failures = 0

        self._total_latency = 0.0

    # ==========================================================
    # Middleware Registration
    # ==========================================================

    def add(
        self,
        middleware: Any,
    ):

        with self._lock:

            self._middlewares.append(middleware)

            self._registry[
                getattr(
                    middleware,
                    "_name",
                    str(len(self._middlewares)),
                )
            ] = middleware

        return self

    def remove(
        self,
        name: str,
    ):

        middleware = self._registry.pop(
            name,
            None,
        )

        if middleware and middleware in self._middlewares:

            self._middlewares.remove(
                middleware
            )

        return self

    def clear(
        self,
    ):

        self._middlewares.clear()
        self._registry.clear()

        return self

    # ==========================================================
    # Async Execution
    # ==========================================================

    async def execute(
        self,
        metric: Any,
        **kwargs,
    ):

        self._ensure_active()

        self._running = True

        start = time.perf_counter()

        result = metric

        try:

            for middleware in self._middlewares:

                if hasattr(
                    middleware,
                    "execute_async",
                ):

                    result = await middleware.execute_async(
                        result,
                        **kwargs,
                    )

                elif hasattr(
                    middleware,
                    "execute",
                ):

                    value = middleware.execute(
                        result,
                        **kwargs,
                    )

                    if asyncio.iscoroutine(
                        value
                    ):

                        result = await value

                    else:

                        result = value

                else:

                    result = middleware(
                        result,
                        **kwargs,
                    )

            self._executions += 1
            self._success += 1

            return result

        except Exception:

            self._executions += 1
            self._failures += 1

            raise

        finally:

            self._running = False

            self._total_latency += (
                time.perf_counter() - start
            )

    async def execute_parallel(
        self,
        metric: Any,
        **kwargs,
    ):

        self._ensure_active()

        tasks = []

        for middleware in self._middlewares:

            if hasattr(
                middleware,
                "execute_async",
            ):

                tasks.append(

                    middleware.execute_async(
                        metric,
                        **kwargs,
                    )

                )

            elif hasattr(
                middleware,
                "execute",
            ):

                tasks.append(

                    asyncio.to_thread(
                        middleware.execute,
                        metric,
                        **kwargs,
                    )

                )

        return await asyncio.gather(
            *tasks
        )

    async def execute_many(
        self,
        metrics,
        **kwargs,
    ):

        return await asyncio.gather(

            *[
                self.execute(
                    m,
                    **kwargs,
                )

                for m in metrics
            ]

        )

    # ==========================================================
    # Runtime
    # ==========================================================

    async def flush(
        self,
    ):

        await asyncio.sleep(0)

        return self

    async def reset(
        self,
    ):

        self._executions = 0
        self._success = 0
        self._failures = 0
        self._total_latency = 0.0

        return self

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(self):

        self._enabled = True
        return self

    def disable(self):

        self._enabled = False
        return self

    def close(self):

        self._closed = True
        return self

    def reopen(self):

        self._closed = False
        return self

    # ==========================================================
    # Context
    # ==========================================================

    def set_context(
        self,
        key: str,
        value: Any,
    ):

        self._context[key] = value

        return self

    def context(self):

        return dict(
            self._context
        )

    # ==========================================================
    # Diagnostics
    # ==========================================================

    @property
    def average_latency(
        self,
    ):

        if self._executions == 0:

            return 0.0

        return (
            self._total_latency
            / self._executions
        )

    def statistics(
        self,
    ):

        return {

            "middlewares": len(
                self._middlewares
            ),

            "executions": self._executions,

            "success": self._success,

            "failures": self._failures,

            "average_latency":
                self.average_latency,

        }

    def status(
        self,
    ):

        return {

            "enabled": self._enabled,

            "running": self._running,

            "closed": self._closed,

            "active":
                self._enabled
                and
                not self._closed,

        }

    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(
        self,
    ):

        if not self._enabled:

            raise RuntimeError(
                "Async middleware runtime disabled."
            )

        if self._closed:

            raise RuntimeError(
                "Async middleware runtime closed."
            )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(
        self,
    ):

        return len(
            self._middlewares
        )

    def __iter__(
        self,
    ):

        return iter(
            self._middlewares
        )

    def __contains__(
        self,
        name,
    ):

        return name in self._registry

    def __repr__(
        self,
    ):

        return (

            "MetricAsyncMiddlewareRuntime("
            f"middlewares={len(self)}, "
            f"executions={self._executions})"

        )