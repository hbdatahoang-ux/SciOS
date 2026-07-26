"""
SciOS-NG Runtime Metrics OpenTelemetry Exporter

OpenTelemetry compatible metrics exporter.

SciOS-NG v0.2
"""


from __future__ import annotations

from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# OpenTelemetryExporter
# ==================================================================


class OpenTelemetryExporter(
    MetricExporter
):
    """
    Runtime OpenTelemetry Metrics Exporter.

    Responsibilities
    ----------------
    - Export metrics using OpenTelemetry model
    - Maintain resource attributes
    - Support tracing context
    - Bridge SciOS metrics with OTel ecosystem
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "OpenTelemetryExporter",
        description: str = "",
        service_name: str = "scios-runtime",
        endpoint: str | None = None,
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # OpenTelemetry Configuration
        # ----------------------------------------------------------

        self._service_name = service_name

        self._endpoint = endpoint



        # ----------------------------------------------------------
        # OTel Runtime Storage
        # ----------------------------------------------------------

        self._records: list[dict[str, Any]] = []



        self._resource: dict[str, Any] = {

            "service.name":
                service_name,

            "telemetry.sdk.name":
                "scios",

        }



        self._attributes: dict[str, Any] = {}



        # ----------------------------------------------------------
        # Instrument Cache
        # ----------------------------------------------------------

        self._instruments: dict[str, dict[str, Any]] = {}



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Export metrics using OpenTelemetry format.
        """

        with self._lock:

            self._ensure_enabled()


            timestamp = datetime.utcnow()



            record = {

                "timestamp":
                    timestamp.isoformat(),


                "resource":
                    self._resource.copy(),


                "attributes":
                    {
                        **self._attributes,
                        **kwargs.get(
                            "attributes",
                            {},
                        ),
                    },


                "metrics":
                    metrics,

            }



            self._records.append(
                record
            )


            self._exports += 1


            self._last_export = timestamp


            self._touch()



        return record



    # ==============================================================
    # Instrument Management
    # ==============================================================

    def create_counter(
        self,
        name: str,
        description: str = "",
    ):
        """
        Create OTel counter instrument.
        """

        self._instruments[name] = {

            "type":
                "counter",

            "description":
                description,

            "value":
                0,

        }


        return self



    def create_gauge(
        self,
        name: str,
        description: str = "",
    ):
        """
        Create OTel gauge instrument.
        """

        self._instruments[name] = {

            "type":
                "gauge",

            "description":
                description,

            "value":
                0,

        }


        return self



    def update_instrument(
        self,
        name: str,
        value: Any,
    ):
        """
        Update instrument value.
        """

        if name not in self._instruments:

            self.create_gauge(
                name
            )


        self._instruments[name][
            "value"
        ] = value


        return self



    def remove_instrument(
        self,
        name: str,
    ):
        """
        Remove instrument.
        """

        self._instruments.pop(
            name,
            None,
        )


        return self



    # ==============================================================
    # Resource Attributes
    # ==============================================================

    def set_resource(
        self,
        key: str,
        value: Any,
    ):
        """
        Set OpenTelemetry resource attribute.
        """

        self._resource[key] = value


        return self



    def set_attribute(
        self,
        key: str,
        value: Any,
    ):
        """
        Set metric attribute.
        """

        self._attributes[key] = value


        return self



    def resource(
        self,
    ):
        """
        Return resource metadata.
        """

        return self._resource



    def attributes(
        self,
    ):
        """
        Return attributes.
        """

        return self._attributes



    # ==============================================================
    # Runtime Access
    # ==============================================================

    def records(
        self,
    ):
        """
        Return exported records.
        """

        return list(
            self._records
        )



    def latest(
        self,
    ):
        """
        Return latest record.
        """

        if not self._records:

            return None


        return self._records[-1]



    def clear(
        self,
    ):
        """
        Clear exported records.
        """

        with self._lock:

            self._records.clear()

            self._instruments.clear()


        return self



    # ==============================================================
    # Flush
    # ==============================================================

    def flush(
        self,
    ):
        """
        Flush metrics.

        Placeholder for:
            OTLP HTTP
            OTLP gRPC
            Collector
        """

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


            "service":
                self._service_name,


            "endpoint":
                self._endpoint,


            "records":
                len(
                    self._records
                ),


            "instruments":
                len(
                    self._instruments
                ),


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
            self._records
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._instruments



    def __iter__(
        self,
    ):

        return iter(
            self._records
        )



    def __repr__(
        self,
    ) -> str:

        return (
            f"OpenTelemetryExporter("
            f"service={self._service_name!r}, "
            f"records={len(self._records)}"
            f")"
        )