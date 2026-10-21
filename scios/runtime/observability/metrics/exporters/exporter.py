"""
SciOS-NG Runtime Metrics Exporter Engine

Base interface for exporting runtime metrics.

SciOS-NG v0.2
"""


from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from threading import RLock
from typing import Any
from uuid import uuid4



# ==================================================================
# MetricExporter
# ==================================================================


class MetricExporter(
    ABC
):
    """
    Base Runtime Metrics Exporter.

    Responsibilities
    ----------------
    - Export runtime metrics
    - Manage exporter lifecycle
    - Provide serialization boundary
    - Integrate observability backends
    """

    VERSION = "0.2.0"



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MetricExporter",
        description: str = "",
    ) -> None:


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id = str(
            uuid4()
        )

        self._name = name

        self._description = description



        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled = True

        self._initialized = False

        self._running = False

        self._closed = False



        # ----------------------------------------------------------
        # Export State
        # ----------------------------------------------------------

        self._exports = 0

        self._failures = 0

        self._last_export = None



        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = RLock()



        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        now = datetime.utcnow()

        self._created_at = now

        self._updated_at = now

        self._version = self.VERSION



        # ----------------------------------------------------------
        # Internal
        # ----------------------------------------------------------

        self._config = {}

        self._hooks = {}

        self._events = []

        self._snapshot = None

        self._context = {}



    # ==============================================================
    # Internal Utilities
    # ==============================================================

    def _touch(
        self,
    ):
        """
        Update timestamp.
        """

        self._updated_at = datetime.utcnow()



    def _ensure_open(
        self,
    ):
        """
        Validate exporter state.
        """

        if self._closed:

            raise RuntimeError(
                "Exporter is closed."
            )



    def _ensure_enabled(
        self,
    ):
        """
        Validate exporter availability.
        """

        self._ensure_open()


        if not self._enabled:

            raise RuntimeError(
                "Exporter is disabled."
            )



    # ==============================================================
    # Export API
    # ==============================================================

    @abstractmethod
    def export(
        self,
        metrics: Any,
        **kwargs,
    ):
        """
        Export metrics.

        Must be implemented by backend.
        """

        raise NotImplementedError



    def flush(
        self,
    ):
        """
        Flush exporter buffer.
        """

        return None



    def close(
        self,
    ):
        """
        Close exporter.
        """

        with self._lock:

            self._closed = True

            self._running = False

            self._touch()



        return self



    # ==============================================================
    # Properties
    # ==============================================================

    @property
    def enabled(
        self,
    ) -> bool:

        return self._enabled



    @property
    def closed(
        self,
    ) -> bool:

        return self._closed



    @property
    def running(
        self,
    ) -> bool:

        return self._running