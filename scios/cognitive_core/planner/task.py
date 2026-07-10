# scios/cognitive_core/planner/task.py

from typing import Any, Dict, List

class Task:
    """
    Task: định nghĩa một nhiệm vụ cụ thể trong kế hoạch.
    Có thể có ràng buộc, trạng thái, và phụ thuộc vào các Task khác.
    """

    def __init__(self, 
                 description: str, 
                 constraints: Dict[str, Any] = None, 
                 dependencies: List[str] = None):
        self.description = description
        self.constraints = constraints or {}
        self.dependencies = dependencies or []
        self.completed: bool = False

    def mark_completed(self) -> None:
        """Đánh dấu Task đã hoàn thành."""
        self.completed = True

    def is_completed(self) -> bool:
        """Kiểm tra trạng thái hoàn thành."""
        return self.completed

    def add_dependency(self, task_id: str) -> None:
        """Thêm một Task phụ thuộc."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"<Task desc='{self.description}' status={status}>"
