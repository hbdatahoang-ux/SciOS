"""
SciOS-NG Runtime Metrics Prometheus Exporter

Prometheus exposition format exporter.

SciOS-NG v0.2
"""


from __future__ import annotations

from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# PrometheusExporter
# ==================================================================


class PrometheusExporter(
    MetricExporter
):
    """
    Runtime Prometheus Metrics Exporter.

    Responsibilities
    ----------------
    - Convert Runtime Metrics to Prometheus format
    - Maintain metric labels
    - Expose scrape-ready text
    - Integrate with monitoring systems
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "PrometheusExporter",
        description: str = "",
        namespace: str = "scios",
        subsystem: str = "runtime",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Prometheus Configuration
        # ----------------------------------------------------------

        self._namespace = namespace

        self._subsystem = subsystem



        # ----------------------------------------------------------
        # Metric Storage
        # ----------------------------------------------------------

        self._metrics: dict[str, dict[str, Any]] = {}



        self._labels: dict[str, dict[str, str]] = {}



        # ----------------------------------------------------------
        # Exposition Cache
        # ----------------------------------------------------------

        self._output = ""



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: dict[str, Any],
        **kwargs,
    ) -> str:
        """
        Export metrics into Prometheus exposition format.
        """

        with self._lock:

            self._ensure_enabled()


            labels = kwargs.get(
                "labels",
                {},
            )


            for name, value in metrics.items():

                self._metrics[name] = {

                    "value":
                        value,

                    "type":
                        kwargs.get(
                            "type",
                            "gauge",
                        ),

                    "help":
                        kwargs.get(
                            "help",
                            name,
                        ),

                }


                self._labels[name] = labels



            self._output = self.generate()



            self._exports += 1


            self._last_export = (
                datetime.utcnow()
            )


            self._touch()



        return self._output



    # ==============================================================
    # Prometheus Format
    # ==============================================================

    def generate(
        self,
    ) -> str:
        """
        Generate Prometheus text format.
        """

        lines = []



        for name, metric in self._metrics.items():


            metric_name = self._format_name(
                name
            )


            metric_type = metric[
                "type"
            ]


            help_text = metric[
                "help"
            ]


            value = metric[
                "value"
            ]



            lines.append(
                f"# HELP {metric_name} {help_text}"
            )


            lines.append(
                f"# TYPE {metric_name} {metric_type}"
            )



            label_text = self._format_labels(
                self._labels.get(
                    name,
                    {},
                )
            )


            lines.append(
                f"{metric_name}"
                f"{label_text} "
                f"{value}"
            )


        return "\n".join(
            lines
        )



    # ==============================================================
    # Metric Management
    # ==============================================================

    def register_metric(
        self,
        name: str,
        value: Any = 0,
        metric_type: str = "gauge",
        help_text: str | None = None,
    ):
        """
        Register Prometheus metric.
        """

        self._metrics[name] = {

            "value":
                value,

            "type":
                metric_type,

            "help":
                help_text
                or name,

        }


        return self



    def update_metric(
        self,
        name: str,
        value: Any,
    ):
        """
        Update metric value.
        """

        if name not in self._metrics:

            self.register_metric(
                name
            )


        self._metrics[name][
            "value"
        ] = value


        return self



    def remove_metric(
        self,
        name: str,
    ):
        """
        Remove metric.
        """

        self._metrics.pop(
            name,
            None,
        )


        self._labels.pop(
            name,
            None,
        )


        return self



    def metrics(
        self,
    ) -> dict[str, Any]:
        """
        Return metrics.
        """

        return self._metrics



    # ==============================================================
    # Labels
    # ==============================================================

    def set_labels(
        self,
        metric: str,
        labels: dict[str, str],
    ):
        """
        Assign metric labels.
        """

        self._labels[metric] = labels


        return self



    def _format_labels(
        self,
        labels: dict[str, str],
    ) -> str:
        """
        Convert labels to Prometheus syntax.
        """

        if not labels:

            return ""


        values = ",".join(

            f'{k}="{v}"'

            for k, v
            in labels.items()

        )


        return (
            "{"
            +
            values
            +
            "}"
        )



    def _format_name(
        self,
        name: str,
    ) -> str:
        """
        Build Prometheus metric name.
        """

        parts = [

            self._namespace,

            self._subsystem,

            name,

        ]


        return "_".join(
            parts
        )



    # ==============================================================
    # Endpoint Support
    # ==============================================================

    def scrape(
        self,
    ) -> str:
        """
        Return scrape endpoint output.
        """

        return self._output or self.generate()



    def clear(
        self,
    ):
        """
        Clear metrics.
        """

        with self._lock:

            self._metrics.clear()

            self._labels.clear()

            self._output = ""


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self._name,

            "namespace":
                self._namespace,

            "subsystem":
                self._subsystem,

            "metric_count":
                len(self._metrics),

            "exports":
                self._exports,

            "failures":
                self._failures,

            "last_export":
                self._last_export,

        }



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._metrics
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._metrics



    def __repr__(
        self,
    ) -> str:

        return (
            f"PrometheusExporter("
            f"metrics={len(self._metrics)}, "
            f"namespace={self._namespace!r}"
            f")"
        )