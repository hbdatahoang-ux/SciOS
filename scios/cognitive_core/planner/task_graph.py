# scios/cognitive_core/planner/task_graph.py

from typing import Dict, List
from .task import Task

class TaskGraph:
    """
    TaskGraph: biểu diễn đồ thị phụ thuộc giữa các Task.
    Dùng DAG để đảm bảo không có vòng lặp và thứ tự thực hiện hợp lý.
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}        # lưu Task theo ID
        self.edges: Dict[str, List[str]] = {}   # lưu danh sách phụ thuộc (adjacency list)

    def add_task(self, task_id: str, task: Task) -> None:
        """Thêm một Task vào đồ thị."""
        self.tasks[task_id] = task
        if task_id not in self.edges:
            self.edges[task_id] = []

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """Thêm cạnh phụ thuộc: task_id phụ thuộc vào depends_on."""
        if task_id not in self.edges:
            self.edges[task_id] = []
        self.edges[task_id].append(depends_on)
        self.tasks[task_id].add_dependency(depends_on)

    def get_dependencies(self, task_id: str) -> List[str]:
        """Lấy danh sách các Task mà task_id phụ thuộc."""
        return self.edges.get(task_id, [])

    def topological_sort(self) -> List[str]:
        """
        Trả về danh sách Task ID theo thứ
