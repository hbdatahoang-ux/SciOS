# planning_stage.py
# Planning Stage cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict
from scios.cognitive_core.pipeline.stage import BaseStage

class PlanningStage(BaseStage):
    """
    PlanningStage chịu trách nhiệm tạo kế hoạch hành động dựa trên dữ liệu perception và reasoning.
    Nó có thể áp dụng rule-based planning hoặc tích hợp với AI planner.
    """

    def __init__(self, name: str = "planning_stage", planner: Any | None = None) -> None:
        self.name = name
        # planner có thể là một hàm, class, hoặc mô hình AI
        self.planner = planner

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo kế hoạch hành động dựa trên dữ liệu perception và reasoning.
        """
        if not self.planner:
            # Default planning: tạo kế hoạch đơn giản dựa trên reasoning
            reasoning = data.get("reasoning", "")
            if "High confidence" in reasoning:
                data["plan"] = ["Validate perception", "Execute action"]
            elif "Moderate confidence" in reasoning:
                data["plan"] = ["Request verification", "Delay execution"]
            else:
                data["plan"] = ["Discard perception", "Seek alternative input"]
        else:
            # Nếu có planner, gọi nó
            if callable(self.planner):
                data["plan"] = self.planner(data)
            elif hasattr(self.planner, "plan"):
                data["plan"] = self.planner.plan(data)
            else:
                raise TypeError(f"Planner cho stage '{self.name}' không hợp lệ.")

        return data

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin stage.
        """
        return {
            "stage": self.name,
            "planner": getattr(self.planner, "__name__", type(self.planner).__name__)
            if self.planner else "default_rule_based"
        }
