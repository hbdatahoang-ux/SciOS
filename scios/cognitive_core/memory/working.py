# scios/cognitive_core/memory/working.py

from typing import Any, Dict, Optional, List
from .base import AbstractMemory
from .record import MemoryRecord

class WorkingMemory(AbstractMemory):
    """
    WorkingMemory: bộ nhớ tạm thời để xử lý thông tin ngắn hạn.
    Thường dùng trong reasoning hoặc pipeline khi cần giữ dữ liệu tức thì.
    """

    def __init__(self, name: str = "WorkingMemory", capacity: int = 10):
        super().__init__(name)
        self.capacity = capacity
        self._records: List[MemoryRecord] = []

    def store(self, record: Dict[str, Any]) -> None:
        """Thêm một thông tin tạm thời vào WorkingMemory."""
        if len(self._records) >= self.capacity:
            # Nếu đầy, loại bỏ record cũ nhất (FIFO)
            self._records.pop(0)
        self._records.append(MemoryRecord(**record))

    def retrieve(self, query: Dict[str, Any]) -> Optional[MemoryRecord]:
        """
        Truy xuất thông tin tạm thời theo query.
        Ví dụ: tìm theo keyword hoặc ID.
        """
        keyword = query.get("keyword")
        record_id = query.get("id")

        for rec in self._records:
            if record_id and rec.id == record_id:
                return rec
            if keyword and keyword.lower() in rec.content.lower():
                return rec
        return None

    def forget(self, record_id: str) -> None:
        """Xóa một record tạm thời theo ID."""
        self._records = [rec for rec in self._records if rec.id != record_id]

    def all_records(self) -> List[MemoryRecord]:
        """Trả về toàn bộ thông tin tạm thời hiện có."""
        return self._records

    def clear(self) -> None:
        """Xóa toàn bộ WorkingMemory."""
        self._records.clear()
