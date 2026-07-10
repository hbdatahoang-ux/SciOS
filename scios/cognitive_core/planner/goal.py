# scios/cognitive_core/planner/goal.py

from typing import Any, Dict, List

class Goal:
    """
    Goal: biểu diễn mục tiêu tổng thể của kế hoạch.
    Có thể bao gồm mô tả, tiêu chí thành công, và các ràng buộc.
    """

    def __init__(self, 
                 description: str, 
                 success_criteria: List[str] = None, 
                 constraints: Dict[str, Any] = None):
        self.description = description
        self.success_criteria = success_criteria or []
        self.constraints = constraints or {}

    def add_success_criterion(self, criterion: str) -> None:
        """Thêm một tiêu chí thành công mới."""
        self.success_criteria.append(criterion)

    def add_constraint(self, key: str, value: Any) -> None:
        """Thêm một ràng buộc vào mục tiêu."""
        self.constraints[key] = value

    def is_satisfied(self, results: Dict[str, Any]) -> bool:
        """
        Kiểm tra xem kết quả có thỏa mãn tiêu chí thành công không.
        (Skeleton: chỉ kiểm tra đơn giản).
        """
        for criterion in self.success_criteria:
            if criterion not in results.get("achievements", []):
                return False
        return True

    def __repr__(self) -> str:
        return f"<Goal desc='{self.description}' criteria={len(self.success_criteria)}>"
