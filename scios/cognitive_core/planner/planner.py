# scios/cognitive_core/planner/planner.py

from typing import Any, Dict
from .base import AbstractPlanner
from .goal import Goal
from .task_graph import TaskGraph
from .scheduler import Scheduler
from .strategy import PlanningStrategy
from .policy import PlanningPolicy
from .optimizer import PlanOptimizer
from .validator import PlanValidator
from .executor import PlanExecutor
from .monitor import ProgressMonitor
from .recovery import FailureRecovery
from .plan import Plan

class PlanningEngine(AbstractPlanner):
    """
    PlanningEngine: bộ máy chính để tạo, tối ưu, kiểm tra và thực thi kế hoạch.
    """

    def __init__(self, name: str = "PlanningEngine"):
        super().__init__(name)
        self.goal: Goal | None = None
        self.task_graph = TaskGraph()
        self.scheduler = Scheduler()
        self.strategy = PlanningStrategy()
        self.policy = PlanningPolicy()
        self.optimizer = PlanOptimizer()
        self.validator = PlanValidator()
        self.executor = PlanExecutor()
        self.monitor = ProgressMonitor()
        self.recovery = FailureRecovery()

    def define_goal(self, goal: Dict[str, Any]) -> None:
        self.goal = Goal(**goal)

    def generate_plan(self) -> Plan:
        tasks = self.strategy.decompose_goal(self.goal)
        self.task_graph.build(tasks)
        scheduled_tasks = self.scheduler.schedule(self.task_graph, self.policy)
        return Plan(goal=self.goal, tasks=scheduled_tasks)

    def optimize_plan(self, plan: Plan) -> Plan:
        return self.optimizer.optimize(plan)

    def validate_plan(self, plan: Plan) -> bool:
        return self.validator.validate(plan)

    def execute_plan(self, plan: Plan) -> None:
        try:
            self.executor.execute(plan)
        except Exception as e:
            self.recovery.handle_failure(plan, e)

    def monitor_progress(self) -> Dict[str, Any]:
        return self.monitor.status()

    def recover_failure(self, error: Exception) -> None:
        self.recovery.handle_failure(None, error)
