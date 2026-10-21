"""
SciOS-NG Runtime Metrics InfluxDB Exporter

Time-series database exporter for InfluxDB.

SciOS-NG v0.2
"""


from __future__ import annotations

from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# InfluxDBExporter
# ==================================================================


class InfluxDBExporter(
    MetricExporter
):
    """
    Runtime InfluxDB Metrics Exporter.

    Responsibilities
    ----------------
    - Convert metrics into InfluxDB line protocol
    - Manage measurements, tags, fields
    - Support time-series storage
    - Bridge SciOS Runtime with TSDB
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "InfluxDBExporter",
        description: str = "",
        url: str | None = None,
        database: str = "scios",
        measurement: str = "runtime_metrics",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # InfluxDB Configuration
        # ----------------------------------------------------------

        self._url = url

        self._database = database

        self._measurement = measurement



        # ----------------------------------------------------------
        # Runtime Storage
        # ----------------------------------------------------------

        self._points: list[dict[str, Any]] = []


        self._tags: dict[str, str] = {}


        self._fields: dict[str, Any] = {}



        # ----------------------------------------------------------
        # Line Protocol Cache
        # ----------------------------------------------------------

        self._line_buffer: list[str] = []



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Export metrics as InfluxDB points.
        """

        with self._lock:

            self._ensure_enabled()


            timestamp = datetime.utcnow()


            point = {

                "measurement":
                    kwargs.get(
                        "measurement",
                        self._measurement,
                    ),


                "tags":
                    {
                        **self._tags,
                        **kwargs.get(
                            "tags",
                            {},
                        ),
                    },


                "fields":
                    metrics,


                "timestamp":
                    timestamp,

            }


            self._points.append(
                point
            )


            self._line_buffer.append(
                self.to_line_protocol(
                    point
                )
            )


            self._exports += 1


            self._last_export = timestamp


            self._touch()



        return point



    # ==============================================================
    # Line Protocol
    # ==============================================================

    def to_line_protocol(
        self,
        point: dict[str, Any],
    ) -> str:
        """
        Convert point to InfluxDB line protocol.
        """

        measurement = point[
            "measurement"
        ]


        tags = point.get(
            "tags",
            {},
        )


        fields = point.get(
            "fields",
            {},
        )


        timestamp = int(
            point[
                "timestamp"
            ].timestamp()
            *
            1_000_000_000
        )



        tag_text = ""

        if tags:

            tag_text = "," + ",".join(

                f"{k}={v}"

                for k, v
                in tags.items()

            )



        field_text = ",".join(

            f"{key}={self._format_field(value)}"

            for key, value
            in fields.items()

        )


        return (
            f"{measurement}"
            f"{tag_text} "
            f"{field_text} "
            f"{timestamp}"
        )



    def _format_field(
        self,
        value: Any,
    ) -> str:
        """
        Format InfluxDB field value.
        """

        if isinstance(
            value,
            str,
        ):

            return (
                f'"{value}"'
            )


        if isinstance(
            value,
            bool,
        ):

            return (
                "true"
                if value
                else
                "false"
            )


        return str(
            value
        )



    # ==============================================================
    # Point Management
    # ==============================================================

    def add_tag(
        self,
        key: str,
        value: str,
    ):
        """
        Add global tag.
        """

        self._tags[key] = value


        return self



    def remove_tag(
        self,
        key: str,
    ):
        """
        Remove global tag.
        """

        self._tags.pop(
            key,
            None,
        )


        return self



    def points(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return stored points.
        """

        return list(
            self._points
        )



    def line_protocol(
        self,
    ) -> str:
        """
        Return InfluxDB write payload.
        """

        return "\n".join(
            self._line_buffer
        )



    # ==============================================================
    # Database Operations
    # ==============================================================

    def write(
        self,
    ):
        """
        Write points to InfluxDB.

        Placeholder for:
            influxdb-client
            HTTP API
        """

        return self.line_protocol()



    def flush(
        self,
    ):
        """
        Flush buffered points.
        """

        with self._lock:

            self.write()

            self._line_buffer.clear()



        return self



    def clear(
        self,
    ):
        """
        Clear time-series buffer.
        """

        with self._lock:

            self._points.clear()

            self._line_buffer.clear()



        return self



    # ==============================================================
    # Query Helpers
    # ==============================================================

    def latest(
        self,
    ):
        """
        Latest point.
        """

        if not self._points:

            return None


        return self._points[-1]



    def count(
        self,
    ) -> int:
        """
        Number of points.
        """

        return len(
            self._points
        )



    # ==============================================================
    # Statistics
    # ==============================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self._name,


            "url":
                self._url,


            "database":
                self._database,


            "measurement":
                self._measurement,


            "points":
                self.count(),


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

        return self.count()



    def __iter__(
        self,
    ):

        return iter(
            self._points
        )



    def __contains__(
        self,
        item,
    ) -> bool:

        return item in self._points



    def __repr__(
        self,
    ) -> str:

        return (
            f"InfluxDBExporter("
            f"measurement={self._measurement!r}, "
            f"points={len(self._points)}"
            f")"
        )