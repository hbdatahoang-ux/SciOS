"""
SciOS-NG Runtime Metrics Parquet Storage

Columnar data lake storage backend.

SciOS-NG v0.2
"""


from __future__ import annotations

import json

from pathlib import Path
from typing import Any


from .backend import MetricStorageBackend



# ==================================================================
# ParquetStorage
# ==================================================================


class ParquetStorage(
    MetricStorageBackend
):
    """
    Runtime Parquet Data Lake Storage.

    Responsibilities
    ----------------
    - Long-term metric archival
    - Columnar analytics storage
    - Data lake integration
    - Batch metric persistence
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str = "metrics.parquet",
        name: str = "ParquetStorage",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Storage
        # ----------------------------------------------------------

        self._path = Path(
            path
        )


        self._records: list[dict] = []



    # ==============================================================
    # Dependency Check
    # ==============================================================

    def _require_engine(
        self,
    ):

        try:

            import pandas

            import pyarrow


        except ImportError:

            raise RuntimeError(

                "ParquetStorage requires "
                "pandas and pyarrow"

            )



    # ==============================================================
    # Storage API
    # ==============================================================

    def put(
        self,
        key: str,
        value: Any,
    ):

        with self._lock:

            self._ensure_active()


            record = {

                "key":
                    key,


                "value":
                    value,

            }


            self._records.append(
                record
            )


            self._writes += 1


            self._touch()



        return value



    def get(
        self,
        key: str,
    ):

        self._reads += 1



        for record in reversed(
            self._records
        ):

            if record["key"] == key:

                return record["value"]



        return None



    def delete(
        self,
        key: str,
    ):

        self._records = [

            r

            for r
            in self._records

            if r["key"] != key

        ]


        self._deletes += 1


        return self



    def exists(
        self,
        key: str,
    ) -> bool:

        return any(

            r["key"] == key

            for r
            in self._records

        )



    def clear(
        self,
    ):

        self._records.clear()


        return self



    # ==============================================================
    # Enumeration
    # ==============================================================

    def keys(
        self,
    ):

        return [

            r["key"]

            for r
            in self._records

        ]



    def values(
        self,
    ):

        return [

            r["value"]

            for r
            in self._records

        ]



    def items(
        self,
    ):

        return [

            (
                r["key"],
                r["value"]
            )

            for r
            in self._records

        ]



    # ==============================================================
    # Data Lake Operations
    # ==============================================================

    def write(
        self,
    ):

        """
        Write records to parquet file.
        """

        self._require_engine()


        import pandas as pd



        dataframe = pd.DataFrame(
            self._records
        )


        dataframe.to_parquet(
            self._path,
            index=False,
        )


        return self



    def load(
        self,
    ):

        """
        Load parquet dataset.
        """

        self._require_engine()


        import pandas as pd



        dataframe = pd.read_parquet(
            self._path
        )


        self._records = (

            dataframe
            .to_dict(
                orient="records"
            )

        )


        return self



    def append(
        self,
    ):

        """
        Append current records to parquet.
        """

        existing = []


        if self._path.exists():

            self.load()

            existing = self._records



        self._records.extend(
            existing
        )


        return self.write()



    # ==============================================================
    # Analytics
    # ==============================================================

    def dataframe(
        self,
    ):

        self._require_engine()


        import pandas as pd


        return pd.DataFrame(
            self._records
        )



    def count(
        self,
    ):

        return len(
            self._records
        )



    # ==============================================================
    # Snapshot
    # ==============================================================

    def snapshot(
        self,
    ):

        return list(
            self._records
        )



    def restore(
        self,
        snapshot,
    ):

        self._records = list(
            snapshot
        )


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "backend":
                "parquet",


            "path":
                str(
                    self._path
                ),


            "records":
                self.count(),


            "format":
                "columnar",

        })


        return data



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            self._records
        )



    def __iter__(
        self,
    ):

        return iter(
            self._records
        )



    def __contains__(
        self,
        key,
    ):

        return self.exists(
            key
        )



    def __repr__(
        self,
    ):

        return (

            f"ParquetStorage("
            f"path={str(self._path)!r}, "
            f"records={len(self._records)}"
            f")"

        )