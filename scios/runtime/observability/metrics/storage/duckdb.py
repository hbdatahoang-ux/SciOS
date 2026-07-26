"""
SciOS-NG Runtime Metrics DuckDB Storage

Analytical OLAP metrics storage backend.

SciOS-NG v0.2
"""


from __future__ import annotations

import json

from pathlib import Path
from typing import Any


from .backend import MetricStorageBackend



# ==================================================================
# DuckDBStorage
# ==================================================================


class DuckDBStorage(
    MetricStorageBackend
):
    """
    Runtime DuckDB Analytics Storage.

    Responsibilities
    ----------------
    - Analytical metric storage
    - OLAP queries
    - Columnar analytics
    - Large-scale runtime observability analysis
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str = "metrics.duckdb",
        name: str = "DuckDBStorage",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Database
        # ----------------------------------------------------------

        self._path = Path(
            path
        )


        self._connection = None


        self._initialize()



    # ==============================================================
    # Initialization
    # ==============================================================

    def _initialize(
        self,
    ):

        try:

            import duckdb


            self._connection = duckdb.connect(
                str(
                    self._path
                )
            )


        except ImportError:

            raise RuntimeError(
                "DuckDB storage requires duckdb package"
            )



        self._connection.execute(

            """
            CREATE TABLE IF NOT EXISTS metrics (

                key VARCHAR,

                value JSON,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """

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



            self._connection.execute(

                """

                DELETE FROM metrics

                WHERE key = ?

                """,

                (
                    key,
                )

            )


            self._connection.execute(

                """

                INSERT INTO metrics
                (
                    key,
                    value
                )

                VALUES
                (
                    ?,
                    ?

                )

                """,

                (
                    key,
                    json.dumps(
                        value,
                        default=str,
                    ),
                )

            )


            self._writes += 1


            self._touch()



        return value



    def get(
        self,
        key: str,
    ):

        result = self._connection.execute(

            """

            SELECT value

            FROM metrics

            WHERE key = ?

            """,

            (
                key,
            )

        ).fetchone()



        self._reads += 1



        if result is None:

            return None



        return json.loads(
            result[0]
        )



    def delete(
        self,
        key: str,
    ):

        self._connection.execute(

            """

            DELETE FROM metrics

            WHERE key = ?

            """,

            (
                key,
            )

        )


        self._deletes += 1


        return self



    def exists(
        self,
        key: str,
    ) -> bool:

        result = self._connection.execute(

            """

            SELECT COUNT(*)

            FROM metrics

            WHERE key = ?

            """,

            (
                key,
            )

        ).fetchone()



        return result[0] > 0



    def clear(
        self,
    ):

        self._connection.execute(

            "DELETE FROM metrics"

        )


        return self



    # ==============================================================
    # Enumeration
    # ==============================================================

    def keys(
        self,
    ):

        result = self._connection.execute(

            """

            SELECT key

            FROM metrics

            """

        ).fetchall()



        return [

            row[0]

            for row
            in result

        ]



    def values(
        self,
    ):

        result = self._connection.execute(

            """

            SELECT value

            FROM metrics

            """

        ).fetchall()



        return [

            json.loads(
                row[0]
            )

            for row
            in result

        ]



    def items(
        self,
    ):

        result = self._connection.execute(

            """

            SELECT key,value

            FROM metrics

            """

        ).fetchall()



        return [

            (
                row[0],
                json.loads(
                    row[1]
                )
            )

            for row
            in result

        ]



    # ==============================================================
    # Analytical Query API
    # ==============================================================

    def query(
        self,
        sql: str,
    ):

        """
        Execute analytical SQL query.
        """

        return self._connection.execute(
            sql
        ).fetchall()



    def dataframe(
        self,
        sql: str = "SELECT * FROM metrics",
    ):

        """
        Return Pandas dataframe.
        """

        return self._connection.execute(
            sql
        ).df()



    def count(
        self,
    ):

        result = self._connection.execute(

            """

            SELECT COUNT(*)

            FROM metrics

            """

        ).fetchone()



        return result[0]



    # ==============================================================
    # Analytics Operations
    # ==============================================================

    def aggregate(
        self,
        field: str,
    ):

        return self._connection.execute(

            f"""

            SELECT

                {field},

                COUNT(*)

            FROM metrics

            GROUP BY {field}

            """

        ).fetchall()



    def optimize(
        self,
    ):

        self._connection.execute(
            "CHECKPOINT"
        )


        return self



    # ==============================================================
    # Lifecycle
    # ==============================================================

    def close(
        self,
    ):

        if self._connection:

            self._connection.close()


        return super().close()



    # ==============================================================
    # Statistics
    # ==============================================================

    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "backend":
                "duckdb",


            "path":
                str(
                    self._path
                ),


            "records":
                self.count(),


            "olap":
                True,

        })


        return data



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return self.count()



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

            f"DuckDBStorage("
            f"path={str(self._path)!r}, "
            f"records={self.count()}"
            f")"

        )