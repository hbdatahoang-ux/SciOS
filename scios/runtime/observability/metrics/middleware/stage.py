"""
SciOS-NG Runtime Metrics Middleware Stage

Middleware stage execution engine.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any, Callable



# ==============================================================
# MetricMiddlewareStage
# ==============================================================


class MetricMiddlewareStage:
    """
    Middleware Stage Execution.

    Responsibilities
    ----------------
    - Represent a single middleware stage
    - Execute stage handler
    - Manage stage lifecycle
    - Provide stage metrics
    """



    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str,
        handler: Callable | None = None,
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
        # Runtime State
        # ------------------------------------------------------

        self._enabled = True

        self._running = False

        self._closed = False



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



        self._last_result = None



    # ==========================================================
    # Execution API
    # ==========================================================

    def execute(
        self,
        metric: Any,
        **kwargs,
    ):

        self._ensure_active()


        self._running = True


        try:

            if self._handler:

                result = self._handler(
                    metric,
                    **kwargs
                )

            else:

                result = metric



            self._success += 1


            self._executions += 1


            self._last_result = result


            return result



        except Exception:

            self._failures += 1

            self._executions += 1

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
    # Handler Management
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

            "name":
                self._name,


            "executions":
                self._executions,


            "success":
                self._success,


            "failures":
                self._failures,

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
                f"Stage {self._name} disabled"
            )


        if self._closed:

            raise RuntimeError(
                f"Stage {self._name} closed"
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

            f"MetricMiddlewareStage("
            f"name={self._name!r}, "
            f"executions={self._executions}"
            f")"

        )



    def __str__(
        self,
    ):

        return self._name