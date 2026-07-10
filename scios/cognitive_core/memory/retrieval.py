# scios/cognitive_core/memory/retrieval.py

from typing import List, Optional
from .record import MemoryRecord

class RetrievalStrategy:
    """
    Base class cho các chiến lược truy xuất memory.
    """

    def retrieve(self, records: List[MemoryRecord], query: dict) -> Optional[MemoryRecord]:
        raise NotImplementedError("Subclasses must implement retrieve()")


class KeywordRetrieval(RetrievalStrategy):
    """
    Truy xuất theo từ khóa (keyword match).
    """

    def retrieve(self, records: List[MemoryRecord], query: dict) -> Optional[MemoryRecord]:
        keyword = query.get("keyword")
        if not keyword:
            return None
        for rec in records:
            if keyword.lower() in rec.content.lower():
                return rec
        return None


class TemporalRetrieval(RetrievalStrategy):
    """
    Truy xuất theo thời gian (timestamp).
    """

    def retrieve(self, records: List[MemoryRecord], query: dict) -> Optional[MemoryRecord]:
        timestamp = query.get("timestamp")
        if not timestamp:
            return None
        for rec in records:
            if rec.metadata.get("timestamp") == timestamp:
                return rec
        return None


class SemanticRetrieval(RetrievalStrategy):
    """
    Truy xuất theo độ tương đồng ngữ nghĩa (embedding similarity).
    (Ở đây skeleton, chưa triển khai thực tế embedding).
    """

    def retrieve(self, records: List[MemoryRecord], query: dict) -> Optional[MemoryRecord]:
        # Giả định có trường "embedding" trong metadata
        target_embedding = query.get("embedding")
        if not target_embedding:
            return None

        # TODO: triển khai tính cosine similarity
        # Hiện tại chỉ skeleton
        best_match = None
        best_score = -1
        for rec in records:
            embedding = rec.metadata.get("embedding")
            if embedding:
                score = self._cosine_similarity(target_embedding, embedding)
                if score > best_score:
                    best_score = score
                    best_match = rec
        return best_match

    def _cosine_similarity
