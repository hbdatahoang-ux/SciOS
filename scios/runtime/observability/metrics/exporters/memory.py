"""
SciOS-NG Runtime Metrics Memory Exporter

In-memory metrics exporter.

SciOS-NG v0.2
"""


from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


from .exporter import MetricExporter



# ==================================================================
# MemoryExporter
# ==================================================================


class MemoryExporter(
    MetricExporter
):
    """
    Runtime Memory Metrics Exporter.

    Stores metrics inside process memory.

    Usage:
        - Runtime debugging
        - Testing
        - Short-lived observability
        - Internal pipelines
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MemoryExporter",
        description: str = "",
        max_size: int | None = None,
    ) -> None:

        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Memory Storage
        # ----------------------------------------------------------

        self._storage: list[dict[str, Any]] = []


        self._max_size = max_size



        # ----------------------------------------------------------
        # Index
        # ----------------------------------------------------------

        self._index: dict[str, list[int]] = {}



    # ==============================================================
    # Export API
    # ==============================================================

    def export(
        self,
        metrics: Any,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Store metrics in memory.
        """

        with self._lock:

            self._ensure_enabled()


            record = {

                "timestamp":
                    datetime.utcnow(),

                "metrics":
                    deepcopy(metrics),

                "metadata":
                    kwargs,

            }


            self._storage.append(
                record
            )


            self._exports += 1


            self._last_export = (
                record["timestamp"]
            )


            self._touch()



            if self._max_size:

                self._trim()



        return record



    # ==============================================================
    # Storage API
    # ==============================================================

    def get(
        self,
        index: int = -1,
    ) -> dict[str, Any] | None:
        """
        Get stored metric record.
        """

        if not self._storage:

            return None


        return self._storage[index]



    def get_all(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all metrics.
        """

        return deepcopy(
            self._storage
        )



    def latest(
        self,
    ) -> dict[str, Any] | None:
        """
        Return latest metrics.
        """

        return self.get(
            -1
        )



    def clear(
        self,
    ):
        """
        Clear memory storage.
        """

        with self._lock:

            self._storage.clear()

            self._index.clear()

            self._touch()


        return self



    def count(
        self,
    ) -> int:
        """
        Number of records.
        """

        return len(
            self._storage
        )



    # ==============================================================
    # Index API
    # ==============================================================

    def index(
        self,
        key: str,
    ):
        """
        Build index by metadata key.
        """

        values = []


        for idx, record in enumerate(
            self._storage
        ):

            if key in record["metadata"]:

                value = record["metadata"][key]


                if value not in self._index:

                    self._index[value] = []


                self._index[value].append(
                    idx
                )


                values.append(
                    value
                )


        return values



    # ==============================================================
    # Maintenance
    # ==============================================================

    def _trim(
        self,
    ):
        """
        Maintain max storage size.
        """

        if (
            self._max_size
            and
            len(self._storage)
            >
            self._max_size
        ):

            remove_count = (
                len(self._storage)
                -
                self._max_size
            )


            del self._storage[
                :remove_count
            ]



    def compact(
        self,
    ):
        """
        Compact empty records.
        """

        with self._lock:

            self._storage = [

                item

                for item
                in self._storage

                if item.get(
                    "metrics"
                )
                is not None

            ]


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Exporter summary.
        """

        return {

            "name":
                self._name,

            "records":
                self.count(),

            "exports":
                self._exports,

            "failures":
                self._failures,

            "last_export":
                self._last_export,

            "enabled":
                self._enabled,

        }



    # ==============================================================
    # Python Protocol
    # ==============================================================

    def __len__(
        self,
    ) -> int:

        return self.count()



    def __iter__(
        self,
    ):

        return iter(
            self._storage
        )



    def __contains__(
        self,
        item,
    ) -> bool:

        return item in self._storage



    def __repr__(
        self,
    ) -> str:

        return (
            f"MemoryExporter("
            f"records={self.count()}, "
            f"exports={self._exports}"
            f")"
        )