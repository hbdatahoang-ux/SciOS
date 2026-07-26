"""
SciOS-NG Runtime Metrics Storage Backend

Base storage contract for metrics persistence.

SciOS-NG v0.2
"""


from __future__ import annotations

import uuid
import threading

from datetime import datetime
from typing import Any



# ==================================================================
# MetricStorageBackend
# ==================================================================


class MetricStorageBackend:
    """
    Base Runtime Metrics Storage Backend.

    Responsibilities
    ----------------
    - Store runtime metrics
    - Provide persistence abstraction
    - Support multiple storage engines

    Implementations:

        MemoryStorage
        SQLiteStorage
        DuckDBStorage
        ParquetStorage
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "storage",
        description: str = "",
    ) -> None:


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id = str(
            uuid.uuid4()
        )

        self._name = name

        self._description = description



        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled = True

        self._closed = False



        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = threading.RLock()



        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        self._created_at = datetime.utcnow()

        self._updated_at = self._created_at

        self._version = "0.2"



        # ----------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------

        self._writes = 0

        self._reads = 0

        self._deletes = 0

        self._failures = 0



    # ==============================================================
    # Storage API
    # ==============================================================

    def put(
        self,
        key: str,
        value: Any,
    ):

        raise NotImplementedError



    def get(
        self,
        key: str,
    ):

        raise NotImplementedError



    def delete(
        self,
        key: str,
    ):

        raise NotImplementedError



    def exists(
        self,
        key: str,
    ) -> bool:

        raise NotImplementedError



    def clear(
        self,
    ):

        raise NotImplementedError



    def keys(
        self,
    ):

        raise NotImplementedError



    def values(
        self,
    ):

        raise NotImplementedError



    def items(
        self,
    ):

        raise NotImplementedError



    # ==============================================================
    # Batch API
    # ==============================================================

    def put_many(
        self,
        items: dict[str, Any],
    ):

        for key, value in items.items():

            self.put(
                key,
                value,
            )


        return self



    def get_many(
        self,
        keys: list[str],
    ):

        return {

            key:
                self.get(key)

            for key
            in keys

        }



    def delete_many(
        self,
        keys: list[str],
    ):

        for key in keys:

            self.delete(
                key
            )


        return self



    # ==============================================================
    # Lifecycle
    # ==============================================================

    def enable(
        self,
    ):

        self._enabled = True

        return self



    def disable(
        self,
    ):

        self._enabled = False

        return self



    def close(
        self,
    ):

        self._closed = True

        return self



    def reopen(
        self,
    ):

        self._closed = False

        return self



    # ==============================================================
    # Diagnostics
    # ==============================================================

    def statistics(
        self,
    ):

        return {

            "writes":
                self._writes,

            "reads":
                self._reads,

            "deletes":
                self._deletes,

            "failures":
                self._failures,

        }



    def status(
        self,
    ):

        return {

            "name":
                self._name,

            "enabled":
                self._enabled,

            "closed":
                self._closed,

            "active":
                self._enabled
                and
                not self._closed,

        }



    # ==============================================================
    # Internal
    # ==============================================================

    def _touch(
        self,
    ):

        self._updated_at = datetime.utcnow()



    def _ensure_active(
        self,
    ):

        if not self._enabled:

            raise RuntimeError(
                "Storage disabled"
            )


        if self._closed:

            raise RuntimeError(
                "Storage closed"
            )



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            list(
                self.keys()
            )
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

            f"MetricStorageBackend("
            f"name={self._name!r}"
            f")"

        )