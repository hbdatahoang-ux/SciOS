from __future__ import annotations

from typing import Any

from scios.execution.node.node import ExecutionNode
from scios.execution.scheduler.scheduler import Scheduler
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.context import ExecutionContext
from scios.runtime.executor import Executor


class ExecutionRunner:
    """
    Executes scheduler-released ExecutionNodes at the runtime boundary.

    ExecutionRunner coordinates graph execution with the existing
    Runtime Executor. It does not own scheduling, graph topology,
    operation registration, or RuntimeEngine orchestration.
    """

    def __init__(
        self,
        *,
        scheduler: Scheduler,
        resolver: OperationResolver,
        executor: Executor,
    ) -> None:
        self.scheduler = scheduler
        self.resolver = resolver
        self.executor = executor

    def run_next(self) -> ExecutionNode | None:
        """
        Execute exactly one scheduler-released node.

        Returns:
            The executed node, or None when no node is READY.
        """
        node = self.scheduler.next()

        if node is None:
            return None

        if node.operation_ref is None:
            raise ValueError("ExecutionNode has no operation_ref")

        operation = self.resolver.resolve(node.operation_ref)

        context = ExecutionContext(task=operation)

        node.mark_running()

        result = self.executor.execute(context)

        if result.success:
            node.mark_success()
        else:
            node.mark_failed()

        self.scheduler.notify_completed(node)

        return node
