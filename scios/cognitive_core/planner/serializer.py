# scios/cognitive_core/planner/serializer.py

import json
from typing import Any, Dict
from .plan import Plan
from .task import Task

class PlanSerializer:
    """
    PlanSerializer: import/export kế hoạch.
    Dùng để lưu trữ và khôi phục Plan từ JSON.
    """

    def __init__(self):
        pass

    def export(self, plan: Plan) -> str:
        """
        Xuất kế hoạch thành JSON string.
        Skeleton: chỉ serialize các trường cơ bản.
        """
        data: Dict[str, Any] = {
            "goal": plan.goal.description,
            "tasks": [
                {
                    "description": t.description,
                    "completed": t.is_completed(),
                    "constraints": t.constraints,
                    "dependencies": t.dependencies,
                }
                for t in plan.tasks
            ],
            "metadata": plan.metadata,
        }
        return json.dumps(data, indent=2)

    def import_plan(self, json_str: str) -> Plan:
        """
        Khôi phục kế hoạch từ JSON string.
        Skeleton: chỉ tạo lại Plan và Task đơn giản.
        """
        data = json.loads(json_str)
        from .goal import Goal
        from .task_graph import TaskGraph
        from .constraint import ConstraintSet

        goal = Goal(description=data["goal"])
        tasks = [Task(description=t["description"], constraints=t["constraints"], dependencies=t["dependencies"]) 
                 for t in data["tasks"]]

        plan = Plan(goal=goal, tasks=tasks, task_graph=TaskGraph(), constraints=ConstraintSet())
        plan.metadata = data.get("metadata", {})
        return plan
