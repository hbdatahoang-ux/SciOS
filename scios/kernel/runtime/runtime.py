"""
SciOS Runtime
=============

Runtime facade for the SciOS Kernel.

Responsibilities
----------------
- Coordinate RuntimeExecutor, Worker and RuntimeLoop.
- Accept task submission.
- Execute tasks through the runtime subsystem.
- Manage runtime lifecycle.

Runtime intentionally does NOT:
- implement reasoning
- implement scheduling algorithms
- execute cognitive stages
- manage kernel lifecycle
"""

from __future__ import annotations

from enum import Enum
import threading
from typing import Any

from ..scheduler import Scheduler, Task
from .executor import RuntimeExecutor
from .worker import Worker
from .loop import RuntimeLoop

__all__ = ["RuntimeState", "Runtime"]


class RuntimeState(Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"

    def __str__(self) -> str:
        return self.value


class Runtime:
    """
    Runtime facade.

    Coordinates

        Scheduler
            ↓
        RuntimeExecutor
            ↓
        Worker
            ↓
        RuntimeLoop
    """

    def __init__(
        self,
        scheduler: Scheduler,
        executor: RuntimeExecutor,
        worker: Worker,
        loop: RuntimeLoop,
    ) -> None:
        self._scheduler = scheduler
        self._executor = executor
        self._worker = worker
        self._loop = loop

        self._state = RuntimeState.CREATED
        self._lock = threading.RLock()

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        with self._lock:
            if self._state is not RuntimeState.CREATED:
                return
            self._state = RuntimeState.INITIALIZED

    def start(self) -> None:
        with self._lock:
            if self._state is RuntimeState.RUNNING:
                return
            if self._state is RuntimeState.CREATED:
                self.initialize()
            self._state = RuntimeState.RUNNING

    def stop(self) -> None:
        with self._lock:
            if self._state is RuntimeState.STOPPED:
                return
            self._state = RuntimeState.STOPPING
            self._state = RuntimeState.STOPPED

    def restart(self) -> None:
        with self._lock:
            self.stop()
            self._state = RuntimeState.CREATED
            self.initialize()
            self.start()

    # ==========================================================
    # Task Management
    # ==========================================================

    def submit(self, task: Task) -> None:
        """Submit a task into the scheduler."""
        self._scheduler.submit(task)

    def execute(self) -> Any:
        """Execute the next task via the executor."""
        if self._state is not RuntimeState.RUNNING:
            raise RuntimeError("Runtime is not running.")
        return self._executor.execute()

    def run(self, task: Task) -> Any:
        """
        Submit then execute immediately.
        """
        if self._state is RuntimeState.CREATED:
            self.initialize()
        if self._state is RuntimeState.INITIALIZED:
            self.start()

        self.submit(task)
        return self.execute()

    # ==========================================================
    # Runtime Loop
    # ==========================================================

    def tick(self) -> Any:
        """Run one loop iteration if running."""
        if self._state is RuntimeState.RUNNING:
            return self._loop.tick()
        return None

    # ==========================================================
    # Status
    # ==========================================================

    @property
    def state(self) -> RuntimeState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state is RuntimeState.RUNNING

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def executor(self) -> RuntimeExecutor:
        return self._executor

    @property
    def worker(self) -> Worker:
        return self._worker

    @property
    def loop(self) -> RuntimeLoop:
        return self._loop

    def status(self) -> dict[str, object]:
        return {
            "state": self._state.value,
            "scheduler": getattr(self._scheduler, "status", lambda: {} )(),
            "executor": getattr(self._executor, "status", lambda: {} )(),
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __repr__(self) -> str:
        return f"Runtime(state='{self._state.value}', running={self.is_running})"
