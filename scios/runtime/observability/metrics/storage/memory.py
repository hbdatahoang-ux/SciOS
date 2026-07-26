"""
SciOS-NG Runtime Metrics Memory Storage

In-memory metrics storage backend.

SciOS-NG v0.2
"""


from __future__ import annotations

from typing import Any


from .backend import MetricStorageBackend



# ==================================================================
# MemoryStorage
# ==================================================================


class MemoryStorage(
    MetricStorageBackend
):
    """
    Runtime In-Memory Metrics Storage.

    Responsibilities
    ----------------
    - Fast metric storage
    - Temporary runtime persistence
    - Cache-like metric access
    - Development/testing backend
    """



    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MemoryStorage",
        description: str = "",
    ) -> None:


        super().__init__(
            name=name,
            description=description,
        )


        # ----------------------------------------------------------
        # Storage
        # ----------------------------------------------------------

        self._store: dict[
            str,
            Any
        ] = {}



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


            self._store[key] = value


            self._writes += 1


            self._touch()



        return value



    def get(
        self,
        key: str,
    ):

        with self._lock:

            self._ensure_active()


            self._reads += 1


            return self._store.get(
                key
            )



    def delete(
        self,
        key: str,
    ):

        with self._lock:

            self._ensure_active()


            if key in self._store:

                del self._store[key]


                self._deletes += 1



            self._touch()



        return self



    def exists(
        self,
        key: str,
    ) -> bool:

        with self._lock:

            return key in self._store



    def clear(
        self,
    ):

        with self._lock:

            self._store.clear()


            self._touch()



        return self



    # ==============================================================
    # Enumeration
    # ==============================================================

    def keys(
        self,
    ):

        return list(
            self._store.keys()
        )



    def values(
        self,
    ):

        return list(
            self._store.values()
        )



    def items(
        self,
    ):

        return list(
            self._store.items()
        )



    # ==============================================================
    # Update API
    # ==============================================================

    def update(
        self,
        key: str,
        value: Any,
    ):

        return self.put(
            key,
            value,
        )



    def get_or_set(
        self,
        key: str,
        default: Any,
    ):

        if self.exists(
            key
        ):

            return self.get(
                key
            )


        return self.put(
            key,
            default,
        )



    # ==============================================================
    # Snapshot
    # ==============================================================

    def snapshot(
        self,
    ):

        return dict(
            self._store
        )



    def restore(
        self,
        snapshot: dict,
    ):

        self._store = dict(
            snapshot
        )


        return self



    # ==============================================================
    # Statistics
    # ==============================================================

    def size(
        self,
    ):

        return len(
            self._store
        )



    def statistics(
        self,
    ):

        data = super().statistics()


        data.update({

            "size":
                self.size(),

            "memory":
                True,

        })


        return data



    # ==============================================================
    # Runtime Operations
    # ==============================================================

    def compact(
        self,
    ):
        """
        Remove empty values.
        """

        with self._lock:

            self._store = {

                k: v

                for k, v
                in self._store.items()

                if v is not None

            }


        return self



    def cleanup(
        self,
    ):

        return self.clear()



    # ==============================================================
    # Python Protocols
    # ==============================================================

    def __len__(
        self,
    ):

        return len(
            self._store
        )



    def __iter__(
        self,
    ):

        return iter(
            self._store
        )



    def __getitem__(
        self,
        key,
    ):

        return self.get(
            key
        )



    def __setitem__(
        self,
        key,
        value,
    ):

        self.put(
            key,
            value
        )



    def __delitem__(
        self,
        key,
    ):

        self.delete(
            key
        )



    def __repr__(
        self,
    ):

        return (

            f"MemoryStorage("
            f"size={len(self._store)}"
            f")"

        )