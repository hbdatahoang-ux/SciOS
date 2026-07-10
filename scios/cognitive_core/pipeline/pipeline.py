# pipeline.py
# Cognitive Pipeline Orchestrator cho SciOS Cognitive Core

from typing import Any, Dict
from scios.cognitive_core.perception.base import BasePerceptor

class CognitivePipeline:
    """
    CognitivePipeline định nghĩa chuỗi xử lý perception cho một modality.
    Nó nhận một Perceptor (theo modality), chạy qua các bước chuẩn hóa,
    và trả về dữ liệu đã xử lý dưới dạng dict để tạo PerceptionContext.
    """

    def __init__(self, name: str = "default_pipeline") -> None:
        self.name = name
        self.steps = [
            "loader",
            "parser",
            "cleaner",
            "normalizer",
            "extractor",
            "embedding"
        ]

    def run(self, perceptor: BasePerceptor, raw_input: Any, metadata: Dict | None = None) -> Dict:
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
        processed.update(perceptor.load(raw_input, metadata))

        # Parser
        processed.update(perceptor.parse(processed))

        # Cleaner
        processed.update(perceptor.clean(processed))

        # Normalizer
        processed.update(perceptor.normalize(processed))

        # Entity & Relation Extraction
        processed["entities"] = perceptor.extract_entities(processed)
        processed["relations"] = perceptor.extract_relations(processed)

        # Embedding
        processed.update(perceptor.embed(processed))

        # Confidence score
        processed["confidence"] = perceptor.confidence(processed)

        return processed

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin pipeline hiện tại.
        """
        return {
            "name": self.name,
            "steps": self.steps
        }
