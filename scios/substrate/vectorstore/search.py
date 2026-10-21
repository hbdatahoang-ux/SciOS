"""
SciOS Vector Search
===================

High-level vector search engine.

Responsibilities
----------------
- Query execution
- Candidate retrieval
- Metadata filtering
- Similarity ranking
- Search orchestration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scios.substrate.tensor import SciOSTensor

from .index import (
    SearchResult,
    VectorIndex,
)

from .metadata import Metadata
from .similarity import (
    Similarity,
    SimilarityMetric,
    get_metric,
)

from .storage import (
    VectorRecord,
    VectorStorage,
)

__all__ = [
    "SearchQuery",
    "SearchResponse",
    "VectorSearch",
]


# ==========================================================
# Query
# ==========================================================

@dataclass(slots=True)
class SearchQuery:
    """
    Vector search request.
    """

    vector: SciOSTensor

    k: int = 10

    metric: SimilarityMetric = SimilarityMetric.COSINE

    filters: dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Response
# ==========================================================

@dataclass(slots=True)
class SearchResponse:
    """
    Search result.
    """

    records: list[VectorRecord]

    metric: SimilarityMetric

    elapsed_ms: float = 0.0


# ==========================================================
# Vector Search
# ==========================================================

class VectorSearch:
    """
    High-level search engine.

    Coordinates Storage, Index and Similarity.
    """

    def __init__(
        self,
        storage: VectorStorage,
        index: VectorIndex,
    ) -> None:

        self.storage = storage

        self.index = index

    # ======================================================
    # Search
    # ======================================================

    def search(
        self,
        query: SearchQuery,
    ) -> SearchResponse:
        """
        Execute vector search.
        """

        candidates = self.index.search(
            query.vector,
            k=query.k,
        )

        results: list[VectorRecord] = []

        for candidate in candidates:

            record = self.storage.get(
                candidate.id
            )

            if record is None:
                continue

            if self._match_filters(
                record.metadata,
                query.filters,
            ):
                results.append(record)

        return SearchResponse(

            records=results,

            metric=query.metric,
        )

    # ======================================================
    # Metadata filtering
    # ======================================================

    @staticmethod
    def _match_filters(
        metadata: Metadata,
        filters: dict[str, Any],
    ) -> bool:

        if not filters:
            return True

        data = metadata.to_dict()

        for key, value in filters.items():

            if data.get(key) != value:

                return False

        return True

    # ======================================================
    # Python
    # ======================================================

    def __repr__(self) -> str:

        return (

            "VectorSearch("

            f"storage={self.storage.backend}, "

            f"index={self.index.index_type.value})"

        )
