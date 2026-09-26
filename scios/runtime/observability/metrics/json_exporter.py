"""
SciOS-NG JSON Metrics Exporter
==============================

JSON exporter for runtime metrics.

Responsibilities
-----------------
- Convert metrics snapshot to JSON.
- Export metrics to string.
- Export metrics to file.
- Preserve exporter contract.

Python 3.11+
"""

from __future__ import annotations


import json

from pathlib import Path
from typing import Any


from .exporter import (
    MetricExporter,
    ExportResult,
)



__all__ = [
    "JSONMetricExporter",
]



# ==========================================================
# JSON Exporter
# ==========================================================


class JSONMetricExporter(
    MetricExporter
):
    """
    JSON metrics exporter.

    Example
    -------

        exporter = JSONMetricExporter()

        result = exporter.export(
            metrics
        )

    """



    def __init__(
        self,
        *,
        indent: int = 2,
        sort_keys: bool = True,
        name: str = "json",
    ):

        super().__init__(
            name=name
        )


        self.indent = indent

        self.sort_keys = sort_keys



    # ======================================================
    # Serialization
    # ======================================================


    def serialize(
        self,
        metrics: dict[str, Any],
    ) -> str:
        """
        Convert metrics snapshot to JSON string.
        """

        return json.dumps(

            metrics,

            indent=self.indent,

            sort_keys=self.sort_keys,

            default=str,

        )



    # ======================================================
    # Export
    # ======================================================


    def export(
        self,
        metrics: dict[str, Any],
    ) -> ExportResult:
        """
        Export metrics as JSON.

        Returns
        -------

        ExportResult

        """

        if not self.enabled:

            return self.create_result(

                records=0,

                error="Exporter disabled",

            )


        try:

            payload = self.serialize(
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
    # File Export
    # ======================================================


    def export_file(
        self,
        metrics: dict[str, Any],
        path: str | Path,
    ) -> ExportResult:
        """
        Write metrics snapshot to JSON file.
        """

        if not self.enabled:

            return self.create_result(

                error="Exporter disabled",

            )


        try:

            file_path = Path(
                path
            )


            file_path.parent.mkdir(

                parents=True,

                exist_ok=True,

            )


            file_path.write_text(

                self.serialize(
                    metrics
                ),

                encoding="utf-8",

            )


            return self.create_result(

                records=len(metrics),

                path=str(file_path),

            )


        except Exception as exc:

            return self.create_result(

                error=str(exc),

            )



    # ======================================================
    # State API
    # ======================================================


    @property
    def last_payload(
        self,
    ) -> str | None:
        """
        Latest exported JSON payload.
        """

        return getattr(
            self,
            "_last_payload",
            None,
        )



    # ======================================================
    # Debug
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "JSONMetricExporter("

            f"enabled={self.enabled}, "

            f"indent={self.indent}"

            ")"

        )