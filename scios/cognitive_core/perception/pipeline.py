# pipeline.py
# Cognitive Pipeline cho SciOS Cognitive Core - Perception

from typing import Any, Dict
from .base import BasePerceptor

class CognitivePipeline:
    """
    CognitivePipeline định nghĩa chuỗi xử lý perception cho một modality.
    Nó nhận một Perceptor (theo modality), chạy qua các bước chuẩn hóa,
    và trả về dữ liệu đã xử lý dưới dạng dict để tạo PerceptionContext.
    """

    def __init__(self, name: str = "default_pipeline"):
        self.name = name
        self.steps = [
            "loader",
            "parser",
            "cleaner",
            "normalizer",
            "extractor",
            "embedding"
        ]

    def run(self, perceptor: BasePerceptor, raw_input: Any, metadata: Dict = None) -> Dict:
        """
        Chạy pipeline perception cho một input.

        Args:
            perceptor (BasePerceptor): đối tượng xử lý input theo modality
            raw_input (Any): dữ liệu thô
            metadata (Dict): thông tin bổ sung

        Returns:
            Dict: dữ liệu đã xử lý (text, embeddings, entities, relations, confidence…)
        """
        processed: Dict = {}

        # Loader
        loaded = perceptor.load(raw_input, metadata)
        processed.update(loaded)

        # Parser
        parsed = perceptor.parse(processed)
        processed.update(parsed)

        # Cleaner
        cleaned = perceptor.clean(processed)
        processed.update(cleaned)

        # Normalizer
        normalized = perceptor.normalize(processed)
        processed.update(normalized)

        # Entity & Relation Extraction
        processed["entities"] = perceptor.extract_entities(processed)
        processed["relations"] = perceptor.extract_relations(processed)

        # Embedding
        embeddings = perceptor.embed(processed)
        processed.update(embeddings)

        # Confidence score
        processed["confidence"] = perceptor.confidence(processed)

        return processed

    def summary(self) -> Dict[str, Any]:
        """Trả về thông tin pipeline."""
        return {
            "name": self.name,
            "steps": self.steps
        }
