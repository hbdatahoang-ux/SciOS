"""
SciOS-NG Metrics Exporter Interface
===================================

Base exporter abstraction for metrics.

Responsibilities
-----------------
- Define exporter contract.
- Export metrics snapshots.
- Support multiple backends.
- Provide exporter lifecycle.

Supported exporters
-------------------
- JSON
- Prometheus
- OpenTelemetry

Python 3.11+
"""

from __future__ import annotations


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any



__all__ = [
    "ExportResult",
    "MetricExporter",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# Export Result
# ==========================================================


@dataclass
class ExportResult:
    """
    Result returned by exporters.
    """


    success: bool = True


    exporter: str = ""


    records: int = 0


    timestamp: str = field(
        default_factory=utc_now
    )


    error: str | None = None


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "success":
                self.success,

            "exporter":
                self.exporter,

            "records":
                self.records,

            "timestamp":
                self.timestamp,

            "error":
                self.error,

            "metadata":
                dict(
                    self.metadata
                ),
        }



# ==========================================================
# Exporter Interface
# ==========================================================


class MetricExporter(
    ABC
):
    """
    Abstract metrics exporter.

    Example
    -------

        class MyExporter(MetricExporter):

            def export(self, data):
                ...

    """



    def __init__(
        self,
        name: str | None = None,
    ):

        self.name = (
            name
            or self.__class__.__name__
        )


        self.enabled = True



    # ======================================================
    # Export
    # ======================================================


    @abstractmethod
    def export(
        self,
        metrics: dict[str, Any],
    ) -> ExportResult:
        """
        Export metrics snapshot.

        Must be implemented by backend.
        """

        raise NotImplementedError



    # ======================================================
    # Lifecycle
    # ======================================================


    def enable(
        self,
    ):

        self.enabled = True



    def disable(
        self,
    ):

        self.enabled = False



    def is_enabled(
        self,
    ) -> bool:

        return self.enabled



    # ======================================================
    # Helpers
    # ======================================================


    def create_result(
        self,
        *,
        records: int = 0,
        error: str | None = None,
        **metadata: Any,
    ) -> ExportResult:
        """
        Create standardized export result.
        """

        return ExportResult(

            success=(
                error is None
            ),

            exporter=self.name,

            records=records,

            error=error,

            metadata=metadata,
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "MetricExporter("
            f"name={self.name!r}, "
            f"enabled={self.enabled}"
            ")"
        )