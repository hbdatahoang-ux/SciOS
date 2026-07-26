"""
SciOS-NG Runtime Metrics Exporters

Public API for metrics exporter subsystem.

SciOS-NG v0.2
"""


# ==============================================================
# Base Exporter
# ==============================================================

from .exporter import (
    MetricExporter,
)



# ==============================================================
# Runtime Exporters
# ==============================================================

from .memory import (
    MemoryExporter,
)


from .json import (
    JSONExporter,
)


from .prometheus import (
    PrometheusExporter,
)


from .otel import (
    OpenTelemetryExporter,
)


from .influxdb import (
    InfluxDBExporter,
)


from .csv import (
    CSVExporter,
)


from .parquet import (
    ParquetExporter,
)



# ==============================================================
# Aliases
# ==============================================================

OTelExporter = OpenTelemetryExporter



# ==============================================================
# Factory
# ==============================================================

EXPORTERS = {

    "memory":
        MemoryExporter,


    "json":
        JSONExporter,


    "prometheus":
        PrometheusExporter,


    "otel":
        OpenTelemetryExporter,


    "influxdb":
        InfluxDBExporter,


    "csv":
        CSVExporter,


    "parquet":
        ParquetExporter,

}



def create_exporter(
    exporter: str,
    **kwargs,
):
    """
    Create runtime metrics exporter.

    Example:

        exporter = create_exporter(
            "prometheus"
        )

    """

    if exporter not in EXPORTERS:

        raise ValueError(
            f"Unknown exporter: {exporter}"
        )


    return EXPORTERS[exporter](
        **kwargs
    )



# ==============================================================
# Public Namespace
# ==============================================================

__all__ = [

    # Base

    "MetricExporter",


    # Exporters

    "MemoryExporter",

    "JSONExporter",

    "PrometheusExporter",

    "OpenTelemetryExporter",

    "OTelExporter",

    "InfluxDBExporter",

    "CSVExporter",

    "ParquetExporter",


    # Factory

    "EXPORTERS",

    "create_exporter",

]