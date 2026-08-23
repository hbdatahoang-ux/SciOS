from __future__ import annotations

from typing import Any

import pytest

from scios.runtime.observability.tracing.provider import (
    TraceProvider,
    ProviderType,
    ProviderState,
    ProviderCapability,
    ProviderStatistics,
    ProviderReport,
)

from scios.runtime.observability.tracing.manager import TraceManager
from scios.runtime.observability.tracing.sampler import TraceSampler
from scios.runtime.observability.tracing.processor import TraceProcessor
from scios.runtime.observability.tracing.exporter import Exporter


# ==============================================================================
# Part 1. Fixtures
# ==============================================================================

@pytest.fixture
def create_manager():
    def factory(**kwargs: Any) -> TraceManager:
        return TraceManager(
            name=kwargs.pop("name", "test"),
            service_name=kwargs.pop(
                "service_name",
                "scios-test",
            ),
            **kwargs,
        )

    return factory


@pytest.fixture
def create_sampler():
    def factory(**kwargs: Any) -> TraceSampler:
        return TraceSampler(
            **kwargs,
        )

    return factory


@pytest.fixture
def create_processor():
    def factory(**kwargs: Any) -> TraceProcessor:
        return TraceProcessor(
            **kwargs,
        )

    return factory


@pytest.fixture
def create_exporter():
    def factory(**kwargs: Any) -> Exporter:
        return Exporter(
            **kwargs,
        )

    return factory


@pytest.fixture
def create_provider(
    create_manager,
    create_sampler,
    create_processor,
):
    def factory(**kwargs: Any) -> TraceProvider:
        kwargs.setdefault(
            "manager",
            create_manager(),
        )

        kwargs.setdefault(
            "sampler",
            create_sampler(),
        )

        kwargs.setdefault(
            "processor",
            create_processor(),
        )

        return TraceProvider(
            **kwargs,
        )

    return factory


@pytest.fixture
def provider(create_provider):
    return create_provider()


# ==============================================================================
# Part 2. Construction
# ==============================================================================

def test_default_construction(provider):
    assert isinstance(provider, TraceProvider)


def test_custom_name(create_provider):
    provider = create_provider(name="custom")

    assert provider.name == "custom"


def test_custom_service_name(create_provider):
    provider = create_provider(
        service_name="custom-service",
    )

    assert provider.service_name == "custom-service"


def test_disabled_provider(create_provider):
    provider = create_provider(enabled=False)

    assert provider.enabled is False


def test_custom_manager(
    create_provider,
    create_manager,
):
    manager = create_manager()

    provider = create_provider(
        manager=manager,
    )

    assert provider.manager is manager


def test_custom_sampler(
    create_provider,
    create_sampler,
):
    sampler = create_sampler()

    provider = create_provider(
        sampler=sampler,
    )

    assert provider is not None


def test_custom_processor(
    create_provider,
    create_processor,
):
    processor = create_processor()

    provider = create_provider(
        processor=processor,
    )

    assert provider is not None


def test_custom_exporters(create_provider):
    provider = create_provider(
        exporters=[],
    )

    assert provider is not None


# ==============================================================================
# Part 3. Properties
# ==============================================================================

def test_name(provider):
    assert isinstance(provider.name, str)


def test_service_name(provider):
    assert isinstance(provider.service_name, str)


def test_enabled(provider):
    assert isinstance(provider.enabled, bool)


def test_state(provider):
    assert provider.state is not None


def test_ready(provider):
    assert isinstance(provider.ready, bool)


def test_active(provider):
    assert isinstance(provider.active, bool)


def test_manager(provider):
    assert provider.manager is not None


def test_trace(provider):
    assert provider.trace is None


def test_current_span(provider):
    assert provider.current_span is None


def test_context(provider):
    assert provider.context is not None


def test_metadata(provider):
    assert isinstance(provider.metadata, dict)


def test_capabilities(provider):
    assert provider.capabilities is not None


# ==============================================================================
# Part 4. Provider Lifecycle
# ==============================================================================

def test_start(provider):
    result = provider.start()

    assert result is provider
    assert provider.active is True


def test_stop(provider):
    provider.start()

    result = provider.stop()

    assert result is provider
    assert provider.active is False


def test_reset(provider):
    provider.start()

    result = provider.reset()

    assert result is provider


def test_clear(provider):
    provider.start()

    result = provider.clear()

    assert result is provider


def test_close(provider):
    result = provider.close()

    assert result is provider


# ==============================================================================
# Part 5. Trace Delegation
# ==============================================================================

def test_start_trace(provider):
    trace = provider.start_trace("trace")

    assert trace is not None
    assert provider.trace is trace


def test_finish_trace(provider):
    provider.start_trace("trace")

    result = provider.finish_trace()

    assert result is not None


def test_cancel_trace(provider):
    provider.start_trace("trace")

    result = provider.cancel_trace()

    assert result is not None


def test_current_trace(provider):
    assert provider.current_trace() is None

    trace = provider.start_trace("trace")

    assert provider.current_trace() is trace


# ==============================================================================
# Part 6. Span Delegation
# ==============================================================================

def test_start_span(provider):
    provider.start_trace("trace")

    span = provider.start_span("span")

    assert span is not None
    assert provider.current_span is span


def test_finish_span(provider):
    provider.start_trace("trace")

    provider.start_span("span")

    result = provider.finish_span()

    assert result is not None


def test_cancel_span(provider):
    provider.start_trace("trace")

    provider.start_span("span")

    result = provider.cancel_span()

    assert result is not None


def test_enter_span(provider):
    provider.start_trace("trace")

    span = provider.enter_span("span")

    assert span is not None


def test_exit_span(provider):
    provider.start_trace("trace")

    provider.enter_span("span")

    result = provider.exit_span()

    assert result is not None


def test_current_span(provider):
    provider.start_trace("trace")

    span = provider.start_span("span")

    assert provider.current_span is span

# ==============================================================================
# Part 7. Context
# ==============================================================================


def test_context(provider):
    context = provider.context()

    assert context is not None


def test_current_context(provider):
    context = provider.current_context()

    assert context is not None


def test_set_context(provider):
    context = provider.current_context()

    result = provider.set_context(
        context,
    )

    assert result is provider
    assert provider.current_context() is not None


def test_update_context(provider):
    context = provider.current_context()

    provider.set_context(
        context,
    )

    result = provider.update_context(
        trace_id="trace-123",
    )

    assert result is provider


def test_clear_context(provider):
    result = provider.clear_context()

    assert result is provider


# ==============================================================================
# Part 8. Metadata
# ==============================================================================


def test_set_metadata(provider):
    result = provider.set_metadata(
        "key",
        "value",
    )

    assert result is provider
    assert provider.get_metadata("key") == "value"


def test_update_metadata(provider):
    result = provider.update_metadata(
        key="value",
        number=123,
    )

    assert result is provider
    assert provider.get_metadata("key") == "value"
    assert provider.get_metadata("number") == 123


def test_get_metadata(provider):
    provider.set_metadata(
        "key",
        "value",
    )

    assert provider.get_metadata("key") == "value"


def test_set_attribute(provider):
    result = provider.set_attribute(
        "attribute",
        "value",
    )

    assert result is provider


def test_add_event(provider):
    result = provider.add_event(
        "test-event",
    )

    assert result is provider


# ==============================================================================
# Part 9. Processing
# ==============================================================================


def test_process_span(provider):
    provider.start_trace(
        "trace",
    )

    span = provider.start_span(
        "span",
    )

    result = provider.process_span(
        span,
    )

    assert result is not None


def test_process_trace(provider):
    trace = provider.start_trace(
        "trace",
    )

    result = provider.process_trace(
        trace,
    )

    assert result is not None


def test_process(provider):
    result = provider.process()

    assert result is not None


# ==============================================================================
# Part 10. Sampling
# ==============================================================================


def test_should_sample(provider):
    result = provider.should_sample()

    assert isinstance(
        result,
        bool,
    )


def test_sampling_decision(provider):
    result = provider.sampling_decision()

    assert result is not None


# ==============================================================================
# Part 11. Export
# ==============================================================================


def test_export_span(provider):
    provider.start_trace(
        "trace",
    )

    span = provider.start_span(
        "span",
    )

    result = provider.export_span(
        span,
    )

    assert result is not None


def test_export_trace(provider):
    trace = provider.start_trace(
        "trace",
    )

    result = provider.export_trace(
        trace,
    )

    assert result is not None


def test_export(provider):
    result = provider.export()

    assert result is not None


def test_flush(provider):
    result = provider.flush()

    assert result is not None


# ==============================================================================
# Part 12. Snapshot
# ==============================================================================


def test_snapshot(provider):
    result = provider.snapshot()

    assert result is not None


def test_restore(provider):
    snapshot = provider.snapshot()

    result = provider.restore(
        snapshot,
    )

    assert result is provider


def test_copy(provider):
    result = provider.copy()

    assert result is not provider
    assert isinstance(
        result,
        TraceProvider,
    )


def test_clone(provider):
    result = provider.clone()

    assert result is not provider
    assert isinstance(
        result,
        TraceProvider,
    )


# ==============================================================================
# Part 13. Validation
# ==============================================================================


def test_validate(provider):
    result = provider.validate()

    assert isinstance(
        result,
        bool,
    )


def test_validate_trace(provider):
    trace = provider.start_trace(
        "trace",
    )

    result = provider.validate_trace(
        trace,
    )

    assert isinstance(
        result,
        bool,
    )


def test_validate_span(provider):
    provider.start_trace(
        "trace",
    )

    span = provider.start_span(
        "span",
    )

    result = provider.validate_span(
        span,
    )

    assert isinstance(
        result,
        bool,
    )


def test_validate_state(provider):
    result = provider.validate_state()

    assert isinstance(
        result,
        bool,
    )


# ==============================================================================
# Part 14. Statistics
# ==============================================================================


def test_trace_count(provider):
    assert isinstance(
        provider.trace_count,
        int,
    )


def test_span_count(provider):
    assert isinstance(
        provider.span_count,
        int,
    )


def test_active_span_count(provider):
    assert isinstance(
        provider.active_span_count,
        int,
    )


def test_exported_count(provider):
    assert isinstance(
        provider.exported_count,
        int,
    )


def test_error_count(provider):
    assert isinstance(
        provider.error_count,
        int,
    )


# ==============================================================================
# Part 15. Diagnostics
# ==============================================================================


def test_health(provider):
    result = provider.health()

    assert result is not None


def test_diagnostics(provider):
    result = provider.diagnostics()

    assert result is not None


def test_summary(provider):
    result = provider.summary()

    assert result is not None


# ==============================================================================
# Part 16. Representation
# ==============================================================================


def test_repr(provider):
    result = repr(
        provider,
    )

    assert isinstance(
        result,
        str,
    )

    assert "TraceProvider" in result


def test_str(provider):
    result = str(
        provider,
    )

    assert isinstance(
        result,
        str,
    )


# ==============================================================================
# Part 17. End
# ==============================================================================    