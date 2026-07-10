# context.py
# PerceptionContext cho SciOS Cognitive Core

from typing import Any, Dict, List, Optional

class PerceptionContext:
    """
    PerceptionContext là object duy nhất mà Cognitive Pipeline nhận được.
    Nó chuẩn hóa dữ liệu từ nhiều modality (text, image, audio, video, documents, sensors)
    thành một cấu trúc thống nhất.
    """

    def __init__(
        self,
        raw_input: Any,
        modality: str,
        metadata: Optional[Dict] = None,
        normalized_text: Optional[str] = None,
        image_embeddings: Optional[List[float]] = None,
        audio_embeddings: Optional[List[float]] = None,
        document_chunks: Optional[List[str]] = None,
        sensor_stream: Optional[Any] = None,
        extracted_entities: Optional[List[Dict]] = None,
        extracted_relations: Optional[List[Dict]] = None,
        confidence: float = 1.0,
    ):
        self.raw_input = raw_input
        self.modality = modality
        self.metadata = metadata or {}

        # Chuẩn hóa theo modality
        self.normalized_text = normalized_text
        self.image_embeddings = image_embeddings
        self.audio_embeddings = audio_embeddings
        self.document_chunks = document_chunks
        self.sensor_stream = sensor_stream

        # Thông tin trích xuất
        self.extracted_entities = extracted_entities or []
        self.extracted_relations = extracted_relations or []

        # Độ tin cậy của pipeline perception
        self.confidence = confidence

    def to_dict(self) -> Dict:
        """
        Xuất PerceptionContext thành dict để truyền qua Cognitive Pipeline.
        """
        return {
            "raw_input": self.raw_input,
            "modality": self.modality,
            "metadata": self.metadata,
            "normalized_text": self.normalized_text,
            "image_embeddings": self.image_embeddings,
            "audio_embeddings": self.audio_embeddings,
            "document_chunks": self.document_chunks,
            "sensor_stream": self.sensor_stream,
            "extracted_entities": self.extracted_entities,
            "extracted_relations": self.extracted_relations,
            "confidence": self.confidence,
        }

    def __repr__(self) -> str:
        return f"<PerceptionContext modality={self.modality} confidence={self.confidence}>"
