"""
SciOS MUSES Long-Term Memory

Persistent memory layer for cognitive knowledge.
"""

from __future__ import annotations

from typing import Any, Dict, List


class LongTermMemory:
    """
    Long-term memory.

    Responsibilities
    ----------------
    - Persist semantic knowledge
    - Persist episodic experiences
    - Organize memory collections
    - Provide unified retrieval API
    """

    def __init__(self):
        self._collections: Dict[str, List[Dict[str, Any]]] = {
            "semantic": [],
            "episodic": [],
            "procedural": [],
        }

    def store(
        self,
        collection: str,
        item: Dict[str, Any],
    ) -> None:
        """
        Store an item in a collection.
        """

        if collection not in self._collections:
            self._collections[collection] = []

        self._collections[collection].append(item)

    def retrieve(
        self,
        collection: str,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve an entire collection.
        """

        return list(
            self._collections.get(collection, [])
        )

    def search(
        self,
        collection: str,
        keyword: str,
    ):
        """
        Search a collection.
        """

        keyword = keyword.lower()

        results = []

        for item in self._collections.get(collection, []):

            if keyword in str(item).lower():
                results.append(item)

        return results

    def collections(self):
        """
        Available collections.
        """

        return sorted(self._collections.keys())

    def clear(
        self,
        collection: str | None = None,
    ):
        """
        Clear one or all collections.
        """

        if collection is None:

            for name in self._collections:
                self._collections[name].clear()

            return

        if collection in self._collections:
            self._collections[collection].clear()

    def statistics(self):
        """
        Memory statistics.
        """

        return {
            name: len(items)
            for name, items in self._collections.items()
        }

    def status(self):
        """
        Runtime status.
        """

        return {
            "component": "LongTermMemory",
            "collections": self.statistics(),
        }