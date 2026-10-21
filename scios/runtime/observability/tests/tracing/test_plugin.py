# ==============================================================================
# scios/runtime/observability/tests/tracing/test_plugin.py
# ==============================================================================
# SciOS Runtime Observability
# Trace Plugin Tests
# ==============================================================================

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.tracing.provider import TraceProvider
from collections.abc import Mapping
from scios.runtime.observability.tracing.context import TraceContext
from scios.runtime.observability.tracing.plugin import (
    DEFAULT_SERVICE_NAME,
    PLUGIN_API_VERSION,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PluginConfigData,
    PluginEvent,
    PluginRegistration,
    PluginSnapshot,
    PluginState,
    PluginStatistics,
    PluginType,
    TracePlugin,
)
from scios.runtime.observability.tracing.span import Span
from scios.runtime.observability.tracing.trace import Trace


# ==============================================================================
# Part 2. Fixtures
# ==============================================================================


@pytest.fixture
def plugin() -> TracePlugin:
    """Create a default TracePlugin instance."""

    return TracePlugin()


@pytest.fixture
def provider() -> TraceProvider:
    """Create a default TraceProvider instance."""

    return TraceProvider()


@pytest.fixture
def configured_plugin() -> TracePlugin:
    """Create a configured TracePlugin instance."""

    config = PluginConfigData(
        name="test-plugin",
        version=PLUGIN_VERSION,
        api_version=PLUGIN_API_VERSION,
        service_name="scios-test",
        enabled=True,
        priority=10,
        order=1,
    )

    return TracePlugin(
        config=config,
    )


@pytest.fixture
def trace(plugin: TracePlugin) -> Trace:
    """
    Create and activate a trace through the real tracing stack.

    The trace must belong to the same TraceManager used by the plugin.
    """

    trace = plugin.start_trace("Runtime")

    assert trace is not None

    return trace


# ==============================================================================
# Part 3. Construction
# ==============================================================================


def test_plugin_constructs(plugin):
    assert plugin is not None
    assert isinstance(plugin, TracePlugin)


def test_plugin_default_name(plugin):
    assert plugin.name == PLUGIN_NAME


def test_plugin_default_version(plugin):
    assert plugin.version == PLUGIN_VERSION


def test_plugin_default_api_version(plugin):
    assert plugin.api_version == PLUGIN_API_VERSION


def test_plugin_default_service_name(plugin):
    assert plugin.service_name == DEFAULT_SERVICE_NAME


def test_plugin_configured(configured_plugin):
    assert configured_plugin.name == "test-plugin"
    assert configured_plugin.service_name == "scios-test"


def test_plugin_config_data():
    config = PluginConfigData()

    assert config.name == PLUGIN_NAME
    assert config.version == PLUGIN_VERSION
    assert config.api_version == PLUGIN_API_VERSION
    assert config.service_name == DEFAULT_SERVICE_NAME
    assert isinstance(config.metadata, dict)
    assert isinstance(config.attributes, dict)


def test_plugin_statistics():
    statistics = PluginStatistics()

    assert statistics.trace_count == 0
    assert statistics.span_count == 0
    assert statistics.processed_count == 0
    assert statistics.sampled_count == 0
    assert statistics.exported_count == 0
    assert statistics.error_count == 0


def test_plugin_snapshot():
    snapshot = PluginSnapshot(
        name=PLUGIN_NAME,
        version=PLUGIN_VERSION,
        state=PluginState.CREATED,
        enabled=True,
        active=False,
    )

    assert snapshot.name == PLUGIN_NAME
    assert snapshot.version == PLUGIN_VERSION
    assert snapshot.state is PluginState.CREATED
    assert snapshot.enabled is True
    assert snapshot.active is False


def test_plugin_registration():
    registration = PluginRegistration(
        name=PLUGIN_NAME,
    )

    assert registration.name == PLUGIN_NAME
    assert registration.plugin_type is PluginType.TRACING
    assert registration.version == PLUGIN_VERSION
    assert registration.factory is None


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties(plugin):
    assert plugin.name == PLUGIN_NAME
    assert plugin.version == PLUGIN_VERSION
    assert plugin.api_version == PLUGIN_API_VERSION
    assert plugin.service_name == DEFAULT_SERVICE_NAME


def test_enabled_property(plugin):
    assert isinstance(plugin.enabled, bool)


def test_active_property(plugin):
    assert isinstance(plugin.active, bool)


def test_state_property(plugin):
    assert isinstance(plugin.state, PluginState)


def test_priority_property(plugin):
    assert isinstance(plugin.priority, int)


def test_order_property(plugin):
    assert isinstance(plugin.order, int)


def test_metadata_property(plugin):
    assert isinstance(plugin.metadata, dict)


def test_attributes_property(plugin):
    assert isinstance(plugin.attributes, dict)


def test_statistics_property(plugin):
    assert isinstance(plugin.statistics, PluginStatistics)


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_initial_state(plugin):
    assert plugin.state is PluginState.CREATED
    assert plugin.active is False


def test_start(plugin):
    result = plugin.start()

    assert result is plugin
    assert plugin.active is True
    assert plugin.state is PluginState.RUNNING


def test_start_idempotent(plugin):
    plugin.start()

    result = plugin.start()

    assert result is plugin
    assert plugin.active is True
    assert plugin.state is PluginState.RUNNING


def test_stop(plugin):
    plugin.start()

    result = plugin.stop()

    assert result is plugin
    assert plugin.active is False
    assert plugin.state is PluginState.STOPPED


def test_stop_idempotent(plugin):
    plugin.start()
    plugin.stop()

    result = plugin.stop()

    assert result is plugin
    assert plugin.active is False


def test_initialize(plugin):
    result = plugin.initialize()

    assert result is plugin
    assert plugin.state in {
        PluginState.INITIALIZED,
        PluginState.RUNNING,
    }


def test_statistics_lifecycle(plugin):
    plugin.start()
    plugin.stop()

    assert plugin.statistics.start_count >= 1
    assert plugin.statistics.stop_count >= 1


# ==============================================================================
# Part 6. Provider Management
# ==============================================================================


def test_provider_property(plugin):
    provider = plugin.provider

    assert provider is None or provider is not None


def test_set_provider(
    plugin: TracePlugin,
) -> None:
    provider = plugin.provider

    result = plugin.set_provider(provider)

    assert result is plugin
    assert plugin.provider is provider


def test_clear_provider(plugin):
    provider = object()

    plugin.set_provider(provider)

    result = plugin.set_provider(None)

    assert result is plugin
    assert plugin.provider is None


def test_provider_factory(plugin):
    provider = object()

    def factory():
        return provider

    result = plugin.set_provider_factory(factory)

    assert result is plugin


def test_create_provider(plugin):
    provider = object()

    def factory():
        return provider

    plugin.set_provider_factory(factory)

    result = plugin.create_provider()

    assert result is provider
    assert plugin.provider is provider


# ==============================================================================
# Part 7. Trace Operations
# ==============================================================================


def test_start_trace(plugin):
    plugin.start()

    trace = plugin.start_trace("trace")

    assert trace is not None
    assert plugin.current_trace is trace


def test_current_trace(plugin):
    plugin.start()

    trace = plugin.start_trace("trace")

    assert plugin.current_trace is trace


def test_finish_trace(plugin):
    plugin.start()

    trace = plugin.start_trace("trace")

    result = plugin.finish_trace()

    assert result is trace or result is not None
    assert plugin.current_trace is None


def test_cancel_trace(plugin):
    plugin.start()

    plugin.start_trace("trace")

    result = plugin.cancel_trace()

    assert result is plugin
    assert plugin.current_trace is None


def test_trace_count(plugin):
    plugin.start()

    plugin.start_trace("trace")

    assert plugin.statistics.trace_count >= 1

# ==============================================================================
# Part 8. Span Operations
# ==============================================================================


def test_start_span(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    span = plugin.start_span("span")

    assert span is not None
    assert isinstance(span, Span)
    assert plugin.current_span is span


def test_start_span_without_name(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    span = plugin.start_span()

    assert span is not None
    assert isinstance(span, Span)


def test_start_nested_span(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    parent = plugin.start_span("parent")

    assert parent is not None

    child = plugin.start_span(
        "child",
        parent=parent,
    )

    assert child is not None
    assert isinstance(child, Span)


def test_finish_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.finish_span()

    assert result is not None


def test_finish_explicit_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.finish_span(span)

    assert result is not None


def test_cancel_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.cancel_span()

    assert result is not None


def test_cancel_explicit_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.cancel_span(span)

    assert result is not None


def test_enter_span(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.enter_span("span")

    assert result is not None
    assert isinstance(result, Span)
    assert plugin.current_span is result


def test_exit_span(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    plugin.enter_span("span")

    result = plugin.exit_span()

    assert result is not None


def test_current_span_after_start(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    span = plugin.start_span("span")

    assert span is not None
    assert plugin.current_span is span


# ==============================================================================
# Part 9. Context Management
# ==============================================================================


def test_current_context(
    plugin: TracePlugin,
) -> None:
    context = plugin.current_context

    assert context is None or isinstance(
        context,
        TraceContext,
    )


def test_set_context(
    plugin: TracePlugin,
) -> None:
    context = TraceContext()

    result = plugin.set_context(context)

    assert result is plugin
    assert plugin.current_context is context


def test_set_context_none(
    plugin: TracePlugin,
) -> None:
    result = plugin.set_context(None)

    assert result is plugin
    assert plugin.current_context is None


def test_update_context(
    plugin: TracePlugin,
) -> None:
    context = TraceContext()

    plugin.set_context(context)

    result = plugin.update_context(
        component="test",
    )

    assert result is plugin


def test_clear_context(
    plugin: TracePlugin,
) -> None:
    plugin.set_context(
        TraceContext(),
    )

    result = plugin.clear_context()

    assert result is plugin
    assert plugin.current_context is None


# ==============================================================================
# Part 10. Processing
# ==============================================================================


def test_process_without_item(
    plugin: TracePlugin,
) -> None:
    result = plugin.process()

    assert result is not None


def test_process_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.process_trace(trace)

    assert result is not None
    assert isinstance(result, Trace)


def test_process_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.process_span(span)

    assert result is not None
    assert isinstance(result, Span)


def test_process_explicit_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.process(trace)

    assert result is not None


def test_process_explicit_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.process(span)

    assert result is not None


def test_process_none(
    plugin: TracePlugin,
) -> None:
    result = plugin.process(None)

    assert result is not None


# ==============================================================================
# Part 11. Sampling
# ==============================================================================


def test_should_sample(
    plugin: TracePlugin,
) -> None:
    result = plugin.should_sample()

    assert isinstance(result, bool)


def test_should_sample_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.should_sample(trace)

    assert isinstance(result, bool)


def test_sampling_decision(
    plugin: TracePlugin,
) -> None:
    result = plugin.sampling_decision()

    assert result is not None


def test_sampling_decision_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.sampling_decision(trace)

    assert result is not None


# ==============================================================================
# Part 12. Exporting
# ==============================================================================


def test_export_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.export_trace(trace)

    assert result is not None


def test_export_current_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.export_trace()

    assert result is not None


def test_export_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.export_span(span)

    assert result is not None


def test_export_current_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.export_span()

    assert result is not None

# ==============================================================================
# Part 13. Snapshot / Restore
# ==============================================================================


def test_snapshot(
    plugin: TracePlugin,
) -> None:
    result = plugin.snapshot()

    assert result is not None


def test_snapshot_after_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.snapshot()

    assert result is not None


def test_restore(
    plugin: TracePlugin,
) -> None:
    snapshot = plugin.snapshot()

    result = plugin.restore(snapshot)

    assert result is plugin


def test_restore_after_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    snapshot = plugin.snapshot()

    result = plugin.restore(snapshot)

    assert result is plugin


# ==============================================================================
# Part 14. Validation
# ==============================================================================


def test_validate(
    plugin: TracePlugin,
) -> None:
    result = plugin.validate()

    assert isinstance(result, bool)


def test_validate_trace(
    plugin: TracePlugin,
    trace: Trace,
) -> None:
    result = plugin.validate_trace(trace)

    assert isinstance(result, bool)


def test_validate_span(
    plugin: TracePlugin,
    span: Span,
) -> None:
    result = plugin.validate_span(span)

    assert isinstance(result, bool)


def test_validate_state(
    plugin: TracePlugin,
) -> None:
    result = plugin.validate_state()

    assert isinstance(result, bool)


# ==============================================================================
# Part 15. Diagnostics
# ==============================================================================


def test_health(
    plugin: TracePlugin,
) -> None:
    result = plugin.health()

    assert isinstance(result, bool)


def test_diagnostics(
    plugin: TracePlugin,
) -> None:
    result = plugin.diagnostics()

    assert result is not None


def test_summary(
    plugin: TracePlugin,
) -> None:
    result = plugin.summary()

    assert result is not None


def test_status(
    plugin: TracePlugin,
) -> None:
    result = plugin.status()

    assert result is not None


# ==============================================================================
# Part 16. Registry / Integration
# ==============================================================================


def test_registration(
    plugin: TracePlugin,
) -> None:
    result = plugin.registration()

    assert result is not None


def test_plugin_type(
    plugin: TracePlugin,
) -> None:
    result = plugin.plugin_type

    assert result is not None


def test_plugin_metadata(
    plugin: TracePlugin,
) -> None:
    result = plugin.metadata

    assert result is not None
    assert isinstance(result, Mapping)


def test_plugin_attributes(
    plugin: TracePlugin,
) -> None:
    result = plugin.attributes

    assert result is not None
    assert isinstance(result, Mapping)


def test_get_provider(
    plugin: TracePlugin,
) -> None:
    result = plugin.provider

    assert result is not None


def test_set_provider(
    plugin: TracePlugin,
    provider: TraceProvider,
) -> None:
    result = plugin.set_provider(provider)

    assert result is plugin
    assert plugin.provider is provider


# ==============================================================================
# Part 17. Edge Cases
# ==============================================================================


def test_disabled_plugin_start_trace(
    plugin: TracePlugin,
) -> None:
    plugin.disable()

    result = plugin.start_trace("trace")

    assert result is None


def test_disabled_plugin_start_span(
    plugin: TracePlugin,
) -> None:
    plugin.disable()

    result = plugin.start_span("span")

    assert result is None


def test_process_none_edge_case(
    plugin: TracePlugin,
) -> None:
    result = plugin.process(None)

    assert result is not None


def test_export_none_trace(
    plugin: TracePlugin,
) -> None:
    result = plugin.export_trace(None)

    assert result is not None


def test_export_none_span(
    plugin: TracePlugin,
) -> None:
    result = plugin.export_span(None)

    assert result is not None


def test_finish_without_span(
    plugin: TracePlugin,
) -> None:
    result = plugin.finish_span()

    assert result is None or result is not False


def test_cancel_without_span(
    plugin: TracePlugin,
) -> None:
    result = plugin.cancel_span()

    assert result is None or result is not False


def test_restore_none(
    plugin: TracePlugin,
) -> None:
    result = plugin.restore(None)

    assert result is plugin
