"""
SciOS MUSES Memory Retriever

Unified interface for retrieving knowledge from memory systems.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .working import WorkingMemory
from .semantic import SemanticMemory
from .episodic import EpisodicMemory
from .longterm import LongTermMemory


class MemoryRetriever:
    """
    Unified memory retrieval layer.

    Responsibilities
    ----------------
    - Query working memory
    - Query semantic memory
    - Query episodic memory
    - Query long-term memory
    - Aggregate retrieval results
    """

    def __init__(
        self,
        working: WorkingMemory,
        semantic: SemanticMemory,
        episodic: EpisodicMemory,
        longterm: LongTermMemory,
    ):
        self.working = working
        self.semantic = semantic
        self.episodic = episodic
        self.longterm = longterm

    def retrieve_context(self) -> Dict[str, Any]:
        """
        Return current execution context.
        """

        return self.working.snapshot()

    def retrieve_semantic(
        self,
        concept: str,
    ):
        """
        Retrieve semantic knowledge.
        """

        return self.semantic.retrieve(concept)

    def search_semantic(
        self,
        keyword: str,
    ):
        """
        Search semantic memory.
        """

        return self.semantic.search(keyword)

    def recent_experiences(
        self,
        limit: int = 10,
    ):
        """
        Retrieve recent episodes.
        """

        return self.episodic.recent(limit)

    def search_longterm(
        self,
        collection: str,
        keyword: str,
    ):
        """
        Search long-term memory.
        """

        return self.longterm.search(
            collection,
            keyword,
        )

    def retrieve_all(
        self,
        keyword: str,
    ) -> Dict[str, Any]:
        """
        Search across all memories.
        """

        return {
            "working": self.working.snapshot(),
            "semantic": self.semantic.search(keyword),
            "episodic": self.episodic.search(keyword),
            "longterm": {
                name: self.longterm.search(name, keyword)
                for name in self.longterm.collections()
            },
        }

    def status(self):
        """
        Runtime status.
        """

        return {
            "component": "MemoryRetriever",
            "status": "ready",
        }