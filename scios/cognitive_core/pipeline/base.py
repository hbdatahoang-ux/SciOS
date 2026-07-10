# base.py
# Base Pipeline cho SciOS Cognitive Core

from typing import Any, Dict, Protocol

class BasePerceptor(Protocol):
    """
    BasePerceptor định nghĩa interface chuẩn cho mọi Perceptor.
    Các pipeline sẽ gọi các method này theo thứ tự để xử lý dữ liệu perception.
    """

    def load(self, raw_input: Any, metadata: Dict | None = None) -> Dict: ...
    def parse(self, data: Dict[str, Any]) -> Dict: ...
    def clean(self, data: Dict[str, Any]) -> Dict: ...
    def normalize(self, data: Dict[str, Any]) -> Dict: ...
    def extract_entities(self, data: Dict[str, Any]) -> list[Dict[str, Any]]: ...
    def extract_relations(self, data: Dict[str, Any]) -> list[Dict[str, Any]]: ...
    def embed(self, data: Dict[str, Any]) -> Dict: ...
    def confidence(self, data: Dict[str, Any]) -> float: ...


class BasePipeline:
    """
    BasePipeline định nghĩa khung chuẩn cho mọi pipeline.
    Các pipeline cụ thể (CognitivePipeline, DAGPipeline…) sẽ kế thừa và triển khai run().
    """

    def __init__(self, name: str = "base_pipeline") -> None:
        self.name = name

    def run(self, perceptor: BasePerceptor, raw_input: Any, metadata: Dict | None = None) -> Dict:
        """
        Phương thức run cần được override bởi pipeline cụ thể.
        """
        raise NotImplementedError("Pipeline subclasses must implement run()")

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin pipeline.
        """
        return {"name": self.name, "type": self.__class__.__name__}
