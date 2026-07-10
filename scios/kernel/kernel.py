"""
SciOS Kernel
============

Core microkernel orchestrator.

Responsibilities
----------------
- Hold references to all infrastructure services.
- Provide unified API surface for integration.
- Delegate lifecycle control to LifecycleManager.
- Route execution requests into the Runtime subsystem.
"""

from __future__ import annotations
from typing import Any, Optional

from .config import KernelConfig
from .events import EventBus
from .registry import ServiceRegistry
from .context import ContextManager
from .scheduler import Scheduler, Task
from .dispatcher import Dispatcher
from .execution import ExecutionEngine
from .runtime.runtime import Runtime
from .lifecycle import LifecycleManager
from .state import KernelState
from .plugins import PluginManager
from .artifacts import ArtifactManager


__all__ = ["Kernel"]


class Kernel:
    """
    SciOS Kernel orchestrator.
    """

    def __init__(
        self,
        config: KernelConfig,
        event_bus: EventBus,
        registry: ServiceRegistry,
        context: ContextManager,
        scheduler: Scheduler,
        plugins: PluginManager,
        artifacts: ArtifactManager,
        dispatcher: Dispatcher,
        execution_engine: ExecutionEngine,
        runtime: Runtime,
        lifecycle: Optional[LifecycleManager] = None,
    ) -> None:
        self._config = config
        self._event_bus = event_bus
        self._registry = registry
        self._context = context
        self._scheduler = scheduler
        self._plugins = plugins
        self._artifacts = artifacts
        self._dispatcher = dispatcher
        self._execution_engine = execution_engine
        self._runtime = runtime
        self._lifecycle = lifecycle

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def boot(self) -> None:
        if not self._lifecycle:
            raise RuntimeError("LifecycleManager not attached")
        self._lifecycle.boot()

    def stop(self) -> None:
        if not self._lifecycle:
            raise RuntimeError("LifecycleManager not attached")
        self._lifecycle.stop()

    def restart(self) -> None:
        if not self._lifecycle:
            raise RuntimeError("LifecycleManager not attached")
        self._lifecycle.restart()

    @property
    def state(self) -> KernelState:
        return self._lifecycle.state if self._lifecycle else KernelState.CREATED

    # ==========================================================
    # Execution
    # ==========================================================

    def run(self, request: Any) -> Any:
        """
        Submit a request into the runtime pipeline.
        """
        task = Task(name="request", payload=request)
        self._scheduler.submit(task)
        return self._runtime.run(task)

    def submit(self, task: Task) -> None:
        """Submit a task directly to the scheduler."""
        self._scheduler.submit(task)

    # ==========================================================
    # Services
    # ==========================================================

    @property
    def config(self) -> KernelConfig:
        return self._config

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def registry(self) -> ServiceRegistry:
        return self._registry

    @property
    def context(self) -> ContextManager:
        return self._context

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @property
    def plugins(self) -> PluginManager:
        return self._plugins

    @property
    def artifacts(self) -> ArtifactManager:
        return self._artifacts

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher

    @property
    def execution_engine(self) -> ExecutionEngine:
        return self._execution_engine

    @property
    def runtime(self) -> Runtime:
        return self._runtime

    # ==========================================================
    # Utilities
    # ==========================================================

    def service(self, name: str) -> Any:
        """Lookup a service by name from the registry."""
        return self._registry.lookup(name)

    def __repr__(self) -> str:
        return f"Kernel(state={self.state}, plugins={len(self._plugins)})"
