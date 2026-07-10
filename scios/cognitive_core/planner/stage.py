# scios/cognitive_core/planner/stage.py

from typing import List

class PlanningStage:
    """
    PlanningStage: biểu diễn một giai đoạn trong vòng đời kế hoạch.
    Ví dụ: initialization, decomposition, optimization, validation, execution, monitoring, recovery.
    """

    def __init__(self, name: str, description: str = "", next_stages: List[str] = None):
        self.name = name
        self.description = description
        self.next_stages = next_stages or []

    def add_next_stage(self, stage_name: str) -> None:
        """Thêm một giai đoạn tiếp theo hợp lệ."""
        if stage_name not in self.next_stages:
            self.next_stages.append(stage_name)

    def can_transition_to(self, stage_name: str) -> bool:
        """Kiểm tra xem có thể chuyển sang stage tiếp theo không."""
        return stage_name in self.next_stages

    def __repr__(self) -> str:
        return f"<PlanningStage name='{self.name}' next={self.next_stages}>"
