from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4

from scios.execution.scheduler.executor.worker import Worker


@dataclass
class WorkerPool:
    """
    WorkerPool = Manages multiple workers in parallel.
    """

    pool_id: UUID = field(default_factory=uuid4)
    size: int = 4  # default pool size
    workers: List[Worker] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Khởi tạo pool với số lượng worker mặc định
        self.workers = [Worker() for _ in range(self.size)]

    # =========================================================
    # Core API
    # =========================================================

    def acquire_worker(self) -> Worker:
        """
        Acquire an available worker from pool.
        """
        for worker in self.workers:
            if worker.is_available():
                return worker
        # Nếu không có worker rảnh, tạo mới (scalable pool)
        new_worker = Worker()
        self.workers.append(new_worker)
        return new_worker

    def release_worker(self, worker: Worker) -> None:
        """
        Release worker back to pool (no-op for stateless workers).
        """
        # Worker tự reset trạng thái sau khi execute, nên không cần xử lý thêm
        pass

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Reset pool by clearing all workers and reinitializing.
        """
        self.workers.clear()
        self.workers = [Worker() for _ in range(self.size)]

    def active_workers(self) -> int:
        """
        Return number of busy workers.
        """
        return sum(1 for w in self.workers if not w.is_available())

    def total_workers(self) -> int:
        """
        Return total number of workers in pool.
        """
        return len(self.workers)
