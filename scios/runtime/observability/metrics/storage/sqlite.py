"""
SciOS-NG Runtime Metrics SQLite Storage

SQLite persistent metrics storage backend.

SciOS-NG v0.2
"""


from __future__ import annotations

import sqlite3
import json

from pathlib import Path
from typing import Any


from .backend import MetricStorageBackend



# ==================================================================
# SQLiteStorage
# ==================================================================


class SQLiteStorage(
    MetricStorageBackend
):
    """
    Runtime SQLite Metrics Storage.

    Responsibilities
    ----------------
    - Persistent local metric storage
    - Structured key/value persistence
    - Lightweight database backend
    - Runtime analytics support
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        path: str = "metrics.db",
        name: str = "SQLiteStorage",
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


        self._connection = sqlite3.connect(
            self._path,
            check_same_thread=False,
        )


        self._initialize()



    # ==============================================================
    # Initialization
    # ==============================================================

    def _initialize(
        self,
    ):

        cursor = self._connection.cursor()


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (

                key TEXT PRIMARY KEY,

                value TEXT,

                created_at TEXT,

                updated_at TEXT

            )
            """
        )


        self._connection.commit()



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


            cursor = self._connection.cursor()


            payload = json.dumps(
                value,
                default=str,
            )


            cursor.execute(

                """
                INSERT INTO metrics
                (
                    key,
                    value,
                    created_at,
                    updated_at
                )

                VALUES
                (
                    ?,
                    ?,
                    datetime('now'),
                    datetime('now')
                )

                ON CONFLICT(key)

                DO UPDATE SET

                    value=excluded.value,

                    updated_at=datetime('now')

                """,

                (
                    key,
                    payload,
                )

            )


            self._connection.commit()


            self._writes += 1


            self._touch()



        return value



    def get(
        self,
        key: str,
    ):

        with self._lock:

            self._ensure_active()


            cursor = self._connection.cursor()


            cursor.execute(

                """
                SELECT value
                FROM metrics
                WHERE key=?

                """,

                (
                    key,
                )

            )


            row = cursor.fetchone()


            self._reads += 1



            if row is None:

                return None



            return json.loads(
                row[0]
            )



    def delete(
        self,
        key: str,
    ):

        with self._lock:

            self._ensure_active()


            cursor = self._connection.cursor()


            cursor.execute(

                """
                DELETE FROM metrics
                WHERE key=?

                """,

                (
                    key,
                )

            )


            self._connection.commit()


            self._deletes += 1



        return self



    def exists(
        self,
        key: str,
    ) -> bool:

        cursor = self._connection.cursor()


        cursor.execute(

            """
            SELECT 1
            FROM metrics
            WHERE key=?

            """,

            (
                key,
            )

        )


        return cursor.fetchone() is not None



    def clear(
        self,
    ):

        with self._lock:

            cursor = self._connection.cursor()


            cursor.execute(
                "DELETE FROM metrics"
            )


            self._connection.commit()



        return self



    # ==============================================================
    # Enumeration
    # ==============================================================

    def keys(
        self,
    ):

        cursor = self._connection.cursor()


        cursor.execute(
            "SELECT key FROM metrics"
        )


        return [

            row[0]

            for row
            in cursor.fetchall()

        ]



    def values(
        self,
    ):

        cursor = self._connection.cursor()


        cursor.execute(
            "SELECT value FROM metrics"
        )


        return [

            json.loads(row[0])

            for row
            in cursor.fetchall()

        ]



    def items(
        self,
    ):

        cursor = self._connection.cursor()


        cursor.execute(

            """
            SELECT key,value
            FROM metrics

            """

        )


        return [

            (
                row[0],
                json.loads(row[1])
            )

            for row
            in cursor.fetchall()

        ]



    # ==============================================================
    # Query API
    # ==============================================================

    def count(
        self,
    ):

        cursor = self._connection.cursor()


        cursor.execute(
            "SELECT COUNT(*) FROM metrics"
        )


        return cursor.fetchone()[0]



    def search(
        self,
        pattern: str,
    ):

        cursor = self._connection.cursor()


        cursor.execute(

            """
            SELECT key,value
            FROM metrics
            WHERE key LIKE ?

            """,

            (
                f"%{pattern}%",
            )

        )


        return [

            (
                row[0],
                json.loads(row[1])
            )

            for row
            in cursor.fetchall()

        ]



    # ==============================================================
    # Maintenance
    # ==============================================================

    def vacuum(
        self,
    ):

        self._connection.execute(
            "VACUUM"
        )


        return self



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
                "sqlite",


            "path":
                str(
                    self._path
                ),


            "records":
                self.count(),

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

            f"SQLiteStorage("
            f"path={str(self._path)!r}, "
            f"records={self.count()}"
            f")"

        )