# output_stage.py
# Output Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class OutputStage(BaseStage):
    """
    OutputStage chịu trách nhiệm định dạng và xuất kết quả cuối cùng của pipeline.
    Nó có thể chuẩn hóa dữ liệu thành dict, JSON, hoặc gửi sang hệ thống khác.
    """

    def __init__(self, name: str = "output_stage", formatter: Any | None = None) -> None:
        self.name = name
        # formatter có thể là hàm, class, hoặc serializer
        self.formatter = formatter

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Định dạng và xuất dữ liệu cuối cùng.
        """
        if not self.formatter:
            # Default: chuẩn hóa dữ liệu thành dict với các trường chính
            output = {
                "text": data.get("text"),
                "entities": data.get("entities", []),
                "relations": data.get("relations", []),
                "confidence": data.get("confidence"),
                "reasoning": data.get("reasoning"),
                "plan": data.get("plan"),
                "reflection": data.get("reflection"),
                "tool_result": data.get("tool_result"),
            }
            data["output"] = output
        else:
            # Nếu có formatter, gọi nó
            if callable(self.formatter):
                data["output"] = self.formatter(data)
            elif hasattr(self.formatter, "format"):
                data["output"] = self.formatter.format(data)
            else:
                raise TypeError(f"Formatter cho stage '{self.name}' không hợp lệ.")

        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "formatter": getattr(self.formatter, "__name__", type(self.formatter).__name__)
            if self.formatter else "default_dict_formatter"
        }
