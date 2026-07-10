# scios/cognitive_core/planner/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class AbstractPlanner(ABC):
    """
    AbstractPlanner: lớp trừu tượng cho mọi planner.
    Định nghĩa interface chung để tạo, tối ưu, kiểm tra và thực thi kế hoạch.
    """

    def __init__(self, name: str = "AbstractPlanner"):
        self.name = name

    @abstractmethod
    def define_goal(self, goal: Dict[str, Any]) -> None:
        """Xác định mục tiêu chính của kế hoạch."""
        pass

    @abstractmethod
    def generate_plan(self) -> Any:
        """Sinh kế hoạch từ mục tiêu, nhiệm vụ và ràng buộc."""
        pass

    @abstractmethod
    def optimize_plan(self, plan: Any) -> Any:
        """Tối ưu hóa kế hoạch (chi phí, thời gian, tài nguyên)."""
        pass

    @abstractmethod
    def validate_plan(self, plan: Any) -> bool:
        """Kiểm tra tính hợp lệ của kế hoạch."""
        pass

    @abstractmethod
    def execute_plan(self, plan: Any) -> None:
        """Thực thi kế hoạch."""
        pass

    @abstractmethod
    def monitor_progress(self) -> Dict[str, Any]:
        """Giám sát tiến độ thực hiện kế hoạch."""
        pass

    @abstractmethod
    def recover_failure(self, error: Exception) -> None:
        """Xử lý khi kế hoạch thất bại."""
        pass
