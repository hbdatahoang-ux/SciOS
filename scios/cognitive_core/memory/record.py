# scios/cognitive_core/memory/record.py

import uuid
from typing import Any, Dict

class MemoryRecord:
    """
    MemoryRecord: cấu trúc dữ liệu chuẩn cho một ký ức.
    Dùng chung cho SemanticMemory, EpisodicMemory, và WorkingMemory.
    """

    def __init__(self, 
                 content: str, 
                 metadata: Dict[str, Any] = None, 
                 id: str = None):
        self.id = id or str(uuid.uuid4())   # Tạo ID duy nhất nếu chưa có
        self.content = content              # Nội dung ký ức (text, fact, event)
        self.metadata = metadata or {}      # Thông tin bổ sung (timestamp, context, tags)

    def __repr__(self) -> str:
        return f"<MemoryRecord id={self.id} content={self.content[:30]}...>"

    def to_dict(self) -> Dict[str, Any]:
        """Xuất record thành dict để dễ serialize."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """Khởi tạo record từ dict (ví dụ khi deserialize)."""
        return cls(
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            id=data.get("id")
        )
