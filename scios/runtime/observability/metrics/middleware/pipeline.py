"""
SciOS-NG Runtime Metrics Middleware Pipeline

Middleware chain execution engine.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid
import threading

from datetime import datetime
from typing import Any



from .stage import (
    MetricMiddlewareStage,
)



# ==============================================================
# MetricMiddlewarePipeline
# ==============================================================


class MetricMiddlewarePipeline:
    """
    Runtime Metric Middleware Pipeline.

    Responsibilities
    ----------------
    - Compose middleware stages
    - Execute ordered processing chain
    - Manage pipeline lifecycle
    - Track execution statistics
    """



    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        name: str = "MetricMiddlewarePipeline",
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
        # Pipeline
        # ------------------------------------------------------

        self._stages: list[
            MetricMiddlewareStage
        ] = []


        self._stage_registry = {}



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

        self._success = 0

        self._failures = 0



        self._last_result = None



    # ==========================================================
    # Stage Management
    # ==========================================================

    def add_stage(
        self,
        stage: MetricMiddlewareStage,
    ):

        with self._lock:

            self._stages.append(
                stage
            )


            self._stage_registry[
                stage._name
            ] = stage



        return self



    def remove_stage(
        self,
        name: str,
    ):

        stage = self._stage_registry.pop(
            name,
            None,
        )


        if stage in self._stages:

            self._stages.remove(
                stage
            )


        return self



    def get_stage(
        self,
        name: str,
    ):

        return self._stage_registry.get(
            name
        )



    def stages(
        self,
    ):

        return list(
            self._stages
        )



    def clear_stages(
        self,
    ):

        self._stages.clear()

        self._stage_registry.clear()


        return self



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


        self._running = True



        try:


            for stage in self._stages:

                result = stage.execute(
                    result,
                    **kwargs
                )



            self._executions += 1

            self._success += 1


            self._last_result = result


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
    # Stage Execution Control
    # ==========================================================

    def execute_stage(
        self,
        name: str,
        metric,
        **kwargs,
    ):

        stage = self.get_stage(
            name
        )


        if stage is None:

            raise KeyError(
                f"Unknown stage: {name}"
            )


        return stage.execute(
            metric,
            **kwargs
        )



    def skip_stage(
        self,
        name: str,
    ):

        stage = self.get_stage(
            name
        )


        if stage:

            stage.disable()


        return self



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


            "success":
                self._success,


            "failures":
                self._failures,


            "stage_count":
                len(
                    self._stages
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
                "Middleware pipeline disabled"
            )


        if self._closed:

            raise RuntimeError(
                "Middleware pipeline closed"
            )



    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(
        self,
    ):

        return len(
            self._stages
        )



    def __iter__(
        self,
    ):

        return iter(
            self._stages
        )



    def __contains__(
        self,
        name,
    ):

        return name in self._stage_registry



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

            f"MetricMiddlewarePipeline("
            f"stages={len(self._stages)}, "
            f"executions={self._executions}"
            f")"

        )