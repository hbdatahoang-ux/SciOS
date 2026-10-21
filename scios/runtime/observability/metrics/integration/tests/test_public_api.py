"""
Tests for Runtime Metrics Integration public API.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

import scios.runtime.observability.metrics.integration as integration


# ============================================================
# Public Classes
# ============================================================


def test_processor_integration_exported():

    assert hasattr(
        integration,
        "MetricProcessorIntegration",
    )

    assert integration.MetricProcessorIntegration is not None


def test_middleware_integration_exported():

    assert hasattr(
        integration,
        "MetricMiddlewareIntegration",
    )

    assert integration.MetricMiddlewareIntegration is not None


def test_pipeline_integration_exported():

    assert hasattr(
        integration,
        "MetricPipelineIntegration",
    )

    assert integration.MetricPipelineIntegration is not None


def test_runtime_integration_exported():

    assert hasattr(
        integration,
        "MetricRuntimeIntegration",
    )

    assert integration.MetricRuntimeIntegration is not None


def test_exporter_integration_exported():

    assert hasattr(
        integration,
        "MetricExporterIntegration",
    )

    assert integration.MetricExporterIntegration is not None


def test_logging_exported():

    assert hasattr(
        integration,
        "MetricLoggingIntegration",
    )

    assert integration.MetricLoggingIntegration is not None


def test_tracing_exported():

    assert hasattr(
        integration,
        "MetricTracingIntegration",
    )

    assert integration.MetricTracingIntegration is not None


def test_profiling_exported():

    assert hasattr(
        integration,
        "MetricProfilingIntegration",
    )

    assert integration.MetricProfilingIntegration is not None


def test_qtc_exported():

    assert hasattr(
        integration,
        "MetricQTCIntegration",
    )

    assert integration.MetricQTCIntegration is not None


# ============================================================
# Canonical Aliases
# ============================================================


def test_processor_alias():

    assert (
        integration.ProcessorIntegration
        is integration.MetricProcessorIntegration
    )


def test_middleware_alias():

    assert (
        integration.MiddlewareIntegration
        is integration.MetricMiddlewareIntegration
    )


def test_pipeline_alias():

    assert (
        integration.PipelineIntegration
        is integration.MetricPipelineIntegration
    )


def test_runtime_alias():

    assert (
        integration.RuntimeIntegration
        is integration.MetricRuntimeIntegration
    )


def test_exporter_alias():

    assert (
        integration.ExporterIntegration
        is integration.MetricExporterIntegration
    )


# ============================================================
# Component Registry
# ============================================================


def test_component_registry_exported():

    assert hasattr(
        integration,
        "_COMPONENTS",
    )

    registry = integration._COMPONENTS

    assert isinstance(
        registry,
        dict,
    )


def test_component_registry():

    registry = integration._COMPONENTS

    assert registry["processor"] is (
        integration.MetricProcessorIntegration
    )

    assert registry["middleware"] is (
        integration.MetricMiddlewareIntegration
    )

    assert registry["pipeline"] is (
        integration.MetricPipelineIntegration
    )

    assert registry["runtime"] is (
        integration.MetricRuntimeIntegration
    )

    assert registry["exporter"] is (
        integration.MetricExporterIntegration
    )

    assert registry["logging"] is (
        integration.MetricLoggingIntegration
    )

    assert registry["tracing"] is (
        integration.MetricTracingIntegration
    )

    assert registry["profiling"] is (
        integration.MetricProfilingIntegration
    )

    assert registry["qtc"] is (
        integration.MetricQTCIntegration
    )


# ============================================================
# Component Discovery
# ============================================================


def test_available_components():

    components = integration.available_components()

    assert isinstance(
        components,
        tuple,
    )

    assert components == (
        "processor",
        "middleware",
        "pipeline",
        "runtime",
        "exporter",
        "logging",
        "tracing",
        "profiling",
        "qtc",
    )


def test_component_count():

    assert (
        integration.component_count()
        == 9
    )


@pytest.mark.parametrize(
    (
        "name",
        "expected",
    ),
    [
        (
            "processor",
            integration.MetricProcessorIntegration,
        ),
        (
            "middleware",
            integration.MetricMiddlewareIntegration,
        ),
        (
            "pipeline",
            integration.MetricPipelineIntegration,
        ),
        (
            "runtime",
            integration.MetricRuntimeIntegration,
        ),
        (
            "exporter",
            integration.MetricExporterIntegration,
        ),
        (
            "logging",
            integration.MetricLoggingIntegration,
        ),
        (
            "tracing",
            integration.MetricTracingIntegration,
        ),
        (
            "profiling",
            integration.MetricProfilingIntegration,
        ),
        (
            "qtc",
            integration.MetricQTCIntegration,
        ),
    ],
)
def test_get_component(
    name,
    expected,
):

    assert (
        integration.get_component(name)
        is expected
    )


def test_get_unknown_component():

    with pytest.raises(
        KeyError,
        match="unknown integration component",
    ):
        integration.get_component(
            "unknown",
        )


def test_get_component_requires_string():

    with pytest.raises(
        TypeError,
        match="component name must be a string",
    ):
        integration.get_component(
            123,
        )


# ============================================================
# Factories
# ============================================================


@pytest.mark.parametrize(
    (
        "factory",
        "expected",
    ),
    [
        (
            integration.create_processor_integration,
            integration.MetricProcessorIntegration,
        ),
        (
            integration.create_middleware_integration,
            integration.MetricMiddlewareIntegration,
        ),
        (
            integration.create_pipeline_integration,
            integration.MetricPipelineIntegration,
        ),
        (
            integration.create_runtime_integration,
            integration.MetricRuntimeIntegration,
        ),
        (
            integration.create_exporter_integration,
            integration.MetricExporterIntegration,
        ),
        (
            integration.create_runtime,
            integration.MetricRuntimeIntegration,
        ),
        (
            integration.create_logging,
            integration.MetricLoggingIntegration,
        ),
        (
            integration.create_tracing,
            integration.MetricTracingIntegration,
        ),
        (
            integration.create_profiling,
            integration.MetricProfilingIntegration,
        ),
        (
            integration.create_qtc,
            integration.MetricQTCIntegration,
        ),
    ],
)
def test_factory(
    factory,
    expected,
):

    instance = factory()

    assert isinstance(
        instance,
        expected,
    )


# ============================================================
# Factory Isolation
# ============================================================


def test_factories_return_new_instances():

    first = integration.create_processor_integration()
    second = integration.create_processor_integration()

    assert isinstance(
        first,
        integration.MetricProcessorIntegration,
    )

    assert isinstance(
        second,
        integration.MetricProcessorIntegration,
    )

    assert first is not second


# ============================================================
# __all__
# ============================================================


def test_all_is_tuple():

    public_api = integration.__all__

    assert isinstance(
        public_api,
        tuple,
    )


def test_all_contains_public_classes():

    public_api = set(
        integration.__all__
    )

    required = {
        "MetricProcessorIntegration",
        "MetricMiddlewareIntegration",
        "MetricPipelineIntegration",
        "MetricRuntimeIntegration",
        "MetricExporterIntegration",
        "MetricLoggingIntegration",
        "MetricTracingIntegration",
        "MetricProfilingIntegration",
        "MetricQTCIntegration",
    }

    assert required.issubset(
        public_api
    )


def test_all_contains_aliases():

    public_api = set(
        integration.__all__
    )

    required = {
        "ProcessorIntegration",
        "MiddlewareIntegration",
        "PipelineIntegration",
        "RuntimeIntegration",
        "ExporterIntegration",
    }

    assert required.issubset(
        public_api
    )


def test_all_contains_factories():

    public_api = set(
        integration.__all__
    )

    required = {
        "create_processor_integration",
        "create_middleware_integration",
        "create_pipeline_integration",
        "create_runtime_integration",
        "create_exporter_integration",
        "create_runtime",
        "create_logging",
        "create_tracing",
        "create_profiling",
        "create_qtc",
    }

    assert required.issubset(
        public_api
    )


def test_all_contains_discovery_helpers():

    public_api = set(
        integration.__all__
    )

    required = {
        "available_components",
        "component_count",
        "get_component",
    }

    assert required.issubset(
        public_api
    )


def test_public_symbols_are_accessible():

    for name in integration.__all__:

        assert hasattr(
            integration,
            name,
        )


# ============================================================
# Public API Instantiation Smoke Test
# ============================================================


@pytest.mark.parametrize(
    "class_name",
    [
        "MetricProcessorIntegration",
        "MetricMiddlewareIntegration",
        "MetricPipelineIntegration",
        "MetricRuntimeIntegration",
        "MetricExporterIntegration",
        "MetricLoggingIntegration",
        "MetricTracingIntegration",
        "MetricProfilingIntegration",
        "MetricQTCIntegration",
    ],
)
def test_public_classes_are_instantiable(
    class_name,
):

    cls = getattr(
        integration,
        class_name,
    )

    instance = cls()

    assert isinstance(
        instance,
        cls,
    )
