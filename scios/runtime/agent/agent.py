"""
SciOS Runtime Agent
===================

High-level autonomous agent orchestration layer.

Python 3.11+
"""

from __future__ import annotations


from typing import Any


from .state import AgentState
from .memory import Memory
from .planner import Planner
from .tool_router import ToolRouter


from scios.runtime.tools.result import ToolResult



__all__ = [
    "Agent",
]



class Agent:
    """
    SciOS Runtime Agent.

    Pipeline:

        Task
         |
        Planner
         |
        ToolRouter
         |
        Result
         |
        AgentResponse
    """



    def __init__(
        self,
        *,
        name: str = "default-agent",
        planner: Planner | None = None,
        memory: Memory | None = None,
        router: ToolRouter | None = None,
        state: AgentState | None = None,
    ) -> None:


        self.name = name


        self._planner = (
            planner
            or Planner()
        )


        self._memory = (
            memory
            or Memory()
        )


        self._router = (
            router
            or ToolRouter()
        )


        self._state = (
            state
            or AgentState()
        )


        self._runs = 0
        self._success = 0
        self._failed = 0



    # ======================================================
    # Properties
    # ======================================================


    @property
    def state(self) -> AgentState:
        return self._state



    @property
    def memory(self) -> Memory:
        return self._memory



    @property
    def planner(self) -> Planner:
        return self._planner



    @property
    def router(self) -> ToolRouter:
        return self._router



    @property
    def tool_router(self) -> ToolRouter:
        return self._router



    @property
    def runs(self) -> int:
        return self._runs



    # ======================================================
    # Planning
    # ======================================================


    def plan(
        self,
        task: str,
    ) -> Any:

        return self._planner.create_plan(
            task
        )



    # ======================================================
    # Memory
    # ======================================================


    def remember(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._memory.store(
            key,
            value,
        )



    def recall(
        self,
        key: str,
    ) -> Any:

        return self._memory.get(
            key
        )



    # ======================================================
    # Tool
    # ======================================================


    def execute_tool(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:

        return self._router.route(
            name,
            **kwargs,
        )



    # ======================================================
    # Main Runtime
    # ======================================================


    def run(
        self,
        task: str,
        *,
        tool: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute agent task.

        Stable contract:

        {
            agent,
            task,
            plan,
            result,
            status
        }
        """


        self._runs += 1


        self.remember(
            "last_task",
            task,
        )


        plan = None


        try:

            #
            # lifecycle
            #
            self._start_state(
                task
            )


            #
            # planning
            #
            plan = self.plan(
                task
            )


            #
            # execution
            #
            if tool is not None:

                result = self.execute_tool(
                    tool,
                    **kwargs,
                )

            else:

                result = self._execute_plan(
                    plan
                )


            #
            # success normalization
            #
            success = self._is_success(
                result
            )


            if success:

                self._success += 1

                self._complete_state(
                    result
                )

            else:

                self._failed += 1

                self._fail_state(
                    result
                )



            return {

                "agent":
                    self.name,


                "task":
                    task,


                "plan":
                    plan,


                "result":
                    self._normalize_result(
                        result
                    ),


                "status":
                    (
                        "completed"
                        if success
                        else "failed"
                    ),

            }



        except Exception as exc:


            self._failed += 1


            self._fail_state(
                exc
            )


            return {

                "agent":
                    self.name,

                "task":
                    task,

                "plan":
                    plan,

                "result":
                    None,

                "status":
                    "failed",

                "error":
                    str(exc),

            }



    # ======================================================
    # Execution helpers
    # ======================================================


    def _execute_plan(
        self,
        plan: Any,
    ) -> Any:


        #
        # Tool plan
        #
        if isinstance(
            plan,
            dict,
        ):

            tool = plan.get(
                "tool"
            )


            args = plan.get(
                "args",
                {},
            )


            if tool:

                return self.execute_tool(
                    tool,
                    **args,
                )



        #
        # Pure reasoning result
        #
        return plan



    def _is_success(
        self,
        result: Any,
    ) -> bool:


        if isinstance(
            result,
            ToolResult,
        ):

            return bool(
                result.success
            )


        #
        # Normal planner output
        #
        return True



    def _normalize_result(
        self,
        result: Any,
    ) -> Any:


        if isinstance(
            result,
            ToolResult,
        ):

            if hasattr(
                result,
                "to_dict",
            ):

                return result.to_dict()


        return result



    # ======================================================
    # State compatibility
    # ======================================================


    def _start_state(
        self,
        task: str,
    ) -> None:


        if hasattr(
            self._state,
            "start",
        ):

            try:
                self._state.start(
                    task
                )
            except TypeError:
                self._state.start()



    def _complete_state(
        self,
        result: Any,
    ) -> None:


        if hasattr(
            self._state,
            "complete",
        ):

            try:
                self._state.complete(
                    result
                )
            except TypeError:
                self._state.complete()



    def _fail_state(
        self,
        error: Any,
    ) -> None:


        if hasattr(
            self._state,
            "fail",
        ):

            self._state.fail(
                error
            )



    # ======================================================
    # Lifecycle
    # ======================================================


    def reset(
        self,
    ) -> None:


        if hasattr(
            self._state,
            "reset",
        ):

            self._state.reset()



    def shutdown(
        self,
    ) -> None:


        if hasattr(
            self._router,
            "registry",
        ):

            self._router.registry.clear()



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self.name,

            "runs":
                self._runs,

            "success":
                self._success,

            "failed":
                self._failed,

            "state":
                self._state.to_dict(),

            "memory":
                self._memory.status(),

            "tools":
                self._router.status(),

        }



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self.name,

            "status":
                self.status(),

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __call__(
        self,
        task: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.run(
            task,
            **kwargs,
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "Agent("
            f"name={self.name!r}, "
            f"runs={self.runs}"
            ")"
        )