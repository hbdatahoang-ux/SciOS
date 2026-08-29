"""
SciOS Runtime Agent
===================

High-level autonomous agent orchestration layer.

Architecture
------------

                    +----------------+
                    |      Agent     |
                    +--------+-------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      AgentState          Memory            Planner
                                                |
                                                v
                                           ToolRouter
                                                |
                                                v
                                           ToolResult

The runtime Agent is an orchestration boundary.

Its responsibilities are limited to:

- lifecycle state
- planning delegation
- memory delegation
- tool routing
- result normalization
- execution diagnostics

Injected dependencies are preserved by object identity.

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .memory import Memory
from .planner import Planner
from .state import AgentState
from .tool_router import ToolRouter

from scios.runtime.tools.result import ToolResult


__all__ = [
    "Agent",
]


class Agent:
    """
    SciOS Runtime Agent.

    Stable response contract
    ------------------------

    ``run()`` returns:

        {
            "agent": str,
            "task": str,
            "plan": Any,
            "result": Any,
            "status": "completed" | "failed",
        }

    Dependency-injection contract
    -----------------------------

    Explicitly supplied dependencies are preserved by identity:

        Agent(memory=x).memory is x
        Agent(planner=x).planner is x
        Agent(router=x).router is x
        Agent(state=x).state is x
    """

    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        name: str = "default-agent",
        *,
        state: AgentState | None = None,
        memory: Memory | None = None,
        planner: Planner | None = None,
        router: ToolRouter | None = None,
    ) -> None:

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "name must be a string"
            )

        if not name:
            raise ValueError(
                "name must not be empty"
            )

        # --------------------------------------------------
        # Identity-preserving dependency injection
        # --------------------------------------------------

        self._name = name

        self._state = (
            state
            if state is not None
            else AgentState()
        )

        self._memory = (
            memory
            if memory is not None
            else Memory()
        )

        self._planner = (
            planner
            if planner is not None
            else Planner()
        )

        self._router = (
            router
            if router is not None
            else ToolRouter()
        )

        # --------------------------------------------------
        # Diagnostics
        # --------------------------------------------------

        self._runs = 0

        self._success = 0

        self._failed = 0

    # ======================================================
    # Properties
    # ======================================================

    @property
    def name(
        self,
    ) -> str:

        return self._name

    @property
    def state(
        self,
    ) -> AgentState:

        return self._state

    @property
    def memory(
        self,
    ) -> Memory:

        return self._memory

    @property
    def planner(
        self,
    ) -> Planner:

        return self._planner

    @property
    def router(
        self,
    ) -> ToolRouter:

        return self._router

    @property
    def tool_router(
        self,
    ) -> ToolRouter:

        return self._router

    @property
    def runs(
        self,
    ) -> int:

        return self._runs

    @property
    def success(
        self,
    ) -> int:

        return self._success

    @property
    def failed(
        self,
    ) -> int:

        return self._failed


    # ======================================================
    # Planning
    # ======================================================

    def plan(
        self,
        task: str,
    ) -> Any:
        """
        Delegate planning to the injected Planner.

        Planner contract
        ----------------

        The canonical Planner entry point is:

            create_plan(goal)

        The injected Planner instance is called directly so that
        dependency injection, subclass overrides, recording doubles,
        and planner failures are all preserved.

        Planner exceptions intentionally propagate to ``run()``,
        where they are converted into the Agent failure contract.
        """

        if not isinstance(
            task,
            str,
        ):
            raise TypeError(
                "task must be a string"
            )

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
        """
        Delegate storage to the injected Memory instance.
        """

        self._memory.store(
            key,
            value,
        )

    def recall(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Delegate retrieval to the injected Memory instance.
        """

        return self._memory.get(
            key,
            default,
        )

    # ======================================================
    # Tool
    # ======================================================

    def execute_tool(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Delegate tool execution to the injected ToolRouter.
        """

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
        Execute an agent task.

        Planner failures and tool failures are represented by
        the stable failed-result contract.

        Unexpected exceptions do not escape the Agent runtime
        boundary.
        """

        if not isinstance(
            task,
            str,
        ):
            raise TypeError(
                "task must be a string"
            )

        self._runs += 1

        plan: Any = None

        try:

            # ------------------------------------------------
            # Lifecycle: running
            # ------------------------------------------------

            self._start_state(
                task
            )

            # ------------------------------------------------
            # Memory
            # ------------------------------------------------

            self.remember(
                "last_task",
                task,
            )

            # ------------------------------------------------
            # Planning
            # ------------------------------------------------

            plan = self.plan(
                task
            )

            # ------------------------------------------------
            # Execution
            # ------------------------------------------------

            if tool is not None:

                result = self.execute_tool(
                    tool,
                    **kwargs,
                )

            else:

                result = self._execute_plan(
                    plan
                )

            # ------------------------------------------------
            # Result classification
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Stable response
            # ------------------------------------------------

            return {
                "agent": self.name,
                "task": task,
                "plan": plan,
                "result": self._normalize_result(
                    result
                ),
                "status": (
                    "completed"
                    if success
                    else "failed"
                ),
            }

        except Exception as exc:

            # ------------------------------------------------
            # Runtime failure boundary
            # ------------------------------------------------

            self._failed += 1

            self._fail_state(
                exc
            )

            return {
                "agent": self.name,
                "task": task,
                "plan": plan,
                "result": None,
                "status": "failed",
                "error": str(exc),
            }

    # ======================================================
    # Plan Execution
    # ======================================================

    def _execute_plan(
        self,
        plan: Any,
    ) -> Any:
        """
        Execute a planner-produced plan.

        Tool plan:

            {
                "tool": "echo",
                "args": {
                    "text": "hello"
                }
            }

        Other planner output is returned as-is.
        """

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

            if args is None:
                args = {}

            if not isinstance(
                args,
                dict,
            ):
                raise TypeError(
                    "plan args must be a dict"
                )

            if tool:

                return self.execute_tool(
                    tool,
                    **args,
                )

        return plan

    # ======================================================
    # Result Classification
    # ======================================================

    def _is_success(
        self,
        result: Any,
    ) -> bool:
        """
        Determine execution success.

        ToolResult controls tool success explicitly.

        Non-ToolResult planner output is considered a successful
        reasoning result.
        """

        if isinstance(
            result,
            ToolResult,
        ):

            return bool(
                result.success
            )

        return True

    # ======================================================
    # Result Normalization
    # ======================================================

    def _normalize_result(
        self,
        result: Any,
    ) -> Any:
        """
        Normalize ToolResult into a dictionary when possible.
        """

        if isinstance(
            result,
            ToolResult,
        ):

            to_dict = getattr(
                result,
                "to_dict",
                None,
            )

            if callable(
                to_dict
            ):

                return to_dict()

        return result

    # ======================================================
    # State Lifecycle
    # ======================================================

    def _start_state(
        self,
        task: str,
    ) -> None:

        self._state.start(
            task
        )

    def _complete_state(
        self,
        result: Any,
    ) -> None:

        self._state.complete(
            result
        )

    def _fail_state(
        self,
        error: Any,
    ) -> None:

        self._state.fail(
            error
        )

    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset lifecycle state.

        Diagnostic counters are historical and therefore
        intentionally preserved.
        """

        self._state.reset()

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown tool registrations.

        The injected router remains the same object.
        """

        registry = getattr(
            self._router,
            "registry",
            None,
        )

        clear = getattr(
            registry,
            "clear",
            None,
        )

        if callable(
            clear
        ):

            clear()

    # ======================================================
    # Diagnostics
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return runtime diagnostics.
        """

        return {
            "name": self.name,
            "runs": self._runs,
            "success": self._success,
            "failed": self._failed,
            "state": self._state.to_dict(),
            "memory": self._memory.status(),
            "tools": self._router.status(),
        }

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Return serializable agent representation.
        """

        return {
            "name": self.name,
            "status": self.status(),
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

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "Agent("
            f"name={self.name!r}, "
            f"runs={self.runs}"
            ")"
        )