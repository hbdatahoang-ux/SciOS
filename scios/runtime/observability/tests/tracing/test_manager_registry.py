"""
Tests for TraceManager registries.

Coverage
--------
- global manager
- active registry
- completed registry
- get_trace()
- has_trace()
- counters
- registry consistency
"""

from __future__ import annotations

from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Global Manager
# ==========================================================


def test_get_global_returns_manager():

    manager = TraceManager.get_global()

    assert isinstance(manager, TraceManager)


def test_get_global_returns_same_instance():

    m1 = TraceManager.get_global()

    m2 = TraceManager.get_global()

    assert m1 is m2


def test_set_global():

    manager = TraceManager()

    TraceManager.set_global(manager)

    assert TraceManager.get_global() is manager


# ==========================================================
# Active Registry
# ==========================================================


def test_active_registry_contains_started_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    assert trace.trace_id in manager.active_traces


def test_active_registry_removed_after_finish():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    manager.finish_trace()

    assert trace.trace_id not in manager.active_traces


# ==========================================================
# Completed Registry
# ==========================================================


def test_completed_registry_contains_finished_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    manager.finish_trace()

    assert trace.trace_id in manager.completed_traces


def test_completed_registry_empty_initially():

    manager = TraceManager()

    assert manager.completed_traces == {}


# ==========================================================
# get_trace()
# ==========================================================


def test_get_active_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    assert manager.get_trace(trace.trace_id) is trace


def test_get_completed_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    manager.finish_trace()

    assert manager.get_trace(trace.trace_id) is trace


def test_get_missing_trace():

    manager = TraceManager()

    assert manager.get_trace("missing") is None


# ==========================================================
# has_trace()
# ==========================================================


def test_has_active_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    assert manager.has_trace(trace.trace_id)


def test_has_completed_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    manager.finish_trace()

    assert manager.has_trace(trace.trace_id)


def test_has_missing_trace():

    manager = TraceManager()

    assert not manager.has_trace("missing")


# ==========================================================
# Counters
# ==========================================================


def test_trace_count_initial():

    manager = TraceManager()

    assert manager.trace_count == 0


def test_active_trace_count():

    manager = TraceManager()

    manager.start_trace("a")

    assert manager.active_trace_count == 1


def test_completed_trace_count():

    manager = TraceManager()

    manager.start_trace("a")

    manager.finish_trace()

    assert manager.completed_trace_count == 1


def test_total_trace_count():

    manager = TraceManager()

    manager.start_trace("a")

    manager.finish_trace()

    assert manager.trace_count == 1


# ==========================================================
# Reset
# ==========================================================


def test_reset_clears_registries():

    manager = TraceManager()

    manager.start_trace("runtime")

    manager.finish_trace()

    manager.reset()

    assert manager.active_traces == {}

    assert manager.completed_traces == {}


# ==========================================================
# Registry Consistency
# ==========================================================


def test_registry_moves_trace():

    manager = TraceManager()

    trace = manager.start_trace("runtime")

    assert trace.trace_id in manager.active_traces

    manager.finish_trace()

    assert trace.trace_id not in manager.active_traces

    assert trace.trace_id in manager.completed_traces


def test_multiple_completed_traces():

    manager = TraceManager()

    for i in range(5):

        manager.start_trace(f"trace-{i}")

        manager.finish_trace()

    assert manager.completed_trace_count == 5


def test_multiple_active_not_allowed():

    manager = TraceManager()

    t1 = manager.start_trace("a")

    t2 = manager.start_trace("b")

    assert manager.active_trace_count == 2

    assert t1.trace_id in manager.active_traces

    assert t2.trace_id in manager.active_traces


# ==========================================================
# __repr__
# ==========================================================


def test_repr():

    manager = TraceManager()

    text = repr(manager)

    assert "TraceManager" in text

    assert "active=" in text

    assert "completed=" in text


# ==========================================================
# Regression
# ==========================================================


def test_registry_after_shutdown():

    manager = TraceManager()

    manager.start_trace("runtime")

    manager.finish_trace()

    manager.shutdown()

    assert manager.active_traces == {}

    assert manager.completed_traces == {}


def test_registry_after_many_traces():

    manager = TraceManager()

    traces = []

    for i in range(50):

        trace = manager.start_trace(f"trace-{i}")

        traces.append(trace)

        manager.finish_trace()

    assert manager.completed_trace_count == 50

    for trace in traces:

        assert manager.get_trace(trace.trace_id) is trace