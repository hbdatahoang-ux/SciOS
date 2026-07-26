"""
SciOS-NG Runtime Metrics Processor Engine

Base processor contract for metric processing pipeline.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid
import threading

from datetime import datetime
from typing import Any



# ==================================================================
# MetricProcessor
# ==================================================================


class MetricProcessor:
    """
    Base Runtime Metrics Processor.

    All processors inherit from this class.

    Pipeline:

        Collector
            |
            v
        Processor
            |
            v
        Aggregator / Exporter
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "processor",
        description: str = "",
    ) -> None:


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self._description = description



        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled = True

        self._closed = False



        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = threading.RLock()



        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._version = "0.2"



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._processed = 0

        self._failed = 0



        # ----------------------------------------------------------
        # Hooks
        # ----------------------------------------------------------

        self._hooks = {}



    # ==============================================================
    # Processing API
    # ==============================================================

    def process(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Main processing entry.

        Override in child classes.
        """

        self._ensure_active()


        try:

            result = self.transform(
                metric,
                **kwargs,
            )


            self._processed += 1


            self._touch()


            return result


        except Exception:

            self._failed += 1

            raise



    def transform(
        self,
        metric: Any,
        **kwargs,
    ):
        """
        Transformation hook.

        Child processors implement.
        """

        return metric



    def batch(
        self,
        metrics: list[Any],
        **kwargs,
    ):

        return [

            self.process(
                metric,
                **kwargs,
            )

            for metric
            in metrics

        ]



    # ==============================================================
    # Lifecycle
    # ==============================================================

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



    # ==============================================================
    # Hooks
    # ==============================================================

    def add_hook(
        self,
        name: str,
        callback,
    ):

        self._hooks[name] = callback

        return self



    def emit(
        self,
        name: str,
        *args,
        **kwargs,
    ):

        if name in self._hooks:

            return self._hooks[name](
                *args,
                **kwargs,
            )



    # ==============================================================
    # Diagnostics
    # ==============================================================

    def statistics(
        self,
    ):

        return {

            "processed":
                self._processed,

            "failed":
                self._failed,

            "enabled":
                self._enabled,

            "closed":
                self._closed,

        }



    def status(
        self,
    ):

        return {

            "name":
                self._name,

            "active":
                self._enabled
                and
                not self._closed,

        }



    # ==============================================================
    # Internal
    # ==============================================================

    def _ensure_active(
        self,
    ):

        if not self._enabled:

            raise RuntimeError(
                "Processor disabled"
            )


        if self._closed:

            raise RuntimeError(
                "Processor closed"
            )



    def _touch(
        self,
    ):

        self._updated_at = datetime.utcnow()



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __call__(
        self,
        metric,
        **kwargs,
    ):

        return self.process(
            metric,
            **kwargs,
        )



    def __repr__(
        self,
    ):

        return (

            f"MetricProcessor("
            f"name={self._name!r}, "
            f"processed={self._processed}"
            f")"

        )