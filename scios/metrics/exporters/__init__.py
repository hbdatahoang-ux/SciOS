"""
SciOS Metrics Exporters Compatibility API
=========================================

Legacy compatibility layer.

Old API:

    scios.metrics.exporters

New implementation:

    scios.runtime.observability.exporters
"""


from __future__ import annotations


from typing import Any



# ==========================================================
# Exporter Implementations
# ==========================================================


from scios.runtime.observability.exporters.base import (
    BaseExporter,
    ExportRecord,
    ExportResult,
    ExportStatus,
    ExportFormat,
)


from scios.runtime.observability.exporters import (
    JSONExporter,
    PrometheusExporter,
    OpenTelemetryExporter,
    JaegerExporter,
    ZipkinExporter,
    StdoutExporter,
)



# ==========================================================
# Registry
# ==========================================================


class ExporterRegistry:
    """
    Compatibility exporter registry.
    """


    def __init__(self) -> None:

        self._exporters: dict[str, Any] = {}



    def register(
        self,
        name: str,
        exporter: Any,
    ):
        """
        Register exporter.
        """

        if not isinstance(name, str):

            raise TypeError(
                "Exporter name must be string"
            )


        self._exporters[
            name.lower()
        ] = exporter


        return exporter



    def unregister(
        self,
        name: str,
    ):

        return self._exporters.pop(
            name.lower(),
            None,
        )



    def get(
        self,
        name: str,
    ):

        return self._exporters.get(
            name.lower()
        )



    def available(
        self,
    ) -> tuple[str, ...]:
        """
        Return exporter names.
        """

        return tuple(
            sorted(
                self._exporters.keys()
            )
        )



    def list(self):

        return list(
            self._exporters.values()
        )



    def clear(self):

        self._exporters.clear()



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return (
            name.lower()
            in self._exporters
        )



    def __len__(self):

        return len(
            self._exporters
        )



# ==========================================================
# Global Registry
# ==========================================================


default_registry = ExporterRegistry()



# ==========================================================
# Register Built-in Exporters
# ==========================================================


default_registry.register(
    "json",
    JSONExporter,
)


default_registry.register(
    "prometheus",
    PrometheusExporter,
)


default_registry.register(
    "opentelemetry",
    OpenTelemetryExporter,
)


default_registry.register(
    "otel",
    OpenTelemetryExporter,
)


default_registry.register(
    "jaeger",
    JaegerExporter,
)


default_registry.register(
    "zipkin",
    ZipkinExporter,
)


default_registry.register(
    "stdout",
    StdoutExporter,
)



# ==========================================================
# Factory
# ==========================================================


def create_exporter(
    name: str,
    **kwargs: Any,
):
    """
    Create exporter instance.
    """

    if not isinstance(
        name,
        str,
    ):
        raise TypeError(
            "Exporter name must be string"
        )


    exporter_cls = (
        default_registry.get(name)
    )


    if exporter_cls is None:

        raise ValueError(
            f"Unknown exporter: {name}"
        )


    try:

        return exporter_cls(
            **kwargs
        )

    except TypeError:

        # backward compatibility
        return exporter_cls()



# ==========================================================
# Public API
# ==========================================================


__all__ = [

    "BaseExporter",

    "ExportRecord",

    "ExportResult",

    "ExportStatus",

    "ExportFormat",


    "JSONExporter",

    "PrometheusExporter",

    "OpenTelemetryExporter",

    "JaegerExporter",

    "ZipkinExporter",

    "StdoutExporter",


    "ExporterRegistry",

    "default_registry",


    "create_exporter",

]