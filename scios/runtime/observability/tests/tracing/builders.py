"""
scios.runtime.observability.tests.tracing.builders

Builder utilities for tracing test objects.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .fakes import (
    FakeExporter,
    FakeProcessor,
    FakeSpan,
    FakeTrace,
    FakeTraceManager,
)


# ============================================================================
# Base Builder
# ============================================================================


class Builder:
    """Base fluent builder."""

    def build(self):
        raise NotImplementedError


# ============================================================================
# TraceBuilder
# ============================================================================


class TraceBuilder(Builder):
    """Builder for FakeTrace."""

    def __init__(self) -> None:
        self._trace = FakeTrace(name="Trace")

    def with_name(self, name: str) -> "TraceBuilder":
        self._trace.name = name
        return self

    def with_status(self, status: str) -> "TraceBuilder":
        self._trace.status = status
        return self

    def with_attribute(
        self,
        key: str,
        value: Any,
    ) -> "TraceBuilder":
        self._trace.set_attribute(key, value)
        return self

    def with_attributes(
        self,
        attrs: dict[str, Any],
    ) -> "TraceBuilder":
        for k, v in attrs.items():
            self._trace.set_attribute(k, v)
        return self

    def with_metadata(
        self,
        metadata: dict[str, Any],
    ) -> "TraceBuilder":
        for k, v in metadata.items():
            self._trace.set_metadata(k, v)
        return self

    def with_event(
        self,
        name: str,
        **attrs: Any,
    ) -> "TraceBuilder":
        self._trace.add_event(name, **attrs)
        return self

    def started(self) -> "TraceBuilder":
        self._trace.start()
        return self

    def finished(
        self,
        status: str = "SUCCESS",
    ) -> "TraceBuilder":
        self._trace.finish(status)
        return self

    def build(self) -> FakeTrace:
        return deepcopy(self._trace)


# ============================================================================
# SpanBuilder
# ============================================================================


class SpanBuilder(Builder):
    """Builder for FakeSpan."""

    def __init__(self) -> None:
        self._span = FakeSpan(name="Span")

    def with_name(self, name: str) -> "SpanBuilder":
        self._span.name = name
        return self

    def with_trace(
        self,
        trace: FakeTrace,
    ) -> "SpanBuilder":
        self._span.trace_id = trace.trace_id
        return self

    def with_parent(
        self,
        parent: FakeSpan,
    ) -> "SpanBuilder":
        self._span.parent = parent
        self._span.parent_span_id = parent.span_id
        parent.add_child(self._span)
        return self

    def with_attribute(
        self,
        key: str,
        value: Any,
    ) -> "SpanBuilder":
        self._span.set_attribute(key, value)
        return self

    def with_attributes(
        self,
        attrs: dict[str, Any],
    ) -> "SpanBuilder":
        for k, v in attrs.items():
            self._span.set_attribute(k, v)
        return self

    def with_event(
        self,
        name: str,
        **attrs: Any,
    ) -> "SpanBuilder":
        self._span.add_event(name, **attrs)
        return self

    def started(self) -> "SpanBuilder":
        self._span.start()
        return self

    def finished(
        self,
        status: str = "SUCCESS",
    ) -> "SpanBuilder":
        self._span.finish(status)
        return self

    def build(self) -> FakeSpan:
        return deepcopy(self._span)


# ============================================================================
# PluginBuilder
# ============================================================================


class PluginBuilder(Builder):

    def __init__(self) -> None:

        from scios.runtime.observability.tracing.plugin import TracingPlugin

        self._manager = FakeTraceManager()

        self._processors: list[FakeProcessor] = []

        self._exporters: list[FakeExporter] = []

        self._enabled = True

        # Default plugin class
        self._plugin_cls = TracingPlugin

    def using(
        self,
        plugin_cls,
    ) -> "PluginBuilder":
        self._plugin_cls = plugin_cls
        return self

    def with_manager(
        self,
        manager: FakeTraceManager,
    ) -> "PluginBuilder":
        self._manager = manager
        return self

    def with_processor(
        self,
        processor: FakeProcessor,
    ) -> "PluginBuilder":
        self._processors.append(processor)
        return self

    def with_processors(
        self,
        processors: list[FakeProcessor],
    ) -> "PluginBuilder":
        self._processors.extend(processors)
        return self

    def with_exporter(
        self,
        exporter: FakeExporter,
    ) -> "PluginBuilder":
        self._exporters.append(exporter)
        return self

    def with_exporters(
        self,
        exporters: list[FakeExporter],
    ) -> "PluginBuilder":
        self._exporters.extend(exporters)
        return self

    def enabled(
        self,
        value: bool = True,
    ) -> "PluginBuilder":
        self._enabled = value
        return self

    def build(self):

        if self._plugin_cls is None:
            raise RuntimeError(
                "Plugin class not configured. "
                "Use PluginBuilder().using(TracingPlugin)."
            )

        return self._plugin_cls(
            manager=self._manager,
            processors=self._processors,
            exporters=self._exporters,
            enabled=self._enabled,
        )


# ============================================================================
# Convenience Builders
# ============================================================================


def build_trace(
    name: str = "Trace",
) -> FakeTrace:
    return TraceBuilder().with_name(name).build()


def build_span(
    name: str = "Span",
) -> FakeSpan:
    return SpanBuilder().with_name(name).build()


__all__ = [
    "Builder",
    "TraceBuilder",
    "SpanBuilder",
    "PluginBuilder",
    "build_trace",
    "build_span",
]