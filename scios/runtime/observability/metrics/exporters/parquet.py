"""
SciOS-NG Runtime Metrics Parquet Exporter

Analytics / Data Lake exporter for Runtime Metrics.

SciOS-NG v0.2
"""


from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# ParquetExporter
# ==================================================================


class ParquetExporter(
    MetricExporter
):
    """
    Runtime Parquet Metrics Exporter.

    Responsibilities
    ----------------
    - Export metrics into columnar Parquet format
    - Support analytics workloads
    - Enable data lake storage
    - Integrate with Spark / Arrow / Pandas ecosystem
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str | None = None,
        name: str = "ParquetExporter",
        description: str = "",
        compression: str = "snappy",
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


        self._compression = compression



        # ----------------------------------------------------------
        # Runtime Buffer
        # ----------------------------------------------------------

        self._rows: list[dict[str, Any]] = []


        self._schema: list[str] = []



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._write_count = 0



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Export metrics into parquet row.
        """

        with self._lock:

            self._ensure_enabled()



            row = {

                "timestamp":
                    datetime.utcnow(),

                **metrics,

                **kwargs,

            }



            self._rows.append(
                row
            )


            self._update_schema(
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
    # Parquet Operations
    # ==============================================================

    def _write(
        self,
    ):
        """
        Write data into parquet file.

        Uses:
            pyarrow
            pandas
        """

        if self._path is None:

            return



        try:

            import pandas as pd


            dataframe = pd.DataFrame(
                self._rows
            )


            self._path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )


            dataframe.to_parquet(
                self._path,
                compression=self._compression,
            )


            self._write_count += 1



        except ImportError:

            raise RuntimeError(
                "Parquet export requires pandas and pyarrow."
            )



    def read(
        self,
    ):
        """
        Read parquet dataset.
        """

        if (
            self._path is None
            or
            not self._path.exists()
        ):

            return []



        try:

            import pandas as pd


            dataframe = pd.read_parquet(
                self._path
            )


            return dataframe.to_dict(
                orient="records"
            )



        except ImportError:

            raise RuntimeError(
                "Parquet read requires pandas and pyarrow."
            )



    def flush(
        self,
    ):
        """
        Flush parquet buffer.
        """

        with self._lock:

            self._write()


        return self



    # ==============================================================
    # Data Lake Features
    # ==============================================================

    def append(
        self,
        metrics: dict[str, Any],
    ):
        """
        Append analytics record.
        """

        return self.export(
            metrics
        )



    def batch_export(
        self,
        rows: list[dict[str, Any]],
    ):
        """
        Export batch metrics.
        """

        with self._lock:

            for row in rows:

                self.export(
                    row
                )


        return self



    def partition(
        self,
        key: str,
    ) -> dict[Any, list[dict]]:
        """
        Create logical partitions.

        Example:
            node_id
            date
            service
        """

        partitions = {}



        for row in self._rows:

            value = row.get(
                key,
                "unknown",
            )


            if value not in partitions:

                partitions[value] = []


            partitions[value].append(
                row
            )



        return partitions



    # ==============================================================
    # Schema Management
    # ==============================================================

    def schema(
        self,
    ) -> list[str]:
        """
        Return parquet schema.
        """

        return list(
            self._schema
        )



    def _update_schema(
        self,
        row: dict[str, Any],
    ):
        """
        Update dynamic schema.
        """

        for key in row.keys():

            if key not in self._schema:

                self._schema.append(
                    key
                )



    # ==============================================================
    # Runtime Management
    # ==============================================================

    def rows(
        self,
    ):
        """
        Return buffered rows.
        """

        return list(
            self._rows
        )



    def count(
        self,
    ):
        """
        Number of records.
        """

        return len(
            self._rows
        )



    def clear(
        self,
    ):
        """
        Clear parquet buffer.
        """

        with self._lock:

            self._rows.clear()

            self._schema.clear()



        return self



    def compact(
        self,
    ):
        """
        Remove invalid rows.
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


            "records":
                self.count(),


            "schema_size":
                len(
                    self._schema
                ),


            "compression":
                self._compression,


            "writes":
                self._write_count,


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
            f"ParquetExporter("
            f"records={self.count()}, "
            f"compression={self._compression!r}"
            f")"
        )