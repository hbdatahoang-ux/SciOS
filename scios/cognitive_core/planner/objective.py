# scios/cognitive_core/planner/objective.py

from typing import Any, Dict, List
from .task import Task

class Objective:
    """
    Objective: biểu diễn một mục tiêu con (subgoal).
    Được phân rã từ Goal và có thể bao gồm nhiều Task.
    """

    def __init__(self, description: str, parent_goal: str = None, constraints: Dict[str, Any] = None):
        self.description = description
        self.parent_goal = parent_goal
        self.constraints = constraints or {}
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Thêm một Task vào Objective."""
        self.tasks.append(task)

    def is_completed(self) -> bool:
        """Kiểm tra xem tất cả Task trong Objective đã hoàn thành chưa."""
        return all(task.is_completed() for task in self.tasks)

    def __repr__(self) -> str:
        return f"<Objective desc='{self.description}' tasks={len(self.tasks)}>"
