"""
SciOS-NG Runtime Metrics Middleware Runtime

Middleware execution foundation.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid
import threading

from datetime import datetime
from typing import Any, Callable



# ==============================================================
# MetricMiddlewareRuntime
# ==============================================================


class MetricMiddlewareRuntime:
    """
    Runtime Middleware Engine.

    Responsibilities
    ----------------
    - Manage middleware chain
    - Execute middleware hooks
    - Provide runtime context
    - Coordinate metric processing flow
    """



    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricMiddlewareRuntime",
        description: str = "",
    ):


        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self._description = description



        # ------------------------------------------------------
        # Middleware Registry
        # ------------------------------------------------------

        self._middlewares = []

        self._registry = {}



        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True

        self._running = False

        self._closed = False



        # ------------------------------------------------------
        # Context
        # ------------------------------------------------------

        self._context = {}



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
        # Statistics
        # ------------------------------------------------------

        self._executions = 0

        self._failures = 0



    # ==========================================================
    # Middleware Registration
    # ==========================================================

    def add(
        self,
        middleware,
    ):

        with self._lock:

            self._middlewares.append(
                middleware
            )


        return self



    def remove(
        self,
        middleware,
    ):

        if middleware in self._middlewares:

            self._middlewares.remove(
                middleware
            )


        return self



    def clear(
        self,
    ):

        self._middlewares.clear()

        return self



    def middlewares(
        self,
    ):

        return list(
            self._middlewares
        )



    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs,
    ):

        self._ensure_active()


        result = metric



        try:

            self._running = True


            for middleware in self._middlewares:

                result = middleware.process(
                    result,
                    **kwargs
                )



            self._executions += 1


            return result



        except Exception:

            self._failures += 1

            raise



        finally:

            self._running = False



    def run(
        self,
        metric,
        **kwargs,
    ):

        return self.execute(
            metric,
            **kwargs
        )



    # ==========================================================
    # Context
    # ==========================================================

    def set_context(
        self,
        key,
        value,
    ):

        self._context[key] = value

        return self



    def context(
        self,
    ):

        return dict(
            self._context
        )



    # ==========================================================
    # Lifecycle
    # ==========================================================

    def enable(
        self,
    ):

        self._enabled = True

        return self



    def disable(
        self,
    ):

        self._enabled = False

        return self



    def close(
        self,
    ):

        self._closed = True

        return self



    def reopen(
        self,
    ):

        self._closed = False

        return self



    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(
        self,
    ):

        return {

            "executions":
                self._executions,


            "failures":
                self._failures,


            "middleware_count":
                len(
                    self._middlewares
                ),

        }



    def status(
        self,
    ):

        return {

            "enabled":
                self._enabled,


            "running":
                self._running,


            "closed":
                self._closed,


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
                "Middleware runtime disabled"
            )


        if self._closed:

            raise RuntimeError(
                "Middleware runtime closed"
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



    def __repr__(
        self,
    ):

        return (

            f"MetricMiddlewareRuntime("
            f"middlewares={len(self._middlewares)}, "
            f"executions={self._executions}"
            f")"

        )