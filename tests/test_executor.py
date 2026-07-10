# tests/test_executor.py

import pytest
from scios.cognitive_core.planner.executor import PlanExecutor
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.goal import Goal


def test_executor_create_and_initial_state():
    executor = PlanExecutor()
    assert executor is not None
    assert executor.get_log() == []


def test_executor_execute_single_task():
    executor = PlanExecutor()
    task = Task(description="Do something")
    plan = Plan(goal=Goal("Single goal"), tasks=[task])

    executor.execute(plan)

    assert task.is_completed()
    logs = executor.get_log()
    assert any("Do something" in log for log in logs)
    assert plan.metadata["status"] == "executed"


def test_executor_execute_fifo_order():
    executor = PlanExecutor()
    t1 = Task(description="Task A")
    t2 = Task(description="Task B")
    plan = Plan(goal=Goal("FIFO goal"), tasks=[t1, t2])

    executor.execute(plan)

    logs = executor.get_log()
    assert logs[0].endswith("Task A")
    assert logs[1].endswith("Task B")
    assert all(t.is_completed() for t in [t1, t2])


def test_executor_execute_multiple_tasks_and_metadata():
    executor = PlanExecutor()
    tasks = [Task(description=f"Task {i}") for i in range(3)]
    plan = Plan(goal=Goal("Multi goal"), tasks=tasks)

    executor.execute(plan)

    assert all(t.is_completed() for t in tasks)
    assert plan.metadata["status"] == "executed"
    assert len(executor.get_log()) == 3


def test_executor_clear_log():
    executor = PlanExecutor()
    t = Task(description="Clear test")
    plan = Plan(goal=Goal("Clear goal"), tasks=[t])

    executor.execute(plan)
    assert executor.get_log() != []

    executor.execution_log.clear()
    assert executor.get_log() == []


def test_executor_empty_plan_raises_error():
    executor = PlanExecutor()
    plan = Plan(goal=Goal("Empty goal"), tasks=[])

    with pytest.raises(ValueError):
        executor.execute(plan)


def test_executor_reuse_for_multiple_plans():
    executor = PlanExecutor()

    t1 = Task(description="First run")
    plan1 = Plan(goal=Goal("Reuse goal 1"), tasks=[t1])
    executor.execute(plan1)
    assert t1.is_completed()

    t2 = Task(description="Second run")
    plan2 = Plan(goal=Goal("Reuse goal 2"), tasks=[t2])
    executor.execute(plan2)
    assert t2.is_completed()


def test_executor_task_failure_handling():
    class FailingTask(Task):
        def run(self):
            raise RuntimeError("Simulated failure")

    executor = PlanExecutor()
    failing_task = FailingTask(description="Failing task")
    plan = Plan(goal=Goal("Failure goal"), tasks=[failing_task])

    # Tùy vào cách PlanExecutor được cài đặt, có thể raise hoặc log error
    try:
        executor.execute(plan)
    except RuntimeError as e:
        assert "Simulated failure" in str(e)
    else:
        logs = executor.get_log()
        assert any("Failing task" in log for log in logs)
        assert plan.metadata.get("status") in ["error", "executed"]
