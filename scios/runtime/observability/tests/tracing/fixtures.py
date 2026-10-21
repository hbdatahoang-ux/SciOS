"""
scios.runtime.observability.tests.tracing.fixtures

Shared pytest fixtures for tracing unit tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from .builders import PluginBuilder, SpanBuilder, TraceBuilder
from .fakes import (
    FakeClock,
    FakeExporter,
    FakeProcessor,
    FakeSpan,
    FakeTrace,
    FakeTraceManager,
)



# ============================================================================
# Core Fakes
# ============================================================================


@pytest.fixture
def fake_clock() -> FakeClock:
    """Deterministic clock for repeatable tests."""
    return FakeClock()


@pytest.fixture
def fake_manager() -> FakeTraceManager:
    """Fresh fake trace manager."""
    return FakeTraceManager()


@pytest.fixture
def fake_processor() -> FakeProcessor:
    """Fresh fake processor."""
    return FakeProcessor()


@pytest.fixture
def fake_exporter() -> FakeExporter:
    """Fresh fake exporter."""
    return FakeExporter()


@pytest.fixture
def fake_exporter_two() -> FakeExporter:
    """Fresh second fake exporter for multi-exporter tests."""
    return FakeExporter()


@pytest.fixture
def disabled_plugin(fake_manager) -> TracePlugin:
    """
    Return a disabled TracePlugin for lifecycle tests.

    The enabled flag is assigned after construction so this fixture
    does not depend on PluginBuilder.build() exposing an ``enabled``
    keyword argument.
    """
    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .build()
    )

    plugin._enabled = False

    return plugin


# ============================================================================
# Fixture Aliases
# ============================================================================


@pytest.fixture
def processor(
    fake_processor: FakeProcessor,
) -> FakeProcessor:
    """Processor fixture used by manager tests."""
    return fake_processor


@pytest.fixture
def exporter(
    fake_exporter: FakeExporter,
) -> FakeExporter:
    """Exporter fixture used by manager tests."""
    return fake_exporter


# ============================================================================
# Core Domain Objects
# ============================================================================


@pytest.fixture
def trace() -> FakeTrace:
    """Default trace object."""
    return (
        TraceBuilder()
        .with_name("Runtime")
        .build()
    )


@pytest.fixture
def span(
    trace: FakeTrace,
) -> FakeSpan:
    """Default root span."""
    return (
        SpanBuilder()
        .with_name("RootSpan")
        .with_trace(trace)
        .build()
    )


# ============================================================================
# Metadata
# ============================================================================


@pytest.fixture
def runtime_metadata() -> dict[str, Any]:
    """Standard runtime metadata."""
    return {
        "runtime": "SciOS",
        "kernel": "SciKernel",
        "execution_mode": "local",
        "kernel_version": "0.1.0",
    }


@pytest.fixture
def provenance_metadata() -> dict[str, Any]:
    """Scientific provenance metadata."""
    return {
        "experiment_id": "exp-001",
        "workflow_id": "wf-001",
        "pipeline_id": "pipe-001",
        "dataset_id": "dataset-001",
        "model_id": "model-001",
    }


@pytest.fixture
def merged_metadata(
    runtime_metadata: dict[str, Any],
    provenance_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Merged metadata with provenance values taking precedence."""
    return {
        **runtime_metadata,
        **provenance_metadata,
    }


# ============================================================================
# Plugin
# ============================================================================


@pytest.fixture
def plugin(
    fake_manager: FakeTraceManager,
    fake_processor: FakeProcessor,
    fake_exporter: FakeExporter,
):
    """
    Default tracing plugin configured with
    one manager, one processor and one exporter.
    """
    return (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )


# ============================================================================
# Runtime Session
# ============================================================================


@pytest.fixture
def runtime_trace(
    fake_manager: FakeTraceManager,
) -> FakeTrace:
    """Active runtime trace."""
    return fake_manager.start_trace("Runtime")


@pytest.fixture
def runtime_span(
    fake_manager: FakeTraceManager,
    runtime_trace: FakeTrace,
) -> FakeSpan:
    """Active runtime span."""
    return fake_manager.start_span(
        runtime_trace,
        "Runtime",
    )


# ============================================================================
# Exception Fixtures
# ============================================================================


@pytest.fixture
def runtime_exception() -> RuntimeError:
    """Generic runtime exception."""
    return RuntimeError("runtime failure")


@pytest.fixture
def value_exception() -> ValueError:
    """Generic value error."""
    return ValueError("invalid value")


# ============================================================================
# Helper Fixtures
# ============================================================================


@pytest.fixture
def populated_trace(
    trace: FakeTrace,
) -> FakeTrace:
    """Trace populated with sample data."""
    trace.set_attribute("user", "tester")
    trace.set_attribute("session", "abc123")

    trace.set_metadata("environment", "test")
    trace.set_metadata("version", "0.1")

    trace.add_event("started")
    trace.add_event("processing")

    return trace


@pytest.fixture
def populated_span(
    span: FakeSpan,
) -> FakeSpan:
    """Span populated with sample data."""
    span.set_attribute("stage", "planner")
    span.add_event("entered")

    return span
