"""
SciOS Bootstrap (Composition Root)

Builds the complete SciOS Kernel object graph.
"""

from __future__ import annotations
from typing import Optional

from .artifacts import ArtifactManager
from .config import KernelConfig
from .context import ContextManager
from .dispatcher import Dispatcher
from .events import EventBus
from .execution import ExecutionEngine
from .kernel import Kernel
from .lifecycle import LifecycleManager
from .plugins import PluginManager
from .registry import ServiceRegistry
from .scheduler import Scheduler

from .runtime.executor import RuntimeExecutor
from .runtime.loop import RuntimeLoop
from .runtime.runtime import Runtime
from .runtime.worker import Worker


def _build_infrastructure(config: KernelConfig) -> tuple[EventBus, ServiceRegistry, ContextManager]:
    event_bus = EventBus()
    registry = ServiceRegistry()
    context = ContextManager()
    return event_bus, registry, context


def _build_services(event_bus: EventBus, config: KernelConfig) -> tuple[Scheduler, PluginManager, ArtifactManager]:
    scheduler = Scheduler()
    plugins = PluginManager()
    artifacts = ArtifactManager(event_bus if getattr(config, "enable_events", True) else None)
    return scheduler, plugins, artifacts


def _build_runtime(scheduler: Scheduler) -> tuple[Dispatcher, ExecutionEngine, RuntimeExecutor, Worker, RuntimeLoop, Runtime]:
    dispatcher = Dispatcher(scheduler)
    execution_engine = ExecutionEngine(dispatcher)
    runtime_executor = RuntimeExecutor(scheduler, execution_engine)
    worker = Worker(runtime_executor)
    loop = RuntimeLoop(scheduler, worker)
    runtime = Runtime(scheduler=scheduler, executor=runtime_executor, worker=worker, loop=loop)
    return dispatcher, execution_engine, runtime_executor, worker, loop, runtime


def build_kernel(config: Optional[KernelConfig] = None) -> Kernel:
    config = config or KernelConfig()

    event_bus, registry, context = _build_infrastructure(config)
    scheduler, plugins, artifacts = _build_services(event_bus, config)
    dispatcher, execution_engine, runtime_executor, worker, loop, runtime = _build_runtime(scheduler)

    kernel = Kernel(
        config=config,
        event_bus=event_bus,
        registry=registry,
        context=context,
        scheduler=scheduler,
        plugins=plugins,
        artifacts=artifacts,
        dispatcher=dispatcher,
        execution_engine=execution_engine,
        runtime=runtime,
        lifecycle=None,
    )

    lifecycle = LifecycleManager(kernel)
    kernel._lifecycle = lifecycle

    # Register all services
    registry.register("config", config)
    registry.register("events", event_bus)
    registry.register("context", context)
    registry.register("scheduler", scheduler)
    registry.register("plugins", plugins)
    registry.register("artifacts", artifacts)
    registry.register("dispatcher", dispatcher)
    registry.register("execution", execution_engine)
    registry.register("runtime_executor", runtime_executor)
    registry.register("worker", worker)
    registry.register("runtime_loop", loop)
    registry.register("runtime", runtime)
    registry.register("kernel", kernel)

    return kernel
