"""
SciOS-NG Runtime Observability Exporters
========================================

Unified exporter public API.

Responsibilities
----------------
- Provide stable exporter imports.
- Register exporter implementations.
- Create exporters dynamically.
- Expose exporter discovery APIs.

Supported Exporters
-------------------
- JSON
- Prometheus
- OpenTelemetry
- Stdout
- Jaeger
- Zipkin

Python 3.11+
"""

from __future__ import annotations


from typing import Any
from typing import Type


# ==============================================================================
# Metadata
# ==============================================================================

__title__ = "SciOS-NG Runtime Observability Exporters"

__version__ = "0.3.0-alpha"

__author__ = "SciOS-NG Team"

__license__ = "MIT"



# ==============================================================================
# Base Exporter
# ==============================================================================

from .base import (
    BaseExporter,
    ExportResult,
)



# ==============================================================================
# JSON Exporter
# ==============================================================================

from .json import (
    JSONExporter,
)



# ==============================================================================
# Prometheus Exporter
# ==============================================================================

from .prometheus import (
    PrometheusExporter,
)



# ==============================================================================
# OpenTelemetry Exporter
# ==============================================================================

from .opentelemetry import (
    OpenTelemetryExporter,
)



# ==============================================================================
# Optional Exporters
# ==============================================================================

try:

    from .stdout import (
        StdoutExporter,
    )

except ImportError:

    StdoutExporter = None



try:

    from .jaeger import (
        JaegerExporter,
    )

except ImportError:

    JaegerExporter = None



try:

    from .zipkin import (
        ZipkinExporter,
    )

except ImportError:

    ZipkinExporter = None



# ==============================================================================
# Exporter Registry
# ==============================================================================


EXPORTER_REGISTRY: dict[
    str,
    Type[BaseExporter],
] = {

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

    EXPORTER_REGISTRY[
        "stdout"
    ] = StdoutExporter



if JaegerExporter is not None:

    EXPORTER_REGISTRY[
        "jaeger"
    ] = JaegerExporter



if ZipkinExporter is not None:

    EXPORTER_REGISTRY[
        "zipkin"
    ] = ZipkinExporter



EXPORTER_NAMES = sorted(
    EXPORTER_REGISTRY.keys()
)



# ==============================================================================
# Factory
# ==============================================================================


def create_exporter(
    exporter_type: str,
    **kwargs: Any,
) -> BaseExporter:
    """
    Create exporter instance.

    Example
    -------

    exporter = create_exporter(
        "json"
    )

    exporter = create_exporter(
        "prometheus",
        namespace="scios",
    )
    """


    if not isinstance(
        exporter_type,
        str,
    ):

        raise TypeError(
            "exporter_type must be a string"
        )


    name = (
        exporter_type
        .strip()
        .lower()
    )


    if not name:

        raise ValueError(
            "exporter_type cannot be empty"
        )


    exporter_cls = (
        EXPORTER_REGISTRY.get(
            name
        )
    )


    if exporter_cls is None:

        raise ValueError(
            f"Unknown exporter: {name}. "
            f"Available: {EXPORTER_NAMES}"
        )


    return exporter_cls(
        **kwargs
    )



# ==============================================================================
# Discovery API
# ==============================================================================


def available_exporters() -> list[str]:
    """
    Return supported exporter names.
    """

    return list(
        EXPORTER_NAMES
    )



def is_exporter_available(
    exporter_type: str,
) -> bool:
    """
    Check exporter availability.
    """

    if not isinstance(
        exporter_type,
        str,
    ):

        return False


    return (
        exporter_type
        .strip()
        .lower()
        in EXPORTER_REGISTRY
    )



def get_exporter_class(
    exporter_type: str,
) -> Type[BaseExporter]:
    """
    Get exporter implementation class.
    """


    name = (
        exporter_type
        .strip()
        .lower()
    )


    exporter_cls = (
        EXPORTER_REGISTRY.get(
            name
        )
    )


    if exporter_cls is None:

        raise ValueError(
            f"Unknown exporter: {name}"
        )


    return exporter_cls



# ==============================================================================
# Public API
# ==============================================================================


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

    "EXPORTER_REGISTRY",

    "EXPORTER_NAMES",



    # Factory

    "create_exporter",

    "available_exporters",

    "is_exporter_available",

    "get_exporter_class",

]