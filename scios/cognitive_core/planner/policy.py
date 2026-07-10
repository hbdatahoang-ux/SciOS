# scios/cognitive_core/planner/policy.py

from typing import List
from .task import Task

class PlanningPolicy:
    """
    PlanningPolicy: chính sách điều hành kế hoạch.
    Dùng để điều chỉnh thứ tự Task theo ưu tiên, deadline, hoặc resource cost.
    """

    def __init__(self, rules: dict = None):
        # rules có thể chứa các quy tắc như {"priority": {...}, "deadline": {...}}
        self.rules = rules or {}

    def apply(self, tasks: List[Task]) -> List[Task]:
        """
        Áp dụng chính sách lên danh sách Task.
        Skeleton: sắp xếp theo constraint 'priority' nếu có, ngược lại giữ nguyên.
        """
        def priority(task: Task) -> int:
            return task.constraints.get("priority", 0)

        # Sắp xếp giảm dần theo priority
        ordered = sorted(tasks, key=priority, reverse=True)
        return ordered
