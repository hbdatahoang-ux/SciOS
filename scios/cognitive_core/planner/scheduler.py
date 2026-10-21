# scios/cognitive_core/planner/scheduler.py

from typing import List
from .task_graph import TaskGraph
from .task import Task
from .policy import PlanningPolicy

class Scheduler:
    """
    Scheduler: sắp xếp thứ tự thực hiện các Task dựa trên DAG và Policy.
    """

    def __init__(self):
        pass

    def schedule(self, task_graph: TaskGraph, policy: PlanningPolicy) -> List[Task]:
        """
        Trả về danh sách Task theo thứ tự thực hiện.
        - Dùng topological sort từ TaskGraph
        - Áp dụng Policy để điều chỉnh ưu tiên
        """
        order_ids = task_graph.topological_sort()
        ordered_tasks = [task_graph.tasks[tid] for tid in order_ids]

        # Áp dụng policy (ví dụ: sắp xếp lại theo độ ưu tiên)
        ordered_tasks = policy.apply(ordered_tasks)

        return ordered_tasks
