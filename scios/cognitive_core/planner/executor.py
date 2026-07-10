# scios/cognitive_core/planner/executor.py

from typing import Any
from .plan import Plan
from .task import Task

class PlanExecutor:
    """
    PlanExecutor: interface để thực thi kế hoạch.
    Chịu trách nhiệm chạy các Task theo thứ tự đã được sắp xếp.
    """

    def __init__(self):
        self.execution_log: list[str] = []

    def execute(self, plan: Plan) -> None:
        """
        Thực thi toàn bộ kế hoạch.
        Skeleton: duyệt qua các Task và đánh dấu completed.
        """
        if not plan or not plan.tasks:
            raise ValueError("No tasks to execute in plan")

        for task in plan.tasks:
            self._execute_task(task)

        plan.metadata["status"] = "executed"

    def _execute_task(self, task: Task) -> None:
        """
        Thực thi một Task đơn lẻ.
        Skeleton: chỉ log và đánh dấu completed.
        """
        self.execution_log.append(f"Executing task: {task.description}")
        task.mark_completed()

    def get_log(self) -> list[str]:
        """Trả về nhật ký thực thi."""
        return self.execution_log
