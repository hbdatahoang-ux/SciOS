"""
Integration tests for TraceManager trace lifecycle.
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.manager import TraceManager
from scios.runtime.observability.tracing.trace import Trace


# ============================================================
# Helpers
# ============================================================


class DummySampler:
    def __init__(self, allow: bool = True):
        self.allow = allow

    def should_sample(self, **kwargs):
        return self.allow


class DummyProcessor:

    def __init__(self):
        self.started = []
        self.finished = []

    def on_trace_start(self, trace):
        self.started.append(trace)

    def on_trace_end(self, trace):
        self.finished.append(trace)


class DummyExporter:

    def __init__(self):
        self.exported = []
        self.flushed = False
        self.shutdown_called = False

    def export_trace(self, trace):
        self.exported.append(trace)

    def flush(self):
        self.flushed = True

    def shutdown(self):
        self.shutdown_called = True


# ============================================================
# Construction
# ============================================================


def test_manager_initial_state():

    mgr = TraceManager()

    assert mgr.current_trace is None
    assert mgr.trace_count == 0
    assert mgr.active_trace_count == 0
    assert mgr.completed_trace_count == 0


# ============================================================
# Trace lifecycle
# ============================================================


def test_start_trace_returns_trace():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    assert isinstance(trace, Trace)
    assert trace.name == "runtime"
    assert mgr.current_trace is trace


def test_start_trace_registers_active_trace():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    assert trace.trace_id in mgr.active_traces
    assert mgr.active_trace_count == 1


def test_finish_trace_moves_registry():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    mgr.finish_trace()

    assert trace.trace_id not in mgr.active_traces
    assert trace.trace_id in mgr.completed_traces


def test_finish_trace_returns_trace():

    mgr = TraceManager()

    mgr.start_trace("runtime")

    trace = mgr.finish_trace()

    assert isinstance(trace, Trace)


def test_finish_without_trace_returns_none():

    mgr = TraceManager()

    assert mgr.finish_trace() is None


def test_finish_trace_clears_current_trace():

    mgr = TraceManager()

    mgr.start_trace("runtime")

    mgr.finish_trace()

    assert mgr.current_trace is None


def test_trace_attributes_are_applied():

    mgr = TraceManager()

    trace = mgr.start_trace(
        "runtime",
        worker="cpu0",
        node="edge-1",
    )

    assert trace.attributes["worker"] == "cpu0"
    assert trace.attributes["node"] == "edge-1"


# ============================================================
# Trace registry
# ============================================================


def test_get_trace_returns_active_trace():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    assert mgr.get_trace(trace.trace_id) is trace


def test_get_trace_returns_completed_trace():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    mgr.finish_trace()

    assert mgr.get_trace(trace.trace_id) is trace


def test_has_trace_true():

    mgr = TraceManager()

    trace = mgr.start_trace("runtime")

    assert mgr.has_trace(trace.trace_id)


def test_has_trace_false():

    mgr = TraceManager()

    assert not mgr.has_trace("missing")


def test_trace_count_updates():

    mgr = TraceManager()

    mgr.start_trace("runtime")

    assert mgr.trace_count == 1

    mgr.finish_trace()

    assert mgr.trace_count == 1


# ============================================================
# Sampler
# ============================================================


def test_sampler_accepts_trace():

    sampler = DummySampler(True)

    mgr = TraceManager(sampler=sampler)

    trace = mgr.start_trace("runtime")

    assert trace is not None


def test_sampler_rejects_trace():

    sampler = DummySampler(False)

    mgr = TraceManager(sampler=sampler)

    with pytest.raises(RuntimeError):

        mgr.start_trace("runtime")


# ============================================================
# Processors
# ============================================================


def test_processor_receives_trace_callbacks():

    proc = DummyProcessor()

    mgr = TraceManager(
        processors=[proc],
    )

    trace = mgr.start_trace("runtime")

    mgr.finish_trace()

    assert proc.started == [trace]
    assert proc.finished == [trace]


# ============================================================
# Exporters
# ============================================================


def test_exporter_receives_finished_trace():

    exporter = DummyExporter()

    mgr = TraceManager(
        exporters=[exporter],
    )

    trace = mgr.start_trace("runtime")

    mgr.finish_trace()

    assert exporter.exported == [trace]


def test_flush_calls_exporters():

    exporter = DummyExporter()

    mgr = TraceManager(
        exporters=[exporter],
    )

    mgr.flush()

    assert exporter.flushed


def test_shutdown_calls_exporter_shutdown():

    exporter = DummyExporter()

    mgr = TraceManager(
        exporters=[exporter],
    )

    mgr.shutdown()

    assert exporter.shutdown_called


# ============================================================
# Reset
# ============================================================


def test_reset_clears_registries():

    mgr = TraceManager()

    mgr.start_trace("runtime")

    mgr.finish_trace()

    mgr.reset()

    assert mgr.trace_count == 0
    assert mgr.active_trace_count == 0
    assert mgr.completed_trace_count == 0
    assert mgr.current_trace is None


# ============================================================
# Representation
# ============================================================


def test_repr_contains_statistics():

    mgr = TraceManager()

    text = repr(mgr)

    assert "TraceManager" in text
    assert "active=" in text
    assert "completed=" in text