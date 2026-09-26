"""
SciOS Kernel Core
=================

Central orchestration component of the Scientific Cognitive
Operating System (SciOS).

Responsibilities
----------------
- Own all kernel subsystems.
- Manage kernel lifecycle.
- Adapt public tasks into runtime tasks.
- Execute tasks.
- Provide service lookup.
- Expose kernel status.

Architecture
------------

Public API
    |
    v
 Kernel
    |
 Task Adapter
    |
    v
 Runtime Engine
    |
 Executor

Python 3.11+
"""

from __future__ import annotations


from collections.abc import Callable

from typing import Any


from .bootstrap import build_components

from .state import KernelState



__all__ = [
    "Kernel",
]



class Kernel:
    """
    SciOS Kernel.

    The Kernel is the central orchestration boundary
    between public SciOS APIs and internal Runtime.

    The Kernel SHOULD understand user intent.

    The Runtime SHOULD only execute normalized tasks.
    """



    # ==========================================================
    # Construction
    # ==========================================================

    def __init__(self) -> None:

        components = build_components()


        self.event_bus = (
            components.event_bus
        )

        self.lifecycle = (
            components.lifecycle
        )

        self.registry = (
            components.registry
        )

        self.scheduler = (
            components.scheduler
        )

        self.runtime = (
            components.runtime
        )

        self.dispatcher = (
            components.dispatcher
        )


        self._state: KernelState = "created"



    # ==========================================================
    # Lifecycle
    # ==========================================================

    def boot(self) -> bool:
        """
        Boot kernel.

        Idempotent operation.
        """

        if self._state == "running":

            return True


        self.lifecycle.initialize()

        self.lifecycle.start()


        self._state = "running"


        return True



    def shutdown(self) -> bool:
        """
        Shutdown kernel.

        Idempotent operation.
        """

        if self._state == "stopped":

            return True


        self.lifecycle.shutdown()


        self._state = "stopped"


        return True



    def restart(self) -> bool:
        """
        Restart kernel.
        """

        self.shutdown()

        self._state = "created"

        return self.boot()



    # ==========================================================
    # Task Adaptation Boundary
    # ==========================================================

    def _adapt_task(
        self,
        task: Any,
    ) -> Callable[[], Any]:
        """
        Normalize public tasks into Runtime executable tasks.

        Runtime contract:

            task -> Callable

        Public API contract:

            task -> Any

        Supported:

        - callable
        - string command
        - arbitrary object
        """


        if callable(task):

            return task



        if isinstance(
            task,
            str,
        ):

            return self._command_task(
                task
            )



        return lambda: task



    def _command_task(
        self,
        command: str,
    ) -> Callable[[], dict[str, Any]]:
        """
        Adapt textual commands.

        Example:

            os.run("ping")

        becomes:

            callable returning command result
        """


        def execute():

            return {

                "command":
                    command,

                "status":
                    "accepted",

            }


        return execute



    # ==========================================================
    # Execution
    # ==========================================================

    def run(
        self,
        task: Any,
        **metadata: Any,
    ) -> Any:
        """
        Execute one task.

        Public examples:

            kernel.run("ping")

            kernel.run(
                lambda: "pong"
            )

        """

        if self._state != "running":

            raise RuntimeError(
                "Kernel is not running."
            )



        runtime_task = self._adapt_task(
            task
        )


        context = self.runtime.run(
            task=runtime_task,
            metadata=metadata,
        )


        return context.result



    # ==========================================================
    # Registry
    # ==========================================================

    def service(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve registered service.
        """

        return self.registry.require(
            name
        )



    # ==========================================================
    # Status
    # ==========================================================

    @property
    def state(
        self,
    ) -> KernelState:
        """
        Current kernel state.
        """

        return self._state



    def status(
        self,
    ) -> dict[str, Any]:
        """
        Kernel diagnostics.
        """

        return {

            "state":
                self._state,

            "services":
                self.registry.count(),

            "scheduler_queue":
                len(self.scheduler),

            "runtime":
                self.runtime.status(),

        }



    # ==========================================================
    # Protocol
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"state={self._state}, "

            f"services={self.registry.count()}"

            ")"

        )