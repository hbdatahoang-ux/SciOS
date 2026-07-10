# scios/cognitive_core/planner/plan.py

from typing import List, Dict
from .goal import Goal
from .task import Task
from .task_graph import TaskGraph
from .constraint import ConstraintSet

class Plan:
    """
    Plan: biểu diễn kế hoạch tổng thể.
    Bao gồm Goal, danh sách Task, TaskGraph, Constraints, và metadata.
    """

    def __init__(self, 
                 goal: Goal, 
                 tasks: List[Task] = None, 
                 task_graph: TaskGraph = None, 
                 constraints: ConstraintSet = None):
        self.goal = goal
        self.tasks = tasks or []
        self.task_graph = task_graph or TaskGraph()
        self.constraints = constraints or ConstraintSet()
        self.metadata: Dict[str, str] = {"status": "created"}

    def add_task(self, task: Task, task_id: str) -> None:
        """Thêm một Task vào kế hoạch và TaskGraph."""
        self.tasks.append(task)
        self.task_graph.add_task(task_id, task)

    def is_completed(self) -> bool:
        """Kiểm tra xem tất cả Task đã hoàn thành chưa."""
        return all(task.is_completed() for task in self.tasks)

    def summary(self) -> Dict[str, any]:
        """Trả về tóm tắt kế hoạch."""
        return {
            "goal": self.goal.description,
            "tasks_total": len(self.tasks),
            "tasks_completed": sum(1 for t in self.tasks if t.is_completed()),
            "status": self.metadata.get("status", "unknown")
        }

    def __repr__(self) -> str:
        return f"<Plan goal='{self.goal.description}' tasks={len(self.tasks)} status={self.metadata['status']}>
