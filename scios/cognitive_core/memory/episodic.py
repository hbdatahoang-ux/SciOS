# scios/cognitive_core/memory/episodic.py

from typing import Any, Dict, Optional, List
from datetime import datetime
from .base import AbstractMemory
from .record import MemoryRecord

class EpisodicMemory(AbstractMemory):
    """
    EpisodicMemory: lưu giữ ký ức sự kiện, trải nghiệm cụ thể.
    Mỗi record thường có timestamp và context.
    """

    def __init__(self, name: str = "EpisodicMemory"):
        super().__init__(name)
        self._records: List[MemoryRecord] = []

    def store(self, record: Dict[str, Any]) -> None:
        """Thêm một sự kiện mới vào EpisodicMemory."""
        if "timestamp" not in record:
            record["timestamp"] = datetime.utcnow().isoformat()
        self._records.append(MemoryRecord(**record))

    def retrieve(self, query: Dict[str, Any]) -> Optional[MemoryRecord]:
        """
        Truy xuất ký ức theo query.
        Có thể tìm theo thời gian, ngữ cảnh hoặc keyword.
        """
        keyword = query.get("keyword")
        timestamp = query.get("timestamp")

        for rec in self._records:
            if keyword and keyword.lower() in rec.content.lower():
                return rec
            if timestamp and rec.metadata.get("timestamp") == timestamp:
                return rec
        return None

    def forget(self, record_id: str) -> None:
        """Xóa một ký ức sự kiện theo ID."""
        self._records = [rec for rec in self._records if rec.id != record_id
