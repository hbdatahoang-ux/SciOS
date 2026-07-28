"""
SciOS Runtime Agent Memory
==========================

Agent memory abstraction layer.

Responsibilities
-----------------
- Store information
- Retrieve memories
- Search memories
- Maintain diagnostics
- Support snapshots

Architecture
------------

Agent
 |
Memory
 |
Storage


Python 3.11+
"""


from __future__ import annotations


from typing import (
    Any,
)


import copy



__all__ = [
    "Memory",
]



# ==========================================================
# Memory
# ==========================================================


class Memory:
    """
    Agent memory store.

    Supports:

    - key/value memory
    - episodic memory
    - retrieval
    - search
    - snapshot
    - diagnostics
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(
        self,
    ) -> None:


        self._storage: dict[str, Any] = {}


        self._writes = 0


        self._reads = 0



    # ======================================================
    # Write API
    # ======================================================


    def store(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store memory by key.
        """


        self._storage[key] = value


        self._writes += 1



    def add(
        self,
        value: Any,
    ) -> str:
        """
        Add anonymous memory.

        Returns generated key.
        """


        key = (
            f"memory-{len(self._storage)}"
        )


        self.store(
            key,
            value,
        )


        return key



    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Batch update memory.
        """


        for key, value in values.items():

            self.store(
                key,
                value,
            )



    # ======================================================
    # Read API
    # ======================================================


    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve memory.
        """


        self._reads += 1


        return self._storage.get(
            key,
            default,
        )



    def recall(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Alias for get().
        """


        return self.get(
            key,
            default,
        )



    def last(
        self,
    ) -> Any:
        """
        Return latest stored memory.

        Example
        -------

        memory.add("hello")

        memory.last()
        -> "hello"
        """


        if not self._storage:

            return None


        return list(
            self._storage.values()
        )[-1]



    def search(
        self,
        query: str,
    ) -> list[Any]:
        """
        Search memory values.

        Returns matched values.

        Example
        -------

        memory.add("python")
        memory.search("python")

        -> ["python"]

        Future:
            Vector DB / embedding retrieval
        """


        query = query.lower()


        return [

            value

            for key, value
            in self._storage.items()

            if (
                query in key.lower()
                or query in str(value).lower()
            )

        ]



    # ======================================================
    # Management
    # ======================================================


    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check memory existence.
        """


        return key in self._storage



    def remove(
        self,
        key: str,
    ) -> bool:
        """
        Remove memory.
        """


        if key not in self._storage:

            return False


        del self._storage[key]


        return True



    def clear(
        self,
    ) -> None:
        """
        Clear all memories.
        """


        self._storage.clear()



    # ======================================================
    # Collection API
    # ======================================================


    def keys(
        self,
    ) -> list[str]:

        return list(
            self._storage.keys()
        )



    def values(
        self,
    ) -> list[Any]:

        return list(
            self._storage.values()
        )



    def items(
        self,
    ) -> list[tuple[str, Any]]:

        return list(
            self._storage.items()
        )



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create memory checkpoint.
        """


        return copy.deepcopy(
            self._storage
        )



    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore memory checkpoint.
        """


        self._storage = copy.deepcopy(
            snapshot
        )



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return dict(
            self._storage
        )



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "size":
                len(
                    self._storage
                ),


            "keys":
                self.keys(),


            "writes":
                self._writes,


            "reads":
                self._reads,

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return len(
            self._storage
        )



    def __contains__(
        self,
        key: str,
    ) -> bool:

        return self.exists(
            key
        )



    def __iter__(
        self,
    ):

        return iter(
            self._storage
        )



    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self._storage[key]



    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.store(
            key,
            value,
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "Memory("
            f"size={len(self)}, "
            f"writes={self._writes}, "
            f"reads={self._reads}"
            ")"
        )