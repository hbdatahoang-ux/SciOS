"""
SciOS-NG Runtime Observability Exporters
========================================

Unified exporter public API.

Responsibilities
----------------
- Stable exporter imports.
- Exporter discovery.
- Dynamic exporter creation.
- Plugin registry integration.

Python 3.11+
"""


from __future__ import annotations


from typing import Any


# ==========================================================
# Metadata
# ==========================================================

__title__ = (
    "SciOS-NG Runtime Observability Exporters"
)

__version__ = "0.3.0-alpha"

__author__ = "SciOS-NG Team"

__license__ = "MIT"



# ==========================================================
# Base API
# ==========================================================

from .base import (
    BaseExporter,
    ExportResult,
)



# ==========================================================
# Built-in Exporters
# ==========================================================

from .json import (
    JSONExporter,
)


from .prometheus import (
    PrometheusExporter,
)


from .opentelemetry import (
    OpenTelemetryExporter,
)



# ==========================================================
# Optional Exporters
# ==========================================================

try:
    from .stdout import StdoutExporter
except ImportError:
    StdoutExporter = None



try:
    from .jaeger import JaegerExporter
except ImportError:
    JaegerExporter = None



try:
    from .zipkin import ZipkinExporter
except ImportError:
    ZipkinExporter = None



# ==========================================================
# Registry Core
# ==========================================================

from .registry import (
    ExporterRegistry,
    default_registry,
)



# ==========================================================
# Register Built-ins
# ==========================================================


def _register_builtin_exporters() -> None:
    """
    Register built-in exporters.
    """

    exporters = {

        "json":
            JSONExporter,

        "prometheus":
            PrometheusExporter,

        "opentelemetry":
            OpenTelemetryExporter,

        "otel":
            OpenTelemetryExporter,

    }


    if StdoutExporter is not None:

        exporters["stdout"] = StdoutExporter


    if JaegerExporter is not None:

        exporters["jaeger"] = JaegerExporter


    if ZipkinExporter is not None:

        exporters["zipkin"] = ZipkinExporter



    for name, exporter in exporters.items():

        if not default_registry.has(name):

            default_registry.register(
                name,
                exporter,
            )



_register_builtin_exporters()



# ==========================================================
# Factory API
# ==========================================================


def create_exporter(
    exporter_type: str,
    **kwargs: Any,
) -> BaseExporter:
    """
    Create exporter instance.
    """


    if not isinstance(
        exporter_type,
        str,
    ):
        raise TypeError(
            "exporter_type must be string"
        )


    name = exporter_type.strip().lower()


    if not name:

        raise ValueError(
            "exporter_type cannot be empty"
        )



    exporter_cls = (
        default_registry.get(name)
    )


    return exporter_cls(
        **kwargs
    )



# ==========================================================
# Discovery API
# ==========================================================


def available_exporters() -> list[str]:
    """
    Return registered exporters.
    """

    return list(
        default_registry.available()
    )



def is_exporter_available(
    exporter_type: str,
) -> bool:
    """
    Check exporter existence.
    """

    if not isinstance(
        exporter_type,
        str,
    ):
        return False


    return default_registry.has(
        exporter_type.strip().lower()
    )



def get_exporter_class(
    exporter_type: str,
) -> type[BaseExporter]:
    """
    Return exporter class.
    """

    return default_registry.get(
        exporter_type.strip().lower()
    )



# ==========================================================
# Public API
# ==========================================================


__all__ = [

    # Metadata

    "__title__",
    "__version__",
    "__author__",
    "__license__",


    # Base

    "BaseExporter",
    "ExportResult",


    # Exporters

    "JSONExporter",
    "PrometheusExporter",
    "OpenTelemetryExporter",
    "StdoutExporter",
    "JaegerExporter",
    "ZipkinExporter",


    # Registry

    "ExporterRegistry",
    "default_registry",


    # Factory

    "create_exporter",
    "available_exporters",
    "is_exporter_available",
    "get_exporter_class",

]