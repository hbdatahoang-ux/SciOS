"""
SciOS Observability - Tracing Plugin
===================================

Runtime tracing plugin.

Responsibilities
----------------
- Bridge Runtime lifecycle to TraceManager
- Coordinate processors
- Coordinate exporters
- Attach runtime metadata
- Provide automatic tracing integration

This plugin intentionally contains no tracing business logic.
All trace/span lifecycle management is delegated to TraceManager.
"""

from __future__ import annotations

import platform
import socket
import threading
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .manager import TraceManager
from .processor import SpanProcessor
from .exporter import TraceExporter

if TYPE_CHECKING:
    from scios.runtime.plugin import RuntimePluginContext

__all__ = [
    "TracingPlugin",
]


class TracingPlugin:
    """
    Runtime tracing plugin.

    This plugin acts as an adapter between the SciOS Runtime
    lifecycle and the tracing subsystem.

    Notes
    -----
    The plugin owns no trace state itself.
    All tracing state is maintained by TraceManager.
    """

    def __init__(
        self,
        manager: TraceManager,
        *,
        processors: list[SpanProcessor] | None = None,
        exporters: list[TraceExporter] | None = None,
        enabled: bool = True,
        auto_runtime_trace: bool = True,
        auto_stage_span: bool = True,
        auto_task_span: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the tracing plugin.

        Parameters
        ----------
        manager
            Shared TraceManager instance.

        processors
            Optional processor chain.

        exporters
            Optional exporter chain.

        enabled
            Enable or disable tracing globally.

        auto_runtime_trace
            Automatically create a root runtime trace.

        auto_stage_span
            Automatically create spans around runtime stages.

        auto_task_span
            Automatically create spans around runtime tasks.

        metadata
            Static metadata attached to every root trace.
        """

        self.manager = manager

        self.enabled = enabled

        self.auto_runtime_trace = auto_runtime_trace

        self.auto_stage_span = auto_stage_span

        self.auto_task_span = auto_task_span

        self.processors: list[SpanProcessor] = (
            list(processors)
            if processors is not None
            else []
        )

        self.exporters: list[TraceExporter] = (
            list(exporters)
            if exporters is not None
            else []
        )

        self.metadata: dict[str, Any] = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        #
        # Runtime information
        #
        self.hostname = socket.gethostname()

        self.platform = platform.system()

        self.platform_release = platform.release()

        self.python_version = platform.python_version()

        self.process_id = None

        try:
            import os

            self.process_id = os.getpid()

        except Exception:
            self.process_id = None

        self.thread_id = threading.get_ident()

        self.started_at: datetime | None = None

        self.runtime_name: str | None = None

    # =====================================================
    # Configuration
    # =====================================================

    @property
    def configured(self) -> bool:
        """
        Returns True if tracing is enabled.
        """

        return self.enabled

    @property
    def processor_count(self) -> int:
        """
        Number of registered processors.
        """

        return len(self.processors)

    @property
    def exporter_count(self) -> int:
        """
        Number of registered exporters.
        """

        return len(self.exporters)

    # =====================================================
    # Registration
    # =====================================================

    def add_processor(
        self,
        processor: SpanProcessor,
    ) -> None:
        """
        Register a span processor.
        """

        self.processors.append(processor)

    def add_exporter(
        self,
        exporter: TraceExporter,
    ) -> None:
        """
        Register a trace exporter.
        """

        self.exporters.append(exporter)
        