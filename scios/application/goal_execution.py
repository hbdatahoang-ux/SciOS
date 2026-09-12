from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.operation.resolver import OperationResolver
from scios.execution.runner.runner import ExecutionRunner
from scios.execution.scheduler.scheduler import Scheduler
from scios.runtime.executor import Executor


@dataclass
class GoalExecutionResult:
    goal: Goal
    plan: Plan
    graph: ExecutionGraph


class GoalExecutionService:
    def __init__(
        self,
        *,
        planner: Planner,
        compiler: PlanCompiler,
        resolver: OperationResolver,
        executor: Executor,
    ) -> None:
        self.planner = planner
        self.compiler = compiler
        self.resolver = resolver
        self.executor = executor

    def execute(
        self,
        goal: Goal,
        tasks: Iterable[str | Task] | None = None,
    ) -> GoalExecutionResult:
        plan = self.planner.create_plan(
            goal,
            tasks=tasks,
        )

        graph = self.compiler.compile(plan)

        scheduler = Scheduler(graph)

        runner = ExecutionRunner(
            scheduler=scheduler,
            resolver=self.resolver,
            executor=self.executor,
        )

        while runner.run_next() is not None:
            pass

        return GoalExecutionResult(
            goal=goal,
            plan=plan,
            graph=graph,
        )
