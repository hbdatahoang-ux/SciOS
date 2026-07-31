"""
SciOS Kernel Bootstrap
======================

Composition Root for SciOS Kernel.

Builds and wires all kernel subsystems.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import dataclass
from typing import Any, Iterator
from scios.runtime import Stage


from scios.runtime import (
    ExecutionEngine,
    Pipeline,
    Stage,
)


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
# Components Container
# ==========================================================


@dataclass(slots=True)
class KernelComponents:
    """
    Kernel dependency container.

    Supports both:

        components.runtime

    and legacy:

        components["runtime"]
    """


    state: str


    event_bus: EventBus

    lifecycle: LifecycleManager

    registry: ServiceRegistry

    scheduler: Scheduler

    runtime: ExecutionEngine

    dispatcher: Dispatcher


    pipeline: Pipeline


    plugin_manager: PluginManager

    artifact_manager: ArtifactManager



    # ------------------------------------------------------
    # Dictionary compatibility
    # ------------------------------------------------------


    def keys(self):
        return self.to_dict().keys()



    def values(self):

        return self.to_dict().values()



    def items(self):

        return self.to_dict().items()



    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self.to_dict()[key]



    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self.to_dict()



    def __iter__(
        self,
    ) -> Iterator[str]:

        return iter(self.keys())



    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "state":
                self.state,


            "event_bus":
                self.event_bus,


            "lifecycle":
                self.lifecycle,


            "registry":
                self.registry,


            "scheduler":
                self.scheduler,


            "runtime":
                self.runtime,


            "dispatcher":
                self.dispatcher,


            "pipeline":
                self.pipeline,


            "plugin_manager":
                self.plugin_manager,


            "artifact_manager":
                self.artifact_manager,

        }



# ==========================================================
# Bootstrap
# ==========================================================


class Bootstrap:
    """
    SciOS kernel composition root.
    """



    def __init__(
        self,
    ) -> None:


        self.state = "created"


        #
        # Shared
        #

        self.event_bus = EventBus()



        #
        # Infrastructure
        #

        self.lifecycle = LifecycleManager()

        self.registry = ServiceRegistry()



        #
        # Runtime
        #

        self.scheduler = Scheduler()



        #
        # Cognitive Pipeline
        #

        self.pipeline = Pipeline()



        self._build_default_pipeline()



        self.runtime = ExecutionEngine(
            pipeline=self.pipeline,
            event_bus=self.event_bus,
        )



        #
        # Dispatcher
        #

        self.dispatcher = Dispatcher(
            scheduler=self.scheduler,
            engine=self.runtime,
        )



        #
        # Managers
        #

        self.plugin_manager = PluginManager()

        self.artifact_manager = ArtifactManager()



    # ======================================================
    # Pipeline
    # ======================================================


    def _build_default_pipeline(
        self,
    ) -> None:
        """
        Default SciOS cognitive pipeline.

        planner
            |
        memory
            |
        reasoner
        """

        class DefaultStage(Stage):

            def run(
                self,
                context,
            ):

                # pass-through stage
                #
                # Real cognitive modules
                # will replace these later.

                return context



        stages = [

            DefaultStage(
                "planner"
            ),

            DefaultStage(
                "memory"
            ),

            DefaultStage(
                "reasoner"
            ),

        ]


        for stage in stages:

            self.pipeline.add_stage(
                stage
            )


    # ======================================================
    # Registry
    # ======================================================


    def register_services(
        self,
    ) -> None:


        services = {

            "event_bus":
                self.event_bus,


            "lifecycle":
                self.lifecycle,


            "registry":
                self.registry,


            "scheduler":
                self.scheduler,


            "runtime":
                self.runtime,


            "dispatcher":
                self.dispatcher,


            "pipeline":
                self.pipeline,


            "plugin_manager":
                self.plugin_manager,


            "artifact_manager":
                self.artifact_manager,

        }



        for name, service in services.items():

            self.registry.register(
                name=name,
                service=service,
                overwrite=True,
            )



    # ======================================================
    # Hooks
    # ======================================================


    def attach_hooks(
        self,
    ) -> None:


        hooks = (

            self.runtime,

            self.scheduler,

            self.dispatcher,

            self.plugin_manager,

            self.artifact_manager,

        )


        for hook in hooks:

            self.lifecycle.add_hook(
                hook
            )



    # ======================================================
    # Build
    # ======================================================


    def build(
        self,
    ) -> KernelComponents:


        self.register_services()

        self.attach_hooks()


        self.state = "ready"



        return KernelComponents(

            state=self.state,

            event_bus=self.event_bus,

            lifecycle=self.lifecycle,

            registry=self.registry,

            scheduler=self.scheduler,

            runtime=self.runtime,

            dispatcher=self.dispatcher,

            pipeline=self.pipeline,

            plugin_manager=self.plugin_manager,

            artifact_manager=self.artifact_manager,

        )



    # ======================================================
    # Compatibility API
    # ======================================================


    @classmethod
    def init_kernel(
        cls,
    ) -> KernelComponents:
        """
        Legacy bootstrap entrypoint.

        Used by older tests and integrations.
        """

        return cls().build()



# ==========================================================
# Factory
# ==========================================================


def build_components() -> KernelComponents:
    """
    Build kernel components.
    """

    return Bootstrap().build()