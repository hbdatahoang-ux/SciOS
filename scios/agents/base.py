"""
SciOS Base Agent
================

Base implementation for every cognitive agent inside SciOS.
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
    """

    def __init__(
        self,
        name: str,
        version: str = "0.3.0",
    ) -> None:

        self._id = str(uuid4())

        self._name = name

        self._version = version

        self._state = "idle"

        self._enabled = True

        self._created_at = datetime.now(
            timezone.utc
        ).isoformat()

        self._executions = 0

    # -------------------------------------------------------
    # Metadata
    # -------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def state(self) -> str:
        return self._state

    @property
    def enabled(self) -> bool:
        return self._enabled

    # -------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def reset(self) -> None:
        """
        Restore initial runtime state.
        """

        self._state = "idle"
        self._executions = 0

    # -------------------------------------------------------
    # Invocation
    # -------------------------------------------------------

    def __call__(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        return self.execute(
            task,
            *args,
            **kwargs,
        )

    # -------------------------------------------------------
    # Execution Wrapper
    # -------------------------------------------------------

    def execute(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Common execution wrapper.
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

            result = self.run(
                task,
                *args,
                **kwargs,
            )

            return result

        finally:

            self._executions += 1
            self._state = "idle"

    # -------------------------------------------------------
    # Implementation
    # -------------------------------------------------------

    @abstractmethod
    def run(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Concrete implementation.
        """

    # -------------------------------------------------------
    # Status
    # -------------------------------------------------------

    def status(self) -> dict[str, Any]:

        return {

            "id": self._id,

            "name": self._name,

            "state": self._state,

            "version": self._version,

            "enabled": self._enabled,

            "executions": self._executions,

            "created_at": self._created_at,
        }

    # -------------------------------------------------------
    # Representation
    # -------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"id='{self._id}', "
            f"name='{self._name}', "
            f"state='{self._state}')"
        )


# Backward compatibility
BaseAgent = Agent