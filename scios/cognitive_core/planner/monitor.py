# scios/cognitive_core/planner/monitor.py

from typing import Dict, List
from .task import Task
from .plan import Plan

class ProgressMonitor:
    """
    ProgressMonitor: giám sát tiến độ thực hiện kế hoạch.
    Theo dõi trạng thái Task, tổng hợp báo cáo tiến độ.
    """

    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def status(self, plan: Plan) -> Dict[str, any]:
        """
        Trả về báo cáo tiến độ hiện tại của kế hoạch.
        Skeleton: tính số Task hoàn thành và tổng số Task.
        """
        if not plan or not plan.tasks:
            return {"progress": 0, "completed": 0, "total": 0, "status": "empty"}

        completed = sum(1 for task in plan.tasks if task.is_completed())
        total = len(plan.tasks)
        progress = completed / total if total > 0 else 0

        report = {
            "progress": round(progress * 100,
