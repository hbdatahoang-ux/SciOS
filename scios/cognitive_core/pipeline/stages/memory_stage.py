# memory_stage.py
# Memory Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class MemoryStage(BaseStage):
    """
    MemoryStage chịu trách nhiệm lưu trữ thông tin từ pipeline vào bộ nhớ.
    Nó có thể được dùng để ghi nhớ entities, context, hoặc metadata quan trọng.
    """

    def __init__(self, name: str = "memory_stage", memory_store: Dict[str, Any] | None = None) -> None:
        self.name = name
        # memory_store có thể là dict đơn giản hoặc một hệ thống memory phức tạp
        self.memory_store = memory_store if memory_store is not None else {}

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lưu trữ dữ liệu perception vào memory_store.
        """
        # Ví dụ: lưu entities và relations
        if "entities" in data:
            self.memory_store.setdefault("entities", []).extend(data["entities"])
        if "relations" in data:
            self.memory_store.setdefault("relations", []).extend(data["relations"])

        # Lưu confidence score
        if "confidence" in data:
            self.memory_store["last_confidence"] = data["confidence"]

        # Lưu toàn bộ processed context
        self.memory_store["last_context"] = data

        # Trả về dữ liệu không thay đổi để pipeline tiếp tục
        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage và trạng thái memory.
        """
        return {
            "stage": self.name,
            "stored_entities": len(self.memory_store.get("entities", [])),
            "stored_relations": len(self.memory_store.get("relations", [])),
            "last_confidence": self.memory_store.get("last_confidence"),
        }
