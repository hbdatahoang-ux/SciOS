from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from uuid import UUID, uuid4
import time

from scios.execution.node.node import ExecutionNode


@dataclass
class SchedulerMonitor:
    """
    SchedulerMonitor = Tracks progress, logs, and metrics for scheduler.
    """

    monitor_id: UUID = field(default_factory=uuid4)
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "tasks_started": 0,
        "tasks_completed": 0,
        "start_time": None,
        "end_time": None,
        "duration": 0.0,
    })

    # =========================================================
    # Core API
    # =========================================================

    def start(self) -> None:
        """
        Mark scheduler start.
        """
        self.metrics["start_time"] = time.time()
        self.log("Scheduler started.")

    def stop(self) -> None:
        """
        Mark scheduler stop.
        """
        self.metrics["end_time"] = time.time()
        self.metrics["duration"] = self.metrics["end_time"] - self.metrics["start_time"]
        self.log("Scheduler stopped.")

    def task_started(self, node: ExecutionNode) -> None:
        """
        Record task start.
        """
        self.metrics["tasks_started"] += 1
        self.log(f"Task started: {node.node_id}")

    def task_completed(self, node: ExecutionNode) -> None:
        """
        Record task completion.
        """
        self.metrics["tasks_completed"] += 1
        self.log(f"Task completed: {node.node_id}")

    # =========================================================
    # Utility
    # =========================================================

    def log(self, message: str) -> None:
        """
        Append log message.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logs.append(f"[{timestamp}] {message}")

    def report(self) -> Dict[str, Any]:
        """
        Return metrics summary.
        """
        return {
            "tasks_started": self.metrics["tasks_started"],
            "tasks_completed": self.metrics["tasks_completed"],
            "duration": self.metrics["duration"],
            "logs": self.logs,
        }

    def reset(self) -> None:
        """
        Reset monitor state.
        """
        self.logs.clear()
        self.metrics.update({
            "tasks_started": 0,
            "tasks_completed": 0,
            "start_time": None,
            "end_time": None,
            "duration": 0.0,
        })
