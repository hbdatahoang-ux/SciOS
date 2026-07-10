# reasoning_stage.py
# Reasoning Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class ReasoningStage(BaseStage):
    """
    ReasoningStage thực hiện suy luận trên dữ liệu perception.
    Nó có thể áp dụng rule-based logic, inference, hoặc mô hình reasoning.
    """

    def __init__(self, name: str = "reasoning_stage", reasoning_engine: Any | None = None) -> None:
        self.name = name
        # reasoning_engine có thể là một hàm, class, hoặc mô hình ML
        self.reasoning_engine = reasoning_engine

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực hiện reasoning trên dữ liệu perception.
        """
        if not self.reasoning_engine:
            # Default reasoning: tạo kết luận đơn giản dựa trên confidence
            confidence = data.get("confidence", 0.0)
            if confidence > 0.8:
                data["reasoning"] = "High confidence perception – likely valid."
            elif confidence > 0.5:
                data["reasoning"] = "Moderate confidence – requires verification."
            else:
                data["reasoning"] = "Low confidence – uncertain perception."
        else:
            # Nếu có reasoning_engine, gọi nó
            if callable(self.reasoning_engine):
                data["reasoning"] = self.reasoning_engine(data)
            elif hasattr(self.reasoning_engine, "infer"):
                data["reasoning"] = self.reasoning_engine.infer(data)
            else:
                raise TypeError(f"Reasoning engine cho stage '{self.name}' không hợp lệ.")

        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "engine": getattr(self.reasoning_engine, "__name__", type(self.reasoning_engine).__name__)
            if self.reasoning_engine else "default_rule_based"
        }
