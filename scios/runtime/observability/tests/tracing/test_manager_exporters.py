"""
Tests for TraceManager exporter pipeline.

Coverage
--------
- exporter registration
- trace export
- span export
- flush
- shutdown
- ordering
- duplicate prevention
- reset interaction
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Dummy Exporter
# ==========================================================


class DummyExporter:

    def __init__(self):

        self.calls = []

    # ------------------------------------------------------

    def export_trace(self, trace):

        self.calls.append(
            (
                "trace",
                trace,
            )
        )

    def export_span(self, span):

        self.calls.append(
            (
                "span",
                span,
            )
        )

    # ------------------------------------------------------

    def flush(self):

        self.calls.append(
            (
                "flush",
            )
        )

    def shutdown(self):

        self.calls.append(
            (
                "shutdown",
            )
        )


# ==========================================================
# Helpers
# ==========================================================


def create_manager():

    exporter = DummyExporter()

    manager = TraceManager(
        exporters=[exporter],
    )

    manager.start_trace("runtime")

    return manager, exporter


# ==========================================================
# Registry
# ==========================================================


def test_add_exporter():

    manager = TraceManager()

    exporter = DummyExporter()

    manager.add_exporter(exporter)

    assert exporter in manager.exporters


def test_remove_exporter():

    manager = TraceManager()

    exporter = DummyExporter()

    manager.add_exporter(exporter)

    manager.remove_exporter(exporter)

    assert exporter not in manager.exporters


def test_clear_exporters():

    manager = TraceManager()

    manager.add_exporter(DummyExporter())

    manager.add_exporter(DummyExporter())

    manager.clear_exporters()

    assert manager.exporters == []


def test_duplicate_exporter_not_added():

    manager = TraceManager()

    exporter = DummyExporter()

    manager.add_exporter(exporter)

    manager.add_exporter(exporter)

    assert manager.exporters.count(exporter) == 1


# ==========================================================
# Trace Export
# ==========================================================


def test_trace_export_called():

    manager, exporter = create_manager()

    manager.finish_trace()

    assert exporter.calls[0][0] == "trace"


def test_trace_export_once():

    manager, exporter = create_manager()

    manager.finish_trace()

    exports = [

        c

        for c in exporter.calls

        if c[0] == "trace"

    ]

    assert len(exports) == 1


# ==========================================================
# Span Export
# ==========================================================


def test_span_export_called():

    manager, exporter = create_manager()

    manager.start_span("planner")

    manager.finish_span()

    assert exporter.calls[0][0] == "span"


def test_multiple_span_exports():

    manager, exporter = create_manager()

    for i in range(3):

        manager.start_span(f"span-{i}")

        manager.finish_span()

    spans = [

        c

        for c in exporter.calls

        if c[0] == "span"

    ]

    assert len(spans) == 3


# ==========================================================
# Flush
# ==========================================================


def test_flush_calls_exporter():

    manager, exporter = create_manager()

    manager.flush()

    assert exporter.calls[-1][0] == "flush"


def test_flush_multiple_exporters():

    e1 = DummyExporter()

    e2 = DummyExporter()

    manager = TraceManager(

        exporters=[e1, e2]

    )

    manager.flush()

    assert e1.calls[-1][0] == "flush"

    assert e2.calls[-1][0] == "flush"


# ==========================================================
# Shutdown
# ==========================================================


def test_shutdown_calls_flush_then_shutdown():

    manager, exporter = create_manager()

    manager.shutdown()

    names = [

        c[0]

        for c in exporter.calls

    ]

    assert "flush" in names

    assert "shutdown" in names


def test_shutdown_resets_manager():

    manager, exporter = create_manager()

    manager.shutdown()

    assert manager.active_trace_count == 0

    assert manager.completed_trace_count == 0

    assert manager.current_trace is None


# ==========================================================
# Ordering
# ==========================================================


def test_span_export_before_trace_export():

    manager, exporter = create_manager()

    manager.start_span("planner")

    manager.finish_span()

    manager.finish_trace()

    names = [

        c[0]

        for c in exporter.calls

    ]

    assert names == [

        "span",

        "trace",

    ]


def test_exporter_order_preserved():

    e1 = DummyExporter()

    e2 = DummyExporter()

    manager = TraceManager(

        exporters=[e1, e2]

    )

    manager.start_trace("runtime")

    manager.finish_trace()

    assert e1.calls[0][0] == "trace"

    assert e2.calls[0][0] == "trace"


# ==========================================================
# Reset Interaction
# ==========================================================


def test_reset_does_not_export():

    manager, exporter = create_manager()

    manager.reset()

    assert exporter.calls == []


# ==========================================================
# Regression
# ==========================================================


def test_manager_without_exporters():

    manager = TraceManager()

    manager.start_trace("runtime")

    manager.start_span("planner")

    manager.finish_span()

    manager.finish_trace()


def test_flush_without_exporters():

    manager = TraceManager()

    manager.flush()


def test_shutdown_without_exporters():

    manager = TraceManager()

    manager.shutdown()