from __future__ import annotations

from typing import Callable, Iterable

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


SimilarityFunction = Callable[[MemoryRecord, str], float]


class SemanticRetrieval(RetrievalStrategy):
    """Retrieve memory records using an injected semantic similarity function."""

    def __init__(
        self,
        name: str = "SemanticRetrieval",
        *,
        similarity: SimilarityFunction,
        threshold: float = 0.0,
    ) -> None:
        super().__init__(name=name)

        if not callable(similarity):
            raise TypeError("similarity must be callable")

        if isinstance(threshold, bool) or not isinstance(
            threshold,
            (int, float),
        ):
            raise TypeError("threshold must be a number")

        self.similarity = similarity
        self.threshold = float(threshold)

    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: str,
    ) -> tuple[MemoryRecord, ...]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            return ()

        return tuple(
            record
            for record in records
            if self.similarity(record, query) >= self.threshold
        )
