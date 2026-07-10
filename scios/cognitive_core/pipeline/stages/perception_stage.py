# perception_stage.py
# Perception Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage
from scios.cognitive_core.perception.base import BasePerceptor

class PerceptionStage(BaseStage):
    """
    PerceptionStage wrap một Perceptor để chạy như một stage trong pipeline.
    Nó nhận dữ liệu, gọi perceptor xử lý, và trả về kết quả.
    """

    def __init__(self, name: str, perceptor: BasePerceptor) -> None:
        self.name = name
        self.perceptor = perceptor

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua perceptor.
        """
        raw_input = data.get("raw_input")
        metadata = data.get("metadata", {})

        processed: Dict[str, Any] = {}

        # Loader
        processed.update(self.perceptor.load(raw_input, metadata))

        # Parser
        processed.update(self.perceptor.parse(processed))

        # Cleaner
        processed.update(self.perceptor.clean(processed))

        # Normalizer
        processed.update(self.perceptor.normalize(processed))

        # Entity & Relation Extraction
        processed["entities"] = self.perceptor.extract_entities(processed)
        processed["relations"] = self.perceptor.extract_relations(processed)

        # Embedding
        processed.update(self.perceptor.embed(processed))

        # Confidence score
        processed["confidence"] = self.perceptor.confidence(processed)

        # Merge với dữ liệu ban đầu
        data.update(processed)
        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "perceptor": type(self.perceptor).__name__,
            "steps": [
                "loader", "parser", "cleaner", "normalizer",
                "extract_entities", "extract_relations", "embedding", "confidence"
            ]
        }
