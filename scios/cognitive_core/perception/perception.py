# perception.py
# Perception Engine cho SciOS Cognitive Core

from .context import PerceptionContext
from .dispatcher import InputDispatcher
from .registry import InputRegistry
from .pipeline import PerceptionPipeline

class PerceptionEngine:
    """
    PerceptionEngine là entry point cho toàn bộ subsystem Perception.
    Nó nhận raw input từ thế giới bên ngoài, phân loại theo modality,
    chạy qua pipeline xử lý, và trả về PerceptionContext chuẩn hóa.
    """

    def __init__(self):
        self.registry = InputRegistry()
        self.dispatcher = InputDispatcher(self.registry)
        self.pipeline = PerceptionPipeline()

    def perceive(self, raw_input, modality: str, metadata: dict = None) -> PerceptionContext:
        """
        Nhận dữ liệu đầu vào và trả về PerceptionContext.

        Args:
            raw_input: dữ liệu thô (text, image, audio, video, document, sensor stream)
            modality: loại dữ liệu ("text", "image", "audio", "video", "document", "sensor")
            metadata: thông tin bổ sung (ngôn ngữ, timestamp, source, user context)

        Returns:
            PerceptionContext: object chuẩn hóa cho Cognitive Pipeline
        """
        # Bước 1: Dispatch input theo modality
        perceptor = self.dispatcher.dispatch(modality)

        # Bước 2: Chạy pipeline xử lý
        processed = self.pipeline.run(perceptor, raw_input, metadata)

        # Bước 3: Tạo PerceptionContext
        context = PerceptionContext(
            raw_input=raw_input,
            modality=modality,
            metadata=metadata or {},
            normalized_text=processed.get("text"),
            image_embeddings=processed.get("image_embeddings"),
            audio_embeddings=processed.get("audio_embeddings"),
            document_chunks=processed.get("document_chunks"),
            sensor_stream=processed.get("sensor_stream"),
            extracted_entities=processed.get("entities"),
            extracted_relations=processed.get("relations"),
            confidence=processed.get("confidence", 1.0)
        )

        return context
