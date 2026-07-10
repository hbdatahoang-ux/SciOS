# scios/cognitive_core/memory/memory_manager.py

from typing import Any, Dict, Optional
from .semantic import SemanticMemory
from .episodic import EpisodicMemory
from .working import WorkingMemory
from .record import MemoryRecord

class MemoryManager:
    """
    MemoryManager: điều phối các loại memory.
    Đóng vai trò như executive function, quyết định khi nào dùng Semantic, Episodic, hay WorkingMemory.
    """

    def __init__(self):
        self.semantic = SemanticMemory()
        self.episodic = EpisodicMemory()
        self.working = WorkingMemory()

    def store(self, record: Dict[str, Any], memory_type: str = "working") -> None:
        """Lưu record vào loại memory được chỉ định."""
        if memory_type == "semantic":
            self.semantic.store(record)
        elif memory_type == "episodic":
            self.episodic.store(record)
        elif memory_type == "working":
            self.working.store(record)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def retrieve(self, query: Dict[str, Any], memory_type: Optional[str] = None) -> Optional[MemoryRecord]:
        """
        Truy xuất record từ memory.
        Nếu memory_type = None, thử lần lượt Working → Episodic → Semantic.
        """
        if memory_type == "semantic":
            return self.semantic.retrieve(query)
        elif memory_type == "episodic":
            return self.episodic.retrieve(query)
        elif memory_type == "working":
            return self.working.retrieve(query)
        else:
            # fallback strategy
            result = self.working.retrieve(query)
            if result: return result
            result = self.episodic.retrieve(query)
            if result: return result
            return self.semantic.retrieve(query)

    def forget(self, record_id: str, memory_type: str) -> None:
        """Xóa record khỏi loại memory cụ thể."""
        if memory_type == "semantic":
            self.semantic.forget(record_id)
        elif memory_type == "episodic":
            self.episodic.forget(record_id)
        elif memory_type == "working":
            self.working.forget(record_id)

    def summary(self) -> Dict[str, int]:
        """Trả về số lượng record trong mỗi loại memory."""
        return {
            "semantic": len(self.semantic.all_records()),
            "episodic": len(self.episodic.all_records()),
            "working": len(self.working.all_records())
        }
