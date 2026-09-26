"""
SciOS-NG Runtime Metrics CSV Exporter

Tabular CSV exporter for Runtime Metrics.

SciOS-NG v0.2
"""


from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# CSVExporter
# ==================================================================


class CSVExporter(
    MetricExporter
):
    """
    Runtime CSV Metrics Exporter.

    Responsibilities
    ----------------
    - Export metrics into CSV format
    - Support analytics workflows
    - Provide tabular runtime observability
    - Integrate with data processing tools
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str | None = None,
        name: str = "CSVExporter",
        description: str = "",
        delimiter: str = ",",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Storage Configuration
        # ----------------------------------------------------------

        self._path = (

            Path(path)

            if path

            else None

        )


        self._delimiter = delimiter



        # ----------------------------------------------------------
        # Runtime Buffer
        # ----------------------------------------------------------

        self._rows: list[dict[str, Any]] = []


        self._columns: list[str] = []



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Export metrics into tabular row.
        """

        with self._lock:

            self._ensure_enabled()



            row = {

                "timestamp":
                    datetime.utcnow().isoformat(),

                **metrics,

                **kwargs,

            }



            self._rows.append(
                row
            )


            self._update_columns(
                row
            )


            self._exports += 1


            self._last_export = (
                datetime.utcnow()
            )


            self._touch()



            if self._path:

                self._write()



        return row



    # ==============================================================
    # CSV File Operations
    # ==============================================================

    def _write(
        self,
    ):
        """
        Write rows to CSV file.
        """

        if self._path is None:

            return



        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )



        with open(
            self._path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:


            writer = csv.DictWriter(
                file,
                fieldnames=self._columns,
                delimiter=self._delimiter,
            )


            writer.writeheader()


            writer.writerows(
                self._rows
            )



    def read(
        self,
    ) -> list[dict[str, Any]]:
        """
        Read CSV file.
        """

        if (
            self._path is None
            or
            not self._path.exists()
        ):

            return []



        with open(
            self._path,
            "r",
            encoding="utf-8",
        ) as file:


            reader = csv.DictReader(
                file,
                delimiter=self._delimiter,
            )


            return list(
                reader
            )



    def flush(
        self,
    ):
        """
        Flush CSV buffer.
        """

        with self._lock:

            self._write()


        return self



    # ==============================================================
    # Row Management
    # ==============================================================

    def rows(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all rows.
        """

        return list(
            self._rows
        )



    def latest(
        self,
    ):
        """
        Return latest row.
        """

        if not self._rows:

            return None


        return self._rows[-1]



    def count(
        self,
    ) -> int:
        """
        Number of rows.
        """

        return len(
            self._rows
        )



    def columns(
        self,
    ) -> list[str]:
        """
        Return CSV columns.
        """

        return list(
            self._columns
        )



    def _update_columns(
        self,
        row: dict[str, Any],
    ):
        """
        Update dynamic columns.
        """

        for key in row.keys():

            if key not in self._columns:

                self._columns.append(
                    key
                )



    # ==============================================================
    # Data Operations
    # ==============================================================

    def clear(
        self,
    ):
        """
        Clear CSV data.
        """

        with self._lock:

            self._rows.clear()

            self._columns.clear()



        return self



    def compact(
        self,
    ):
        """
        Remove empty rows.
        """

        with self._lock:

            self._rows = [

                row

                for row
                in self._rows

                if row

            ]



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


            "path":
                str(
                    self._path
                )
                if self._path
                else None,


            "rows":
                self.count(),


            "columns":
                len(
                    self._columns
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

        return self.count()



    def __iter__(
        self,
    ):

        return iter(
            self._rows
        )



    def __contains__(
        self,
        item,
    ) -> bool:

        return item in self._rows



    def __repr__(
        self,
    ) -> str:

        return (
            f"CSVExporter("
            f"rows={self.count()}, "
            f"columns={len(self._columns)}"
            f")"
        )