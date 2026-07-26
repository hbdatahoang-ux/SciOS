"""
SciOS-NG OpenTelemetry Metrics Exporter
=======================================

OpenTelemetry compatible metrics exporter.

Responsibilities
-----------------
- Convert SciOS metrics snapshots into OTEL format.
- Provide vendor-neutral telemetry output.
- Support future OTLP integration.
- Keep exporter independent from SDK.

Python 3.11+
"""

from __future__ import annotations


from datetime import datetime, timezone
from typing import Any


from .exporter import (
    MetricExporter,
    ExportResult,
)



__all__ = [
    "OpenTelemetryExporter",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_timestamp() -> str:
    """
    Current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# OpenTelemetry Exporter
# ==========================================================


class OpenTelemetryExporter(
    MetricExporter
):
    """
    OpenTelemetry metrics exporter.

    Produces OTEL compatible
    metric payload structure.

    Example
    -------

        exporter = OpenTelemetryExporter()

        payload = exporter.export_data(
            snapshot
        )

    """



    def __init__(
        self,
        *,
        service_name: str = "scios-runtime",
        name: str = "opentelemetry",
    ):

        super().__init__(
            name=name
        )


        self.service_name = service_name


        self._last_payload: dict[str, Any] = {}



    # ======================================================
    # Metric Conversion
    # ======================================================


    def _metric(
        self,
        name: str,
        value: Any,
        metric_type: str,
    ) -> dict[str, Any]:

        return {

            "name":
                name,


            "type":
                metric_type,


            "value":
                value,

        }



    def convert(
        self,
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert SciOS snapshot
        into OTEL style structure.
        """

        metrics = []



        # --------------------------------------------------
        # Counters
        # --------------------------------------------------

        for name in [

            "total_tasks",

            "completed_tasks",

            "failed_tasks",

        ]:

            if name in snapshot:

                metrics.append(

                    self._metric(

                        name=name,

                        value=snapshot[name],

                        metric_type="counter",

                    )

                )



        # --------------------------------------------------
        # Rates
        # --------------------------------------------------

        for name in [

            "success_rate",

            "failure_rate",

        ]:

            if name in snapshot:

                metrics.append(

                    self._metric(

                        name=name,

                        value=snapshot[name],

                        metric_type="gauge",

                    )

                )



        # --------------------------------------------------
        # Latency
        # --------------------------------------------------

        latency = snapshot.get(
            "latency",
            {},
        )


        if isinstance(
            latency,
            dict,
        ):

            for key, value in latency.items():

                if key in {

                    "average",

                    "min",

                    "max",

                }:

                    metrics.append(

                        self._metric(

                            name=f"latency_{key}",

                            value=value,

                            metric_type="gauge",

                        )

                    )



        # --------------------------------------------------
        # Throughput
        # --------------------------------------------------

        if "throughput" in snapshot:

            metrics.append(

                self._metric(

                    name="throughput",

                    value=snapshot["throughput"],

                    metric_type="gauge",

                )

            )



        return {

            "resource":

            {

                "service.name":

                    self.service_name,

            },


            "timestamp":

                utc_timestamp(),


            "metrics":

                metrics,

        }



    # ======================================================
    # Export
    # ======================================================


    def export(
        self,
        metrics: dict[str, Any],
    ) -> ExportResult:
        """
        Export metrics into OTEL payload.
        """

        if not self.enabled:

            return self.create_result(

                error="Exporter disabled",

            )


        try:

            payload = self.convert(
                metrics
            )


            self._last_payload = payload


            return self.create_result(

                records=len(
                    payload["metrics"]
                ),

            )


        except Exception as exc:

            return self.create_result(

                error=str(exc),

            )



    # ======================================================
    # Public API
    # ======================================================


    def payload(
        self,
    ) -> dict[str, Any]:
        """
        Latest OTEL payload.
        """

        return self._last_payload



    def to_otlp(
        self,
    ) -> dict[str, Any]:
        """
        Alias for OTLP compatibility.
        """

        return self._last_payload



    # ======================================================
    # Debug
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "OpenTelemetryExporter("

            f"service={self.service_name!r}, "

            f"enabled={self.enabled}"

            ")"

        )