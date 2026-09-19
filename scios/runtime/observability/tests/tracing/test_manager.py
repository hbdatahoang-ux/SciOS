"""
SciOS Runtime Observability
TraceManager tests
===================

Tests for the public TraceManager contract.
"""
from __future__ import annotations


# ==============================================================================
# Part 1. Imports
# ==============================================================================

from typing import Any

import pytest

from scios.runtime.observability.tracing.event import Event

from scios.runtime.observability.tracing.manager import TraceManager


# ==============================================================================
# Part 2. Fixtures & Fakes
# ==============================================================================


class FakeProcessor:
    """Minimal processor fake for TraceManager tests."""

    def __init__(self) -> None:
        self.started = []
        self.finished = []
        self.processed = []

    def trace_started(self, trace: Any) -> None:
        self.started.append(trace)

    def trace_finished(self, trace: Any) -> None:
        self.finished.append(trace)

    def process(self, value: Any) -> Any:
        self.processed.append(value)
        return value


class FakeExporter:
    """Minimal exporter fake for TraceManager tests."""

    def __init__(self) -> None:
        self.exported = []
        self.flushed = 0
        self.shutdowns = 0

    def export(self, value: Any) -> Any:
        self.exported.append(value)
        return value

    def flush(self) -> None:
        self.flushed += 1

    def shutdown(self) -> None:
        self.shutdowns += 1


class FakeSampler:
    """Minimal sampler fake for TraceManager tests."""

    def __init__(self, decision: bool = True) -> None:
        self.decision = decision
        self.calls = []

    def should_sample(self, value: Any = None) -> bool:
        self.calls.append(value)
        return self.decision


def create_manager(
    *,
    name: str = "test",
    service_name: str = "scios",
    enabled: bool = True,
    sampler: Any = None,
    processor: Any = None,
    exporters: Any = None,
) -> TraceManager:
    """Create a minimal TraceManager for tests."""

    return TraceManager(
        name=name,
        service_name=service_name,
        enabled=enabled,
        sampler=sampler,
        processor=processor,
        exporters=exporters,
    )


def create_populated_manager() -> TraceManager:
    """
    Create a manager with all optional components configured.
    """

    sampler = FakeSampler()
    processor = FakeProcessor()
    exporter = FakeExporter()

    return create_manager(
        sampler=sampler,
        processor=processor,
        exporters=[exporter],
    )


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


# ------------------------------------------------------------------------------
# 3.1 Default construction
# ------------------------------------------------------------------------------


def test_default_construction() -> None:
    manager = TraceManager()

    assert isinstance(manager, TraceManager)
    assert manager.name == "tracer"
    assert manager.service_name == "scios"
    assert manager.enabled is True
    assert manager.active is False
    assert manager.current_trace is None
    assert manager.current_span is None


# ------------------------------------------------------------------------------
# 3.2 Custom name
# ------------------------------------------------------------------------------


def test_custom_name() -> None:
    manager = TraceManager(
        name="custom-tracer",
    )

    assert manager.name == "custom-tracer"


def test_name_must_be_string() -> None:
    with pytest.raises(TypeError):
        TraceManager(
            name=123,  # type: ignore[arg-type]
        )


def test_name_cannot_be_empty() -> None:
    with pytest.raises(ValueError):
        TraceManager(
            name="",
        )


def test_name_is_stripped() -> None:
    manager = TraceManager(
        name="  tracer  ",
    )

    assert manager.name == "tracer"


# ------------------------------------------------------------------------------
# 3.3 service_name
# ------------------------------------------------------------------------------


def test_service_name() -> None:
    manager = TraceManager(
        service_name="my-service",
    )

    assert manager.service_name == "my-service"


def test_service_name_must_be_string() -> None:
    with pytest.raises(TypeError):
        TraceManager(
            service_name=123,  # type: ignore[arg-type]
        )


def test_service_name_cannot_be_empty() -> None:
    with pytest.raises(ValueError):
        TraceManager(
            service_name="",
        )


def test_service_name_is_stripped() -> None:
    manager = TraceManager(
        service_name="  my-service  ",
    )

    assert manager.service_name == "my-service"


# ------------------------------------------------------------------------------
# 3.4 enabled
# ------------------------------------------------------------------------------


def test_enabled_defaults_to_true() -> None:
    manager = TraceManager()

    assert manager.enabled is True


def test_enabled_can_be_disabled() -> None:
    manager = TraceManager(
        enabled=False,
    )

    assert manager.enabled is False
    assert manager.active is False


def test_enabled_must_be_bool() -> None:
    with pytest.raises(TypeError):
        TraceManager(
            enabled=1,  # type: ignore[arg-type]
        )


# ------------------------------------------------------------------------------
# 3.5 sampler
# ------------------------------------------------------------------------------


def test_sampler_is_stored() -> None:
    sampler = FakeSampler()

    manager = create_manager(
        sampler=sampler,
    )

    assert manager._sampler is sampler


# ------------------------------------------------------------------------------
# 3.6 processor
# ------------------------------------------------------------------------------


def test_processor_is_stored() -> None:
    processor = FakeProcessor()

    manager = create_manager(
        processor=processor,
    )

    assert manager._processor is processor


def test_set_processor() -> None:
    manager = create_manager()

    processor = FakeProcessor()

    result = manager.set_processor(
        processor,
    )

    assert result is manager
    assert manager._processor is processor


def test_set_processor_can_clear_processor() -> None:
    processor = FakeProcessor()

    manager = create_manager(
        processor=processor,
    )

    result = manager.set_processor(
        None,
    )

    assert result is manager
    assert manager._processor is None


# ------------------------------------------------------------------------------
# 3.7 exporters
# ------------------------------------------------------------------------------


def test_exporters_default_to_empty_list() -> None:
    manager = TraceManager()

    assert manager._exporters == []


def test_exporters_are_stored_as_list() -> None:
    exporter = FakeExporter()

    manager = create_manager(
        exporters=[exporter],
    )

    assert isinstance(
        manager._exporters,
        list,
    )

    assert manager._exporters == [exporter]


def test_exporters_iterable_is_materialized() -> None:
    exporter = FakeExporter()

    manager = create_manager(
        exporters=(item for item in [exporter]),
    )

    assert manager._exporters == [exporter]


# ------------------------------------------------------------------------------
# 3.8 Populated construction
# ------------------------------------------------------------------------------


def test_populated_manager() -> None:
    manager = create_populated_manager()

    assert manager.enabled is True
    assert manager._sampler is not None
    assert manager._processor is not None
    assert len(manager._exporters) == 1


# ------------------------------------------------------------------------------
# 3.9 Initial state
# ------------------------------------------------------------------------------


def test_initial_trace_state() -> None:
    manager = TraceManager()

    assert manager.current_trace is None
    assert manager.trace is None
    assert manager.active is False


def test_initial_span_state() -> None:
    manager = TraceManager()

    assert manager.current_span is None
    assert manager.span_stack == []
    assert manager.span_depth == 0


def test_initial_context_state() -> None:
    manager = TraceManager()

    assert manager.current_context() is None


def test_initial_metadata_state() -> None:
    manager = TraceManager()

    assert manager.metadata == {}


def test_initial_statistics_state() -> None:
    manager = TraceManager()

    assert manager.trace_count() == 0
    assert manager.completed_trace_count() == 0
    assert manager.span_count() == 0
    assert manager.active_span_count() == 0
    assert manager.exported_count() == 0
    assert manager.error_count() == 0


# ==============================================================================
# Part 4. Core Properties
# ==============================================================================


def test_name_property() -> None:
    manager = TraceManager(name="runtime")

    assert manager.name == "runtime"


def test_service_name_property() -> None:
    manager = TraceManager(service_name="scios-runtime")

    assert manager.service_name == "scios-runtime"


def test_enabled_property() -> None:
    enabled = TraceManager(enabled=True)
    disabled = TraceManager(enabled=False)

    assert enabled.enabled is True
    assert disabled.enabled is False


def test_active_initially_false() -> None:
    manager = TraceManager()

    assert manager.active is False


def test_trace_alias_matches_current_trace() -> None:
    manager = TraceManager()

    assert manager.trace is manager.current_trace
    assert manager.trace is None


def test_current_trace_after_start() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    assert trace is not None
    assert manager.current_trace is trace
    assert manager.trace is trace


def test_current_span_initially_none() -> None:
    manager = TraceManager()

    assert manager.current_span is None


def test_span_stack_initially_empty() -> None:
    manager = TraceManager()

    assert manager.span_stack == []


def test_span_stack_returns_copy() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    stack = manager.span_stack
    stack.clear()

    assert manager.span_depth == 1


def test_span_depth_initially_zero() -> None:
    manager = TraceManager()

    assert manager.span_depth == 0


def test_span_depth_after_start() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    assert manager.span_depth == 1


# ==============================================================================
# Part 5. Trace Lifecycle
# ==============================================================================


def test_start_trace_creates_trace() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    assert trace is not None
    assert manager.active is True
    assert manager.current_trace is trace


def test_start_trace_uses_given_name() -> None:
    manager = TraceManager()

    trace = manager.start_trace("experiment")

    assert trace is not None
    assert getattr(trace, "name", None) == "experiment"


def test_start_trace_default_name() -> None:
    manager = TraceManager(name="default-tracer")

    trace = manager.start_trace()

    assert trace is not None
    assert getattr(trace, "name", None) == "default-tracer"


def test_start_trace_increments_trace_counter() -> None:
    manager = TraceManager()

    assert manager.trace_count() == 0

    manager.start_trace("one")

    assert manager.trace_count() == 1


def test_start_trace_resets_span_state() -> None:
    manager = TraceManager()

    manager.start_trace("one")
    manager.start_span("root")

    assert manager.span_depth == 1

    manager.start_trace("two")

    assert manager.span_depth == 0
    assert manager.current_span is None


def test_start_trace_restarts_active_trace() -> None:
    manager = TraceManager()

    first = manager.start_trace("first")
    second = manager.start_trace("second")

    assert first is not None
    assert second is not None
    assert second is not first
    assert manager.current_trace is second
    assert manager.active is True


def test_finish_trace_returns_trace() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    finished = manager.finish_trace()

    assert finished is trace


def test_finish_trace_clears_current_trace() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.finish_trace()

    assert manager.current_trace is None
    assert manager.trace is None
    assert manager.active is False


def test_finish_trace_clears_span_state() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")
    manager.start_span("child")

    manager.finish_trace()

    assert manager.current_span is None
    assert manager.span_depth == 0
    assert manager.active_span_count() == 0


def test_finish_trace_increments_completed_counter() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.finish_trace()

    assert manager.completed_trace_count() == 1


def test_finish_trace_without_active_trace_is_safe() -> None:
    manager = TraceManager()

    assert manager.finish_trace() is None

    assert manager.active is False
    assert manager.current_trace is None


def test_cancel_trace_returns_trace() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    cancelled = manager.cancel_trace()

    assert cancelled is trace


def test_cancel_trace_clears_state() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    manager.cancel_trace()

    assert manager.current_trace is None
    assert manager.current_span is None
    assert manager.span_depth == 0
    assert manager.active is False


def test_cancel_trace_without_active_trace_is_safe() -> None:
    manager = TraceManager()

    assert manager.cancel_trace() is None


def test_multiple_trace_cycles() -> None:
    manager = TraceManager()

    for index in range(5):
        manager.start_trace(f"trace-{index}")
        manager.finish_trace()

    assert manager.trace_count() == 5
    assert manager.completed_trace_count() == 5


# ==============================================================================
# Part 6. Span Lifecycle
# ==============================================================================

def test_start_span_requires_active_trace() -> None:
    manager = TraceManager()

    with pytest.raises(
        RuntimeError,
        match="cannot start span without an active trace",
    ):
        manager.start_span("orphan")


def test_start_span_creates_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None
    assert manager.current_span is span


def test_start_span_increments_span_count() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    assert manager.span_count() == 1
    assert manager.active_span_count() == 1


def test_finish_span_returns_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    finished = manager.finish_span()

    assert finished is span


def test_finish_span_clears_current_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")
    manager.finish_span()

    assert manager.current_span is None
    assert manager.span_depth == 0
    assert manager.active_span_count() == 0


def test_cancel_span_clears_current_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    manager.cancel_span()

    assert manager.current_span is None
    assert manager.span_depth == 0


def test_cancel_span_without_span_is_safe() -> None:
    manager = TraceManager()

    assert manager.cancel_span() is manager


def test_nested_spans() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    root = manager.start_span("root")
    child = manager.start_span("child")

    assert root is not None
    assert child is not None
    assert manager.current_span is child
    assert manager.span_depth == 2


def test_nested_span_parent_child_relationship() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    root = manager.start_span("root")
    child = manager.start_span("child")

    assert root is not None
    assert child is not None

    root_id = getattr(root, "span_id", None)

    child_parent_id = getattr(
        child,
        "parent_span_id",
        None,
    )

    if root_id is not None:
        assert child_parent_id == root_id


def test_finish_child_restores_parent() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    root = manager.start_span("root")
    child = manager.start_span("child")

    assert root is not None
    assert child is not None

    manager.finish_span()

    assert manager.current_span is root
    assert manager.span_depth == 1


def test_finish_root_clears_stack() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    manager.finish_span()

    assert manager.current_span is None
    assert manager.span_depth == 0


def test_push_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    span = manager.start_span("root")

    assert span is not None

    manager.pop_span()

    manager.push_span(span)

    assert manager.current_span is span
    assert manager.span_depth == 1


def test_pop_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    popped = manager.pop_span()

    assert popped is span
    assert manager.current_span is None
    assert manager.span_depth == 0


def test_pop_empty_stack_is_safe() -> None:
    manager = TraceManager()

    assert manager.pop_span() is None


# ==============================================================================
# Part 7. Context Management
# ==============================================================================


def test_context_initially_none() -> None:
    manager = TraceManager()

    assert manager.context() is None
    assert manager.current_context() is None


def test_current_context_after_start_trace() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    context = manager.current_context()

    assert context is not None


def test_set_context() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    context = manager.current_context()

    assert context is not None

    result = manager.set_context(context)

    assert result is manager
    assert manager.current_context() is context


def test_set_context_none_clears_context() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    manager.set_context(None)

    assert manager.current_context() is None


def test_update_context() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    result = manager.update_context(
        component="runtime",
    )

    assert result is manager


def test_clear_context() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.update_context(
        component="runtime",
    )

    result = manager.clear_context()

    assert result is manager


# ==============================================================================
# Part 8. Metadata & Events
# ==============================================================================


def test_set_metadata() -> None:
    manager = TraceManager()

    result = manager.set_metadata(
        "dataset",
        "demo",
    )

    assert result is manager
    assert manager.get_metadata("dataset") == "demo"


def test_update_metadata() -> None:
    manager = TraceManager()

    result = manager.update_metadata(
        {
            "project": "SciOS",
            "version": "1",
        },
    )

    assert result is manager
    assert manager.get_metadata("project") == "SciOS"
    assert manager.get_metadata("version") == "1"


def test_update_metadata_kwargs() -> None:
    manager = TraceManager()

    manager.update_metadata(
        project="SciOS",
        dataset="demo",
    )

    assert manager.get_metadata("project") == "SciOS"
    assert manager.get_metadata("dataset") == "demo"


def test_metadata_returns_copy() -> None:
    manager = TraceManager()

    manager.set_metadata(
        "project",
        "SciOS",
    )

    metadata = manager.metadata
    metadata["project"] = "modified"

    assert manager.get_metadata("project") == "SciOS"


def test_set_attribute_without_span() -> None:
    manager = TraceManager()

    result = manager.set_attribute(
        "component",
        "runtime",
    )

    assert result is manager


def test_set_attribute_on_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    result = manager.set_attribute(
        "component",
        "runtime",
    )

    assert result is manager


def test_add_event_without_active_span_raises() -> None:
    manager = TraceManager()

    with pytest.raises(RuntimeError):
        manager.add_event(
            "test",
        )


def test_add_event_on_active_span() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    result = manager.add_event(
        "test",
    )

    assert result.name == "test"
    assert manager.current_span.events[-1] is result


# ==============================================================================
# Part 9. Processing & Sampling
# ==============================================================================


def test_process_span_without_processor() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    result = manager.process_span(span)

    assert result is span


def test_process_trace_without_processor() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    assert trace is not None

    result = manager.process_trace(trace)

    assert result is trace


def test_process_without_processor() -> None:
    manager = TraceManager()

    value = object()

    result = manager.process(value)

    assert result is value


def test_process_span_with_processor(
    processor: FakeProcessor,
) -> None:
    manager = TraceManager(
        processor=processor,
    )

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    result = manager.process_span(span)

    assert result is span
    assert processor.processed


def test_should_sample_without_sampler() -> None:
    manager = TraceManager()

    result = manager.should_sample()

    assert isinstance(result, bool)


def test_should_sample_with_sampler() -> None:
    sampler = FakeSampler(
        decision=True,
    )

    manager = TraceManager(
        sampler=sampler,
    )

    result = manager.should_sample()

    assert result is True
    assert len(sampler.calls) == 1


def test_sampling_decision() -> None:
    manager = TraceManager()

    result = manager.sampling_decision()

    assert isinstance(result, bool)


# ==============================================================================
# Part 10. Exporting
# ==============================================================================


def test_export_span_without_exporters() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    result = manager.export_span(span)

    assert result == []


def test_export_trace_without_exporters() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    assert trace is not None

    result = manager.export_trace(trace)

    assert result == []


def test_export_without_exporters() -> None:
    manager = TraceManager()

    assert manager.export() is None


def test_export_span_with_exporter(
    exporter: FakeExporter,
) -> None:
    manager = TraceManager(
        exporters=[exporter],
    )

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None

    manager.export_span(span)

    assert exporter.exported


def test_export_trace_with_exporter(
    exporter: FakeExporter,
) -> None:
    manager = TraceManager(
        exporters=[exporter],
    )

    trace = manager.start_trace("test")

    assert trace is not None

    manager.export_trace(trace)

    assert exporter.exported


def test_flush_calls_exporter(
    exporter: FakeExporter,
) -> None:
    manager = TraceManager(
        exporters=[exporter],
    )

    result = manager.flush()

    assert result is manager
    assert exporter.flushed == 1


# ==============================================================================
# Part 11. State Management
# ==============================================================================


def test_snapshot_empty_manager() -> None:
    manager = TraceManager()

    snapshot = manager.snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot["active"] is False
    assert snapshot["trace"] is None


def test_snapshot_active_manager() -> None:
    manager = create_populated_manager()

    manager.start_trace("test")
    manager.start_span("root")

    snapshot = manager.snapshot()

    assert snapshot["active"] is True
    assert snapshot["trace"] is not None
    assert snapshot["current_span"] is not None


def test_restore_snapshot() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    snapshot = manager.snapshot()

    manager.finish_trace()

    assert manager.active is False

    result = manager.restore(snapshot)

    assert result is manager
    assert manager.active is True
    assert manager.current_trace is not None
    assert manager.current_span is not None


def test_restore_does_not_use_same_metadata_object() -> None:
    manager = TraceManager()

    manager.set_metadata(
        "project",
        "SciOS",
    )

    snapshot = manager.snapshot()

    manager.set_metadata(
        "project",
        "changed",
    )

    manager.restore(snapshot)

    assert manager.get_metadata("project") == "SciOS"


def test_copy_returns_manager() -> None:
    manager = create_manager()

    copied = manager.copy()

    assert isinstance(copied, TraceManager)
    assert copied is not manager


def test_copy_preserves_configuration() -> None:
    manager = TraceManager(
        name="test",
        service_name="service",
        enabled=True,
    )

    copied = manager.copy()

    assert copied.name == manager.name
    assert copied.service_name == manager.service_name
    assert copied.enabled == manager.enabled


def test_clone_returns_independent_manager() -> None:
    manager = create_manager()

    cloned = manager.clone()

    assert isinstance(cloned, TraceManager)
    assert cloned is not manager


# ==============================================================================
# Part 12. Validation & Diagnostics
# ==============================================================================


def test_validate_empty_manager() -> None:
    manager = TraceManager()

    assert manager.validate() is True


def test_validate_active_manager() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    assert manager.validate() is True


def test_validate_span_stack_empty() -> None:
    manager = TraceManager()

    assert manager.validate_span_stack() is True


def test_validate_span_stack_active() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    assert manager.validate_span_stack() is True


def test_validate_state_empty_manager() -> None:
    manager = TraceManager()

    assert manager.validate_state() is True


def test_validate_trace_active() -> None:
    manager = TraceManager()

    trace = manager.start_trace("test")

    assert trace is not None
    assert manager.validate_trace(trace) is True


def test_validate_span_active() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    span = manager.start_span("root")

    assert span is not None
    assert manager.validate_span(span) is True


def test_health_returns_mapping() -> None:
    manager = TraceManager()

    health = manager.health()

    assert isinstance(health, dict)
    assert "healthy" in health
    assert "enabled" in health
    assert "active" in health


def test_health_empty_manager() -> None:
    manager = TraceManager()

    health = manager.health()

    assert health["healthy"] is True
    assert health["active"] is False


def test_diagnostics_returns_mapping() -> None:
    manager = TraceManager()

    diagnostics = manager.diagnostics()

    assert isinstance(diagnostics, dict)
    assert "name" in diagnostics
    assert "service_name" in diagnostics
    assert "statistics" in diagnostics


def test_summary_returns_mapping() -> None:
    manager = TraceManager()

    summary = manager.summary()

    assert isinstance(summary, dict)
    assert summary["name"] == manager.name
    assert summary["service_name"] == manager.service_name
    assert summary["trace_count"] == 0


# ==============================================================================
# Part 13. Representation & Edge Cases
# ==============================================================================


def test_repr() -> None:
    manager = TraceManager(
        name="test",
        service_name="service",
    )

    value = repr(manager)

    assert "TraceManager" in value
    assert "test" in value
    assert "service" in value


def test_str() -> None:
    manager = TraceManager(
        name="test",
    )

    value = str(manager)

    assert "TraceManager" in value
    assert "test" in value


def test_disabled_manager_start_trace() -> None:
    manager = TraceManager(
        enabled=False,
    )

    trace = manager.start_trace("test")

    assert trace is None
    assert manager.active is False
    assert manager.current_trace is None


def test_disabled_manager_start_span() -> None:
    manager = TraceManager(
        enabled=False,
    )

    span = manager.start_span("test")

    assert span is None
    assert manager.current_span is None


def test_empty_manager_finish_trace() -> None:
    manager = TraceManager()

    assert manager.finish_trace() is None


def test_empty_manager_cancel_trace() -> None:
    manager = TraceManager()

    assert manager.cancel_trace() is None


def test_repeated_finish_trace_is_safe() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    manager.finish_trace()
    manager.finish_trace()
    manager.finish_trace()

    assert manager.active is False
    assert manager.current_trace is None


def test_repeated_cancel_trace_is_safe() -> None:
    manager = TraceManager()

    manager.start_trace("test")

    manager.cancel_trace()
    manager.cancel_trace()
    manager.cancel_trace()

    assert manager.active is False
    assert manager.current_trace is None


def test_repeated_finish_span_is_safe() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    manager.finish_span()
    manager.finish_span()
    manager.finish_span()

    assert manager.current_span is None
    assert manager.span_depth == 0


def test_cleanup_after_trace_failure() -> None:
    manager = TraceManager()

    manager.start_trace("test")
    manager.start_span("root")

    manager.finish_trace()

    assert manager.active is False
    assert manager.current_trace is None
    assert manager.current_span is None
    assert manager.span_depth == 0


def test_manager_can_be_reused_after_finish() -> None:
    manager = TraceManager()

    first = manager.start_trace("first")
    manager.start_span("root")
    manager.finish_trace()

    second = manager.start_trace("second")

    assert first is not None
    assert second is not None
    assert second is not first
    assert manager.active is True


def test_manager_can_be_reused_after_cancel() -> None:
    manager = TraceManager()

    first = manager.start_trace("first")
    manager.start_span("root")
    manager.cancel_trace()

    second = manager.start_trace("second")

    assert first is not None
    assert second is not None
    assert second is not first
    assert manager.active is True
