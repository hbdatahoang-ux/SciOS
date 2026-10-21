"""
SciOS Runtime Metrics Exporters
===============================

Public exporter API.
"""

from __future__ import annotations

from .base import (
    BaseExporter,
    DEFAULT_ENCODING,
    DEFAULT_VERSION,
    ExportManyPayload,
    ExportPayload,
    Serializable,
)

from .registry import (
    ExporterRegistry,
    default_registry,
)

from .json_exporter import JSONExporter

try:
    from .prometheus_exporter import PrometheusExporter
except ImportError:
    PrometheusExporter = None

try:
    from .opentelemetry_exporter import OpenTelemetryExporter
except ImportError:
    OpenTelemetryExporter = None

__version__ = "0.1.0"


def create_exporter(
    name: str,
    *args,
    **kwargs,
):
    """
    Create exporter instance from the default registry.
    """
    return default_registry.create(
        name,
        *args,
        **kwargs,
    )


__all__ = [
    "__version__",

    # base
    "BaseExporter",
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "Serializable",
    "ExportPayload",
    "ExportManyPayload",

    # registry
    "ExporterRegistry",
    "default_registry",

    # exporters
    "JSONExporter",
    "PrometheusExporter",
    "OpenTelemetryExporter",

    # helpers
    "create_exporter",
]