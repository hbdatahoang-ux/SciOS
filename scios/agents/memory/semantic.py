"""
SciOS MUSES Semantic Memory

Long-term semantic memory for cognitive agents.
"""

from __future__ import annotations

from typing import Any, Dict, List


class SemanticMemory:
    """
    Long-term semantic memory.

    Responsibilities
    ----------------
    - Store semantic knowledge
    - Retrieve knowledge
    - Search concepts
    - Manage memory lifecycle
    """

    def __init__(self):
        self._memory: List[Dict[str, Any]] = []

    def store(
        self,
        concept: str,
        meaning: Any,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Store a semantic concept.
        """

        record = {
            "concept": concept,
            "meaning": meaning,
            "metadata": metadata or {},
        }

        self._memory.append(record)

        return record

    def retrieve(self, concept: str):
        """
        Retrieve a concept.
        """

        for item in self._memory:
            if item["concept"] == concept:
                return item

        return None

    def search(self, keyword: str):
        """
        Search concepts.
        """

        keyword = keyword.lower()

        return [
            item
            for item in self._memory
            if keyword in item["concept"].lower()
        ]

    def all(self):
        """
        Return all memory.
        """

        return list(self._memory)

    def clear(self):
        """
        Remove all memory.
        """

        self._memory.clear()

    def size(self) -> int:
        """
        Number of stored concepts.
        """

        return len(self._memory)

    def status(self):
        """
        Runtime status.
        """

        return {
            "component": "SemanticMemory",
            "concepts": self.size(),
        }