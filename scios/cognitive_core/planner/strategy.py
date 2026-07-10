# scios/cognitive_core/planner/strategy.py

from typing import List
from .goal import Goal
from .objective import Objective
from .task import Task

class PlanningStrategy:
    """
    PlanningStrategy: chiến lược phân rã mục tiêu thành Objective và Task.
    Có thể mở rộng với nhiều thuật toán khác nhau.
    """

    def __init__(self, name: str = "DefaultStrategy"):
        self.name = name

    def decompose_goal(self, goal: Goal) -> List[Task]:
        """
        Phân rã Goal thành danh sách Task.
        Skeleton: tạo một Objective duy nhất và một số Task đơn giản.
        """
        objective = Objective(description=f"Subgoal of {goal.description}", parent_goal=goal.description)

        # Ví dụ: mỗi success criterion tạo thành một Task
        tasks = []
        for criterion in goal.success_criteria:
            task = Task(description=f"Achieve criterion: {criterion}")
            objective.add_task(task)
            tasks.append(task)

        # Nếu không có success criteria, tạo một Task mặc định
        if not tasks:
            default_task = Task(description=f"Execute plan for {goal.description}")
            objective.add_task(default_task)
            tasks.append(default_task)

        return tasks
