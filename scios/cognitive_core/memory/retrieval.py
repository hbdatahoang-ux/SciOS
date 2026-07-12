"""
SciOS Cognitive Core Memory Retrieval
=====================================

Memory retrieval strategies.

Supported:
- Keyword retrieval
- Temporal retrieval
- Semantic retrieval

Design:
- Lightweight local retrieval.
- Vector backend replaceable.
- Compatible with future Qdrant integration.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any

from .record import MemoryRecord


__all__ = [
    "RetrievalStrategy",
    "KeywordRetrieval",
    "TemporalRetrieval",
    "SemanticRetrieval",
]


# ==========================================================
# Base Strategy
# ==========================================================


class RetrievalStrategy(ABC):
    """
    Base retrieval strategy.
    """

    @abstractmethod
    def retrieve(
        self,
        records: list[MemoryRecord],
        query: dict[str, Any],
    ) -> MemoryRecord | None:
        """
        Retrieve best matching memory.
        """

        raise NotImplementedError



# ==========================================================
# Keyword Retrieval
# ==========================================================


class KeywordRetrieval(
    RetrievalStrategy
):
    """
    Simple keyword based retrieval.
    """

    def retrieve(
        self,
        records: list[MemoryRecord],
        query: dict[str, Any],
    ) -> MemoryRecord | None:

        keyword = query.get(
            "keyword"
        )

        if not keyword:
            return None


        keyword = str(
            keyword
        ).lower()


        for record in records:

            content = str(
                record.content
            ).lower()


            if keyword in content:
                return record


        return None



# ==========================================================
# Temporal Retrieval
# ==========================================================


class TemporalRetrieval(
    RetrievalStrategy
):
    """
    Retrieve memory by timestamp.
    """

    def retrieve(
        self,
        records: list[MemoryRecord],
        query: dict[str, Any],
    ) -> MemoryRecord | None:


        timestamp = query.get(
            "timestamp"
        )

        if not timestamp:
            return None


        for record in records:

            if (
                record.metadata.get(
                    "timestamp"
                )
                ==
                timestamp
            ):
                return record


        return None



# ==========================================================
# Semantic Retrieval
# ==========================================================


class SemanticRetrieval(
    RetrievalStrategy
):
    """
    Embedding similarity retrieval.

    Current:
        Local cosine similarity.

    Future:
        Replace with:
        - Qdrant
        - FAISS
        - Vector DB
    """

    def retrieve(
        self,
        records: list[MemoryRecord],
        query: dict[str, Any],
    ) -> MemoryRecord | None:


        target_embedding = query.get(
            "embedding"
        )


        if not target_embedding:
            return None


        best_record = None

        best_score = -1.0


        for record in records:

            embedding = (
                record.metadata.get(
                    "embedding"
                )
            )


            if embedding is None:
                continue


            score = self._cosine_similarity(
                target_embedding,
                embedding,
            )


            if score > best_score:

                best_score = score

                best_record = record


        return best_record



    # ======================================================
    # Math
    # ======================================================

    @staticmethod
    def _cosine_similarity(
        vec1: list[float],
        vec2: list[float],
    ) -> float:
        """
        Compute cosine similarity.

        Returns:
            -1.0 ... 1.0
        """

        if not vec1 or not vec2:
            return 0.0


        if len(vec1) != len(vec2):
            return 0.0


        dot = sum(
            a * b
            for a, b in zip(
                vec1,
                vec2,
            )
        )


        norm1 = math.sqrt(
            sum(
                a * a
                for a in vec1
            )
        )


        norm2 = math.sqrt(
            sum(
                b * b
                for b in vec2
            )
        )


        if norm1 == 0 or norm2 == 0:
            return 0.0


        return dot / (
            norm1 * norm2
        )