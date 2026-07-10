# scios/cognitive_core/memory/semantic.py

from typing import Any, Dict, Optional, List
from .base import AbstractMemory
from .record import MemoryRecord

class SemanticMemory(AbstractMemory):
    """
    SemanticMemory: lưu trữ kiến thức khái quát (facts, concepts).
    Có thể triển khai bằng vector embeddings để hỗ trợ tìm kiếm ngữ nghĩa.
    """

    def __init__(self, name: str = "SemanticMemory"):
        super().__init__(name)
        self._records: List[MemoryRecord] = []

    def store(self, record: Dict[str, Any]) -> None:
        """Thêm một kiến thức mới vào SemanticMemory."""
        self._records.append(MemoryRecord(**record))

    def retrieve(self, query: Dict[str, Any]) -> Optional[MemoryRecord]:
        """
        Truy xuất kiến thức theo query.
        Ví dụ: tìm theo keyword hoặc similarity score.
        """
        keyword = query.get("keyword")
        if keyword:
            for rec in self._records:
                if keyword.lower() in rec.content.lower():
                    return rec
        return None

    def forget(self, record_id: str) -> None:
        """Xóa một kiến thức theo ID."""
        self._records = [rec for rec in self._records if rec.id != record_id]

    def all_records(self) -> List[MemoryRecord]:
        """Trả về toàn bộ kiến thức đã lưu."""
        return self._records
