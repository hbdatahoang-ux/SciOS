"""
SciOS-NG Runtime Metrics Middleware Task

Metric task middleware execution unit.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any, Callable



# ==============================================================
# MetricMiddlewareTask
# ==============================================================


class MetricMiddlewareTask:
    """
    Runtime Metric Middleware Task.

    Responsibilities
    ----------------
    - Represent executable metric task
    - Manage task lifecycle
    - Execute task handler
    - Track task state and result
    """



    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str,
        handler: Callable | None = None,
        priority: int = 0,
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
        # Handler
        # ------------------------------------------------------

        self._handler = handler



        # ------------------------------------------------------
        # Scheduling
        # ------------------------------------------------------

        self._priority = priority



        # ------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True

        self._running = False

        self._completed = False

        self._failed = False

        self._cancelled = False



        # ------------------------------------------------------
        # Result
        # ------------------------------------------------------

        self._result = None

        self._error = None



        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at



        # ------------------------------------------------------
        # Statistics
        # ------------------------------------------------------

        self._executions = 0

        self._success = 0

        self._failures = 0



    # ==========================================================
    # Execution API
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs,
    ):

        self._ensure_active()


        if self._cancelled:

            raise RuntimeError(
                "Task cancelled"
            )



        self._running = True


        try:

            if self._handler:

                result = self._handler(
                    metric,
                    **kwargs
                )

            else:

                result = metric



            self._result = result

            self._completed = True

            self._success += 1


            return result



        except Exception as exc:


            self._failed = True

            self._error = exc

            self._failures += 1


            raise



        finally:

            self._running = False

            self._executions += 1



    def run(
        self,
        metric,
        **kwargs,
    ):

        return self.execute(
            metric,
            **kwargs
        )



    def process(
        self,
        metric,
        **kwargs,
    ):

        return self.execute(
            metric,
            **kwargs
        )



    # ==========================================================
    # Handler API
    # ==========================================================

    def set_handler(
        self,
        handler: Callable,
    ):

        self._handler = handler

        return self



    def handler(
        self,
    ):

        return self._handler



    # ==========================================================
    # Task Control
    # ==========================================================

    def cancel(
        self,
    ):

        self._cancelled = True

        self._updated_at = datetime.utcnow()


        return self



    def reset(
        self,
    ):

        self._running = False

        self._completed = False

        self._failed = False

        self._cancelled = False


        self._result = None

        self._error = None


        return self



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



    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(
        self,
    ):

        return self._name



    @property
    def priority(
        self,
    ):

        return self._priority



    @property
    def result(
        self,
    ):

        return self._result



    @property
    def error(
        self,
    ):

        return self._error



    @property
    def running(
        self,
    ):

        return self._running



    @property
    def completed(
        self,
    ):

        return self._completed



    @property
    def cancelled(
        self,
    ):

        return self._cancelled



    # ==========================================================
    # Diagnostics
    # ==========================================================

    def statistics(
        self,
    ):

        return {

            "executions":
                self._executions,


            "success":
                self._success,


            "failures":
                self._failures,


            "priority":
                self._priority,

        }



    def status(
        self,
    ):

        return {

            "enabled":
                self._enabled,


            "running":
                self._running,


            "completed":
                self._completed,


            "failed":
                self._failed,


            "cancelled":
                self._cancelled,

        }



    # ==========================================================
    # Internal
    # ==========================================================

    def _ensure_active(
        self,
    ):

        if not self._enabled:

            raise RuntimeError(
                f"Task {self._name} disabled"
            )



    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __call__(
        self,
        metric,
        **kwargs,
    ):

        return self.execute(
            metric,
            **kwargs
        )



    def __repr__(
        self,
    ):

        return (

            f"MetricMiddlewareTask("
            f"name={self._name!r}, "
            f"priority={self._priority}, "
            f"executions={self._executions}"
            f")"

        )



    def __str__(
        self,
    ):

        return self._name