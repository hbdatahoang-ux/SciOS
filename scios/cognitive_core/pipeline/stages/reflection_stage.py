# reflection_stage.py
# Reflection Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class ReflectionStage(BaseStage):
    """
    ReflectionStage thực hiện phản tư trên dữ liệu pipeline.
    Nó đánh giá kết quả perception, reasoning, và planning để rút ra bài học hoặc điều chỉnh.
    """

    def __init__(self, name: str = "reflection_stage", reflector: Any | None = None) -> None:
        self.name = name
        # reflector có thể là một hàm, class, hoặc mô hình AI
        self.reflector = reflector

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực hiện reflection trên dữ liệu pipeline.
        """
        if not self.reflector:
            # Default reflection: đánh giá confidence và plan
            confidence = data.get("confidence", 0.0)
            plan = data.get("plan", [])
            reasoning = data.get("reasoning", "")

            reflection_notes = []
            if confidence < 0.5:
                reflection_notes.append("Confidence thấp – cần cải thiện perception.")
            if "verification" in reasoning.lower():
                reflection_notes.append("Reasoning yêu cầu xác minh – cần thêm dữ liệu.")
            if plan:
                reflection_notes.append(f"Kế hoạch hiện tại: {plan}")

            data["reflection"] = reflection_notes or ["Không có phản tư đáng chú ý."]
        else:
            # Nếu có reflector, gọi nó
            if callable(self.reflector):
                data["reflection"] = self.reflector(data)
            elif hasattr(self.reflector, "reflect"):
                data["reflection"] = self.reflector.reflect(data)
            else:
                raise TypeError(f"Reflector cho stage '{self.name}' không hợp lệ.")

        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "reflector": getattr(self.reflector, "__name__", type(self.reflector).__name__)
            if self.reflector else "default_rule_based"
        }
