"""
SciOS Base Agent
================

Base abstraction for every cognitive agent inside SciOS.

Responsibilities
----------------
- Agent identity and metadata
- Enable / disable lifecycle
- Common execution wrapper
- Execution diagnostics
- Memory dependency injection
- Tool router dependency injection
- Memory delegation
- Tool execution delegation

Architecture
------------

                Agent
                  |
        +---------+---------+
        |                   |
      Memory            ToolRouter
        |                   |
   Runtime Memory     Runtime Tool Layer

Python 3.11+
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


__all__ = [
    "Agent",
    "BaseAgent",
]


class Agent(ABC):
    """
    Root abstraction of every SciOS agent.

    The base Agent owns framework-level concerns:

    - identity
    - metadata
    - enable/disable state
    - execution lifecycle
    - execution counter
    - memory delegation
    - tool-router delegation

    Concrete cognitive behavior belongs to ``run()``.
    """

    def __init__(
        self,
        name: str,
        version: str = "0.3.0",
        *,
        memory: Any | None = None,
        router: Any | None = None,
    ) -> None:

        # ---------------------------------------------------
        # Identity
        # ---------------------------------------------------

        self._id = str(uuid4())

        self._name = name

        self._version = version

        # ---------------------------------------------------
        # Lifecycle
        # ---------------------------------------------------

        self._state = "idle"

        self._enabled = True

        # ---------------------------------------------------
        # Metadata
        # ---------------------------------------------------

        self._created_at = datetime.now(
            timezone.utc
        ).isoformat()

        # ---------------------------------------------------
        # Diagnostics
        # ---------------------------------------------------

        self._executions = 0

        # ---------------------------------------------------
        # Dependencies
        #
        # IMPORTANT:
        #
        # Do not use:
        #
        #     memory or Memory()
        #
        # or:
        #
        #     router or ToolRouter()
        #
        # because Memory and ToolRouter can be empty and
        # therefore evaluate as False.
        #
        # Dependency injection is identity-preserving.
        # ---------------------------------------------------

        if memory is None:
            from scios.runtime.agent.memory import Memory

            self._memory = Memory()

        else:
            self._memory = memory

        if router is None:
            from scios.runtime.agent.tool_router import ToolRouter

            self._router = ToolRouter()

        else:
            self._router = router

    # =======================================================
    # Metadata
    # =======================================================

    @property
    def id(self) -> str:
        """
        Stable unique agent identifier.
        """

        return self._id

    @property
    def name(self) -> str:
        """
        Agent name.
        """

        return self._name

    @property
    def version(self) -> str:
        """
        Agent version.
        """

        return self._version

    @property
    def state(self) -> str:
        """
        Current framework execution state.

        Normal states:

        - ``idle``
        - ``running``
        """

        return self._state

    @property
    def enabled(self) -> bool:
        """
        Whether the agent is enabled.
        """

        return self._enabled

    @property
    def memory(self) -> Any:
        """
        Injected memory dependency.
        """

        return self._memory

    @property
    def router(self) -> Any:
        """
        Injected tool router dependency.
        """

        return self._router

    @property
    def tool_router(self) -> Any:
        """
        Alias for ``router``.
        """

        return self._router

    @property
    def executions(self) -> int:
        """
        Number of completed execution attempts.
        """

        return self._executions

    # =======================================================
    # Lifecycle
    # =======================================================

    def enable(self) -> None:
        """
        Enable the agent.
        """

        self._enabled = True

    def disable(self) -> None:
        """
        Disable the agent.

        Disabled agents reject execution through
        ``execute()``.
        """

        self._enabled = False

    def reset(self) -> None:
        """
        Restore initial runtime state.

        The execution counter is reset.
        Identity and creation metadata remain unchanged.
        """

        self._state = "idle"

        self._executions = 0

    # =======================================================
    # Memory Delegation
    # =======================================================

    def remember(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value through the configured memory backend.
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
        Retrieve a value through the configured memory backend.
        """

        return self._memory.get(
            key,
            default,
        )

    # =======================================================
    # Tool Delegation
    # =======================================================

    def execute_tool(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a registered tool through the configured
        tool router.
        """

        return self._router.route(
            name,
            **kwargs,
        )

    # =======================================================
    # Invocation
    # =======================================================

    def __call__(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Callable shorthand for ``execute()``.
        """

        return self.execute(
            task,
            *args,
            **kwargs,
        )

    # =======================================================
    # Execution Wrapper
    # =======================================================

    def execute(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Common framework execution wrapper.

        Guarantees:

        - ``None`` task is rejected.
        - disabled agents are rejected.
        - state becomes ``running`` during execution.
        - state returns to ``idle`` afterward.
        - execution counter increases exactly once.
        """

        if task is None:
            raise ValueError(
                "Task cannot be None."
            )

        if not self._enabled:
            raise RuntimeError(
                f"Agent '{self._name}' is disabled."
            )

        self._state = "running"

        try:

            return self.run(
                task,
                *args,
                **kwargs,
            )

        finally:

            self._executions += 1

            self._state = "idle"

    # =======================================================
    # Implementation Contract
    # =======================================================

    @abstractmethod
    def run(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Concrete agent implementation.

        Subclasses must implement this method.

        ``execute()`` is the framework wrapper.
        ``run()`` contains agent-specific behavior.
        """

        raise NotImplementedError

    # =======================================================
    # Status
    # =======================================================

    def status(self) -> dict[str, Any]:
        """
        Return a snapshot of public agent diagnostics.

        A new dictionary is returned for every invocation.
        """

        return {
            "id": self._id,
            "name": self._name,
            "state": self._state,
            "version": self._version,
            "enabled": self._enabled,
            "executions": self._executions,
            "created_at": self._created_at,
        }

    # =======================================================
    # Representation
    # =======================================================

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id='{self._id}', "
            f"name='{self._name}', "
            f"state='{self._state}')"
        )


# ===========================================================
# Backward Compatibility
# ===========================================================

BaseAgent = Agent