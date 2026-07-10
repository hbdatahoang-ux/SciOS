# context.py
# CognitiveContext cho SciOS Cognitive Core

from typing import Any, Dict, List

class CognitiveContext:
    """
    CognitiveContext lưu giữ kết quả xử lý perception từ CognitivePipeline.
    Nó đóng vai trò như một container cho dữ liệu đã xử lý, embedding,
    entities, relations, và confidence score.
    """

    def __init__(self, modality: str, raw_input: Any, processed: Dict[str, Any]) -> None:
        self.modality = modality
        self.raw_input = raw_input
        self.processed = processed

        # Trích xuất các trường quan trọng
        self.text: str | None = processed.get("text")
        self.embedding: List[float] | None = processed.get("embedding")
        self.entities: List[Dict[str, Any]] = processed.get("entities", [])
        self.relations: List[Dict[str, Any]] = processed.get("relations", [])
        self.confidence: float = processed.get("confidence", 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """
        Trả về CognitiveContext dưới dạng dict.
        """
        return {
            "modality": self.modality,
            "raw_input": self.raw_input,
            "text": self.text,
            "embedding": self.embedding,
            "entities": self.entities,
            "relations": self.relations,
            "confidence": self.confidence,
            "processed": self.processed,
        }

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin tóm tắt về context.
        """
        return {
            "modality": self.modality,
            "text_preview": (self.text[:50] + "...") if self.text else None,
            "entities_count": len(self.entities),
            "relations_count": len(self.relations),
            "confidence": self.confidence,
        }
