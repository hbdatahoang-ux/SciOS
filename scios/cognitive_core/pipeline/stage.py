# stage.py
# Base Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict, Protocol

class BaseStage(Protocol):
    """
    BaseStage định nghĩa interface chuẩn cho một stage trong pipeline.
    Mỗi stage nhận dữ liệu (dict), xử lý, và trả về dữ liệu đã cập nhật.
    """

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...


class Stage:
    """
    Stage cơ bản, có thể wrap một hàm hoặc đối tượng có logic xử lý.
    """

    def __init__(self, name: str, handler: Any) -> None:
        """
        Args:
            name (str): tên stage
            handler (Any): hàm callable hoặc đối tượng có method process
        """
        self.name = name
        self.handler = handler

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua stage.
        """
        if callable(self.handler):
            return self.handler(data)
        elif hasattr(self.handler, "process"):
            return self.handler.process(data)
        else:
            raise TypeError(f"Handler cho stage '{self.name}' không hợp lệ.")

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "name": self.name,
            "type": getattr(self.handler, "__name__", type(self.handler).__name__)
        }
