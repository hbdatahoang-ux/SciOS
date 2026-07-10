# scios/cognitive_core/planner/validator.py

from typing import Any
from .plan import Plan
from .constraint import ConstraintSet
from .task_graph import TaskGraph

class PlanValidator:
    """
    PlanValidator: kiểm tra tính hợp lệ của kế hoạch.
    Đảm bảo kế hoạch thỏa mãn ràng buộc, không có vòng lặp, và khả thi.
    """

    def __init__(self):
        pass

    def validate(self, plan: Plan) -> bool:
        """
        Kiểm tra tính hợp lệ của kế hoạch.
        Skeleton: kiểm tra constraints và DAG.
        """
        if not plan:
            raise ValueError("No plan provided for validation")

        # Kiểm tra ràng buộc
        constraints: ConstraintSet = plan.constraints
        if constraints and not constraints.is_satisfied(plan.metadata):
            return False

        # Kiểm tra DAG không có vòng lặp
        task_graph: TaskGraph = plan.task_graph
        try:
            task_graph.topological_sort()
        except ValueError:
            return False

        # Kiểm tra có ít nhất một Task
        if not plan.tasks:
            return False

        return True
