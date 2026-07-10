# scios/cognitive_core/planner/recovery.py

from typing import Any
from .plan import Plan
from .task import Task

class FailureRecovery:
    """
    FailureRecovery: xử lý khi kế hoạch hoặc Task thất bại.
    Có thể retry, bỏ qua, hoặc tái cấu trúc kế hoạch.
    """

    def __init__(self):
        self.recovery_log: list[str] = []

    def handle_failure(self, plan: Plan | None, error: Exception) -> None:
        """
        Xử lý lỗi trong quá trình thực thi kế hoạch.
        Skeleton: log lỗi và đánh dấu kế hoạch là 'failed'.
        """
        msg = f"Failure detected: {str(error)}"
        self.recovery_log.append(msg)

        if plan:
            plan.metadata["status"] = "failed"
            plan.metadata["error"] = str(error)

    def retry_task(self, task: Task) -> bool:
        """
        Thử thực thi lại một Task.
        Skeleton: giả định retry thành công.
        """
        self.recovery_log.append(f"Retrying task: {task.description}")
        try:
            task.mark_completed()
            return True
        except Exception as e:
            self.recovery_log.append(f"Retry failed: {str(e)}")
            return False

    def fallback_plan(self, plan: Plan) -> Plan:
        """
        Tạo kế hoạch fallback khi kế hoạch chính thất bại.
