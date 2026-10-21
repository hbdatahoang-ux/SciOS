"""
SciOS Metrics Integration
=========================

Public integration API for the SciOS metrics subsystem.

This package exposes the concrete integration adapters together with
factory and discovery helpers.

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Public integration classes
# ==============================================================================

from .processor_integration import MetricProcessorIntegration
from .middleware_integration import MetricMiddlewareIntegration
from .pipeline_integration import MetricPipelineIntegration
from .runtime_integration import MetricRuntimeIntegration
from .exporter_integration import MetricExporterIntegration

from .logging import MetricLoggingIntegration
from .tracing import MetricTracingIntegration
from .profiling import MetricProfilingIntegration
from .qtc import MetricQTCIntegration


# ==============================================================================
# Compatibility aliases
# ==============================================================================

# Short aliases for the core integration adapters.
#
# These aliases intentionally point to the exact same class objects.
# They do not create subclasses or wrappers.

ProcessorIntegration = MetricProcessorIntegration
MiddlewareIntegration = MetricMiddlewareIntegration
PipelineIntegration = MetricPipelineIntegration
RuntimeIntegration = MetricRuntimeIntegration
ExporterIntegration = MetricExporterIntegration


# ==============================================================================
# Component registry
# ==============================================================================

_COMPONENTS: dict[str, type] = {
    "processor": MetricProcessorIntegration,
    "middleware": MetricMiddlewareIntegration,
    "pipeline": MetricPipelineIntegration,
    "runtime": MetricRuntimeIntegration,
    "exporter": MetricExporterIntegration,
    "logging": MetricLoggingIntegration,
    "tracing": MetricTracingIntegration,
    "profiling": MetricProfilingIntegration,
    "qtc": MetricQTCIntegration,
}


# Public compatibility name for the component registry.
#
# Keep both names available:
#
#   _COMPONENTS
#   INTEGRATION_COMPONENTS
#
# `_COMPONENTS` remains the internal canonical object while
# `INTEGRATION_COMPONENTS` is the public API name.
INTEGRATION_COMPONENTS = _COMPONENTS


# ==============================================================================
# Factory helpers
# ==============================================================================


def create_processor_integration(
    *args,
    **kwargs,
) -> MetricProcessorIntegration:
    """
    Create a metric processor integration.
    """
    return MetricProcessorIntegration(
        *args,
        **kwargs,
    )


def create_middleware_integration(
    *args,
    **kwargs,
) -> MetricMiddlewareIntegration:
    """
    Create a metric middleware integration.
    """
    return MetricMiddlewareIntegration(
        *args,
        **kwargs,
    )


def create_pipeline_integration(
    *args,
    **kwargs,
) -> MetricPipelineIntegration:
    """
    Create a metric pipeline integration.
    """
    return MetricPipelineIntegration(
        *args,
        **kwargs,
    )


def create_runtime_integration(
    *args,
    **kwargs,
) -> MetricRuntimeIntegration:
    """
    Create a metric runtime integration.
    """
    return MetricRuntimeIntegration(
        *args,
        **kwargs,
    )


def create_exporter_integration(
    *args,
    **kwargs,
) -> MetricExporterIntegration:
    """
    Create a metric exporter integration.
    """
    return MetricExporterIntegration(
        *args,
        **kwargs,
    )


def create_runtime(
    *args,
    **kwargs,
) -> MetricRuntimeIntegration:
    """
    Create a runtime integration.

    This is a convenience alias for
    :func:`create_runtime_integration`.
    """
    return create_runtime_integration(
        *args,
        **kwargs,
    )


def create_logging(
    *args,
    **kwargs,
) -> MetricLoggingIntegration:
    """
    Create a metric logging integration.
    """
    return MetricLoggingIntegration(
        *args,
        **kwargs,
    )


def create_tracing(
    *args,
    **kwargs,
) -> MetricTracingIntegration:
    """
    Create a metric tracing integration.
    """
    return MetricTracingIntegration(
        *args,
        **kwargs,
    )


def create_profiling(
    *args,
    **kwargs,
) -> MetricProfilingIntegration:
    """
    Create a metric profiling integration.
    """
    return MetricProfilingIntegration(
        *args,
        **kwargs,
    )


def create_qtc(
    *args,
    **kwargs,
) -> MetricQTCIntegration:
    """
    Create a metric QTC integration.
    """
    return MetricQTCIntegration(
        *args,
        **kwargs,
    )


# ==============================================================================
# Component discovery
# ==============================================================================


def available_components() -> tuple[str, ...]:
    """
    Return the names of all publicly available integration components.

    The ordering follows the canonical component registry.
    """
    return tuple(
        _COMPONENTS.keys()
    )


def component_count() -> int:
    """
    Return the number of available integration components.
    """
    return len(
        _COMPONENTS
    )


def get_component(
    name: str,
) -> type:
    """
    Return an integration class by component name.

    Parameters
    ----------
    name:
        Component name such as ``"runtime"`` or ``"logging"``.

    Returns
    -------
    type
        The registered integration class.

    Raises
    ------
    TypeError
        If ``name`` is not a string.

    KeyError
        If ``name`` is not a registered component.
    """
    if not isinstance(
        name,
        str,
    ):
        raise TypeError(
            "component name must be a string"
        )

    try:
        return _COMPONENTS[name]
    except KeyError:
        raise KeyError(
            f"unknown integration component: {name!r}"
        ) from None


# ==============================================================================
# Public API
# ==============================================================================

__all__ = (
    # ------------------------------------------------------------------
    # Canonical integration classes
    # ------------------------------------------------------------------
    "MetricProcessorIntegration",
    "MetricMiddlewareIntegration",
    "MetricPipelineIntegration",
    "MetricRuntimeIntegration",
    "MetricExporterIntegration",
    "MetricLoggingIntegration",
    "MetricTracingIntegration",
    "MetricProfilingIntegration",
    "MetricQTCIntegration",

    # ------------------------------------------------------------------
    # Short compatibility aliases
    # ------------------------------------------------------------------
    "ProcessorIntegration",
    "MiddlewareIntegration",
    "PipelineIntegration",
    "RuntimeIntegration",
    "ExporterIntegration",

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------
    "INTEGRATION_COMPONENTS",

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------
    "available_components",
    "component_count",
    "get_component",
)