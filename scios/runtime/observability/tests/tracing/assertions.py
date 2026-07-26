"""
scios.runtime.observability.tests.tracing.assertions

Reusable assertion helpers for tracing tests.
"""

from __future__ import annotations

from typing import Iterable

from .fakes import (
    FakeExporter,
    FakeProcessor,
    FakeSpan,
    FakeTrace,
    FakeTraceManager,
)


# ============================================================================
# Trace Assertions
# ============================================================================


def assert_trace_started(trace: FakeTrace) -> None:
    assert trace.started_at is not None, "Trace was not started."


def assert_trace_finished(trace: FakeTrace) -> None:
    assert trace.finished, "Trace was not finished."


def assert_trace_status(
    trace: FakeTrace,
    expected: str,
) -> None:
    assert (
        trace.status == expected
    ), f"Expected trace status {expected!r}, got {trace.status!r}"


def assert_trace_duration(trace: FakeTrace) -> None:
    assert trace.duration is not None
    assert trace.duration >= 0


def assert_trace_attribute(
    trace: FakeTrace,
    key: str,
    value,
) -> None:
    assert trace.get_attribute(key) == value


def assert_trace_metadata(
    trace: FakeTrace,
    key: str,
    value,
) -> None:
    assert trace.get_metadata(key) == value


def assert_trace_event_count(
    trace: FakeTrace,
    expected: int,
) -> None:
    assert trace.event_count == expected


def assert_trace_exception_count(
    trace: FakeTrace,
    expected: int,
) -> None:
    assert trace.exception_count == expected


# ============================================================================
# Span Assertions
# ============================================================================


def assert_span_started(span: FakeSpan) -> None:
    assert span.started_at is not None


def assert_span_finished(span: FakeSpan) -> None:
    assert span.finished


def assert_span_status(
    span: FakeSpan,
    expected: str,
) -> None:
    assert span.status == expected


def assert_span_attribute(
    span: FakeSpan,
    key: str,
    value,
) -> None:
    assert span.get_attribute(key) == value


def assert_span_event_count(
    span: FakeSpan,
    expected: int,
) -> None:
    assert span.event_count == expected


def assert_span_exception_count(
    span: FakeSpan,
    expected: int,
) -> None:
    assert span.exception_count == expected


def assert_span_child_count(
    span: FakeSpan,
    expected: int,
) -> None:
    assert span.child_count == expected


def assert_span_tree(root: FakeSpan) -> None:
    """
    Recursively verifies that every child's parent
    points back to the current node.
    """
    for child in root.children:
        assert child.parent is root
        assert_span_tree(child)


# ============================================================================
# Manager Assertions
# ============================================================================


def assert_trace_count(
    manager: FakeTraceManager,
    expected: int,
) -> None:
    assert manager.trace_count == expected


def assert_span_count(
    manager: FakeTraceManager,
    expected: int,
) -> None:
    assert manager.span_count == expected


def assert_stack_depth(
    manager: FakeTraceManager,
    expected: int,
) -> None:
    assert manager.stack_depth == expected


def assert_active_trace(
    manager: FakeTraceManager,
) -> None:
    assert manager.current_trace is not None


def assert_no_active_trace(
    manager: FakeTraceManager,
) -> None:
    assert manager.current_trace is None


def assert_active_span(
    manager: FakeTraceManager,
) -> None:
    assert manager.current_span is not None


def assert_no_active_span(
    manager: FakeTraceManager,
) -> None:
    assert manager.current_span is None


# ============================================================================
# Processor Assertions
# ============================================================================


def assert_processor_called(
    processor: FakeProcessor,
    method: str,
) -> None:
    assert processor.was_called(method)


def assert_processor_not_called(
    processor: FakeProcessor,
    method: str,
) -> None:
    assert not processor.was_called(method)


def assert_processor_call_count(
    processor: FakeProcessor,
    expected: int,
) -> None:
    assert processor.call_count == expected


def assert_processor_call_order(
    processor: FakeProcessor,
    expected: Iterable[str],
) -> None:
    assert processor.call_order() == list(expected)


# ============================================================================
# Exporter Assertions
# ============================================================================


def assert_export_count(
    exporter: FakeExporter,
    expected: int,
) -> None:
    assert exporter.export_count == expected


def assert_export_order(
    exporter: FakeExporter,
    expected: Iterable[str],
) -> None:
    actual = [
        kind
        for kind, _ in exporter.exports
    ]
    assert actual == list(expected)


def assert_flushed(
    exporter: FakeExporter,
) -> None:
    assert exporter.flushed


def assert_shutdown(
    exporter: FakeExporter,
) -> None:
    assert exporter.shutdown_called


# ============================================================================
# Generic Assertions
# ============================================================================


def assert_success(obj) -> None:
    assert getattr(obj, "status", None) == "SUCCESS"


def assert_failure(obj) -> None:
    assert getattr(obj, "status", None) == "FAILED"


__all__ = [
    "assert_trace_started",
    "assert_trace_finished",
    "assert_trace_status",
    "assert_trace_duration",
    "assert_trace_attribute",
    "assert_trace_metadata",
    "assert_trace_event_count",
    "assert_trace_exception_count",
    "assert_span_started",
    "assert_span_finished",
    "assert_span_status",
    "assert_span_attribute",
    "assert_span_event_count",
    "assert_span_exception_count",
    "assert_span_child_count",
    "assert_span_tree",
    "assert_trace_count",
    "assert_span_count",
    "assert_stack_depth",
    "assert_active_trace",
    "assert_no_active_trace",
    "assert_active_span",
    "assert_no_active_span",
    "assert_processor_called",
    "assert_processor_not_called",
    "assert_processor_call_count",
    "assert_processor_call_order",
    "assert_export_count",
    "assert_export_order",
    "assert_flushed",
    "assert_shutdown",
    "assert_success",
    "assert_failure",
]