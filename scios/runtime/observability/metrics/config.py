"""
SciOS Runtime Metrics Configuration
===================================

Configuration model for SciOS Metrics subsystem.

Responsibilities
-----------------
- Define default metrics settings.
- Control retention and sampling.
- Configure export behavior.
- Provide immutable runtime configuration.

Does NOT know about:
- ExecutionEngine
- TelemetryPlugin
- Exporters
- Storage backend

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Any


__all__ = [
    "MetricsConfig",
    "DEFAULT_METRICS_CONFIG",
]



# ==========================================================
# Constants
# ==========================================================


DEFAULT_NAMESPACE = "scios_runtime"


DEFAULT_RETENTION_LIMIT = 10000


DEFAULT_HISTORY_SIZE = 1000


DEFAULT_EXPORT_INTERVAL = 10.0


DEFAULT_ENABLE_LATENCY = True


DEFAULT_ENABLE_THROUGHPUT = True


DEFAULT_ENABLE_HISTOGRAM = True



# ==========================================================
# Metrics Configuration
# ==========================================================


@dataclass(slots=True)
class MetricsConfig:
    """
    Metrics runtime configuration.

    Example
    -------

    config = MetricsConfig(
        namespace="scios",
        retention_limit=5000,
    )

    """


    # ======================================================
    # Identity
    # ======================================================


    namespace: str = (
        DEFAULT_NAMESPACE
    )



    # ======================================================
    # Storage
    # ======================================================


    retention_limit: int = (
        DEFAULT_RETENTION_LIMIT
    )


    history_size: int = (
        DEFAULT_HISTORY_SIZE
    )



    # ======================================================
    # Collection
    # ======================================================


    enable_latency: bool = (
        DEFAULT_ENABLE_LATENCY
    )


    enable_throughput: bool = (
        DEFAULT_ENABLE_THROUGHPUT
    )


    enable_histogram: bool = (
        DEFAULT_ENABLE_HISTOGRAM
    )



    # ======================================================
    # Export
    # ======================================================


    export_interval: float = (
        DEFAULT_EXPORT_INTERVAL
    )


    exporters: list[str] = field(
        default_factory=lambda: [
            "json"
        ]
    )



    # ======================================================
    # Metadata
    # ======================================================


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ======================================================
    # Validation
    # ======================================================


    def __post_init__(self) -> None:
        """
        Validate configuration.
        """


        if self.retention_limit < 1:

            raise ValueError(
                "retention_limit must be >= 1"
            )


        if self.history_size < 1:

            raise ValueError(
                "history_size must be >= 1"
            )


        if self.export_interval <= 0:

            raise ValueError(
                "export_interval must be > 0"
            )


        self.exporters = list(
            self.exporters
        )



    # ======================================================
    # API
    # ======================================================


    def enable_exporter(
        self,
        name: str,
    ) -> None:
        """
        Add exporter.
        """


        if name not in self.exporters:

            self.exporters.append(
                name
            )



    def disable_exporter(
        self,
        name: str,
    ) -> None:
        """
        Remove exporter.
        """


        if name in self.exporters:

            self.exporters.remove(
                name
            )



    def to_dict(self) -> dict[str, Any]:
        """
        Serialize configuration.
        """


        return {

            "namespace":
                self.namespace,


            "retention_limit":
                self.retention_limit,


            "history_size":
                self.history_size,


            "enable_latency":
                self.enable_latency,


            "enable_throughput":
                self.enable_throughput,


            "enable_histogram":
                self.enable_histogram,


            "export_interval":
                self.export_interval,


            "exporters":
                list(self.exporters),


            "metadata":
                dict(self.metadata),
        }



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricsConfig":
        """
        Restore configuration.
        """


        return cls(

            namespace=data.get(
                "namespace",
                DEFAULT_NAMESPACE,
            ),


            retention_limit=data.get(
                "retention_limit",
                DEFAULT_RETENTION_LIMIT,
            ),


            history_size=data.get(
                "history_size",
                DEFAULT_HISTORY_SIZE,
            ),


            enable_latency=data.get(
                "enable_latency",
                True,
            ),


            enable_throughput=data.get(
                "enable_throughput",
                True,
            ),


            enable_histogram=data.get(
                "enable_histogram",
                True,
            ),


            export_interval=data.get(
                "export_interval",
                DEFAULT_EXPORT_INTERVAL,
            ),


            exporters=data.get(
                "exporters",
                ["json"],
            ),


            metadata=data.get(
                "metadata",
                {},
            ),
        )



    def copy(self) -> "MetricsConfig":
        """
        Clone configuration.
        """

        return MetricsConfig.from_dict(
            self.to_dict()
        )



# ==========================================================
# Default Instance
# ==========================================================


DEFAULT_METRICS_CONFIG = MetricsConfig()