"""
SciOS-NG Prometheus Metrics Exporter
====================================

Prometheus compatible metrics exporter.

Responsibilities
-----------------
- Convert metrics snapshots into Prometheus exposition format.
- Export counters.
- Export gauges.
- Export histograms.
- Support labels.
- Serve monitoring systems.

Python 3.11+
"""

from __future__ import annotations


from typing import Any


from .exporter import (
    MetricExporter,
    ExportResult,
)



__all__ = [
    "PrometheusExporter",
]



# ==========================================================
# Prometheus Exporter
# ==========================================================


class PrometheusExporter(
    MetricExporter
):
    """
    Prometheus exposition exporter.

    Example
    -------

        exporter = PrometheusExporter()

        text = exporter.format(
            metrics
        )

    """



    def __init__(
        self,
        *,
        namespace: str = "scios",
        name: str = "prometheus",
    ):

        super().__init__(
            name=name
        )


        self.namespace = namespace


        self._last_payload = ""



    # ======================================================
    # Formatting Helpers
    # ======================================================


    def _metric_name(
        self,
        name: str,
    ) -> str:

        return (
            f"{self.namespace}_{name}"
            .replace(
                "-",
                "_",
            )
        )



    def _format_labels(
        self,
        labels: dict[str, Any] | None,
    ) -> str:

        if not labels:

            return ""


        values = []


        for key, value in labels.items():

            values.append(
                f'{key}="{value}"'
            )


        return (
            "{"
            +
            ",".join(values)
            +
            "}"
        )



    # ======================================================
    # Serialization
    # ======================================================


    def format(
        self,
        metrics: dict[str, Any],
    ) -> str:
        """
        Convert metrics snapshot into Prometheus text format.
        """

        lines: list[str] = []



        # --------------------------------------------------
        # Counters
        # --------------------------------------------------

        counters = [

            "total_tasks",

            "completed_tasks",

            "failed_tasks",

        ]


        for key in counters:

            if key in metrics:

                name = self._metric_name(
                    key
                )

                lines.append(
                    f"# TYPE {name} counter"
                )


                lines.append(
                    f"{name} {metrics[key]}"
                )



        # --------------------------------------------------
        # Rates
        # --------------------------------------------------

        for key in [

            "success_rate",

            "failure_rate",

        ]:

            if key in metrics:

                name = self._metric_name(
                    key
                )


                lines.append(
                    f"# TYPE {name} gauge"
                )


                lines.append(
                    f"{name} {metrics[key]}"
                )



        # --------------------------------------------------
        # Latency
        # --------------------------------------------------

        latency = metrics.get(
            "latency",
            {},
        )


        if isinstance(
            latency,
            dict,
        ):

            for key in [

                "average",

                "min",

                "max",

            ]:

                if key in latency:

                    name = self._metric_name(
                        f"latency_{key}"
                    )


                    lines.append(
                        f"# TYPE {name} gauge"
                    )


                    lines.append(
                        f"{name} {latency[key]}"
                    )



        # --------------------------------------------------
        # Throughput
        # --------------------------------------------------

        if "throughput" in metrics:

            name = self._metric_name(
                "throughput"
            )


            lines.append(
                f"# TYPE {name} gauge"
            )


            lines.append(
                f"{name} {metrics['throughput']}"
            )



        return "\n".join(
            lines
        )



    # ======================================================
    # Export
    # ======================================================


    def export(
        self,
        metrics: dict[str, Any],
    ) -> ExportResult:
        """
        Export metrics.

        """

        if not self.enabled:

            return self.create_result(

                error="Exporter disabled",

            )


        try:

            payload = self.format(
                metrics
            )


            self._last_payload = payload


            return self.create_result(

                records=len(metrics),

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
    ) -> str:
        """
        Return latest Prometheus payload.
        """

        return self._last_payload



    # ======================================================
    # Debug
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "PrometheusExporter("

            f"namespace={self.namespace!r}, "

            f"enabled={self.enabled}"

            ")"

        )