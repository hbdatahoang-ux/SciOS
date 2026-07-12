"""
SciOS Kernel Bootstrap
======================

Composition Root for the SciOS Kernel.

Responsibilities
----------------
- Construct all kernel subsystems.
- Wire subsystem dependencies.
- Register default services.
- Attach lifecycle hooks.

This module intentionally DOES NOT import Kernel in order to
avoid circular imports. Kernel construction should be performed
by the public API (kernel/__init__.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from scios.runtime import ExecutionEngine
from scios.shared import EventBus

from .artifact_manager import ArtifactManager
from .dispatcher import Dispatcher
from .lifecycle import LifecycleManager
from .plugin_manager import PluginManager
from .registry import ServiceRegistry
from .scheduler import Scheduler

__all__ = [
    "KernelComponents",
    "Bootstrap",
    "build_components",
]


# ==========================================================
# Kernel Components
# ==========================================================


@dataclass(slots=True)
class KernelComponents:
    """
    Fully wired kernel components.

    This object is consumed by Kernel during construction.
    """

    event_bus: EventBus

    lifecycle: LifecycleManager

    registry: ServiceRegistry

    scheduler: Scheduler

    runtime: ExecutionEngine

    dispatcher: Dispatcher

    plugin_manager: PluginManager

    artifact_manager: ArtifactManager


# ==========================================================
# Bootstrap
# ==========================================================


class Bootstrap:
    """
    Kernel composition root.

    Responsible for wiring together all kernel infrastructure.
    """

    def __init__(self) -> None:

        # --------------------------------------------------
        # Shared Infrastructure
        # --------------------------------------------------

        self.event_bus = EventBus()

        # --------------------------------------------------
        # Core Infrastructure
        # --------------------------------------------------

        self.lifecycle = LifecycleManager()

        self.registry = ServiceRegistry()

        # --------------------------------------------------
        # Execution
        # --------------------------------------------------

        self.scheduler = Scheduler()

        self.runtime = ExecutionEngine(
            event_bus=self.event_bus,
        )

        self.dispatcher = Dispatcher(
            scheduler=self.scheduler,
            engine=self.runtime,
        )

        # --------------------------------------------------
        # Managers
        # --------------------------------------------------

        self.plugin_manager = PluginManager()

        self.artifact_manager = ArtifactManager()

    # ======================================================
    # Registration
    # ======================================================

    def register_services(self) -> None:
        """
        Register all default kernel services.
        """

        services = {
            "event_bus": self.event_bus,
            "lifecycle": self.lifecycle,
            "registry": self.registry,
            "scheduler": self.scheduler,
            "runtime": self.runtime,
            "dispatcher": self.dispatcher,
            "plugin_manager": self.plugin_manager,
            "artifact_manager": self.artifact_manager,
        }

        for name, service in services.items():

            self.registry.register(
                name=name,
                service=service,
                overwrite=True,
            )

    # ======================================================
    # Lifecycle Hooks
    # ======================================================

    def attach_hooks(self) -> None:
        """
        Register lifecycle-aware components.
        """

        hooks = (
            self.runtime,
            self.scheduler,
            self.dispatcher,
            self.plugin_manager,
            self.artifact_manager,
        )

        for hook in hooks:

            self.lifecycle.add_hook(hook)

    # ======================================================
    # Build
    # ======================================================

    def build(self) -> KernelComponents:
        """
        Build a fully wired kernel dependency graph.

        Returns
        -------
        KernelComponents
            Ready-to-use kernel components.
        """

        self.register_services()

        self.attach_hooks()

        return KernelComponents(
            event_bus=self.event_bus,
            lifecycle=self.lifecycle,
            registry=self.registry,
            scheduler=self.scheduler,
            runtime=self.runtime,
            dispatcher=self.dispatcher,
            plugin_manager=self.plugin_manager,
            artifact_manager=self.artifact_manager,
        )


# ==========================================================
# Public Factory
# ==========================================================


def build_components() -> KernelComponents:
    """
    Build the complete kernel dependency graph.

    Unlike build_kernel(), this function does NOT construct
    a Kernel instance. It only returns fully wired components,
    preventing circular imports between bootstrap.py and
    kernel.py.
    """

    return Bootstrap().build()