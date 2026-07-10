"""
SciOS Base Agent
================

Abstract base class for all cognitive agents in SciOS.

Responsibilities
----------------
- Define the common agent interface
- Manage lifecycle
- Maintain agent metadata
- Expose execution status
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "BaseAgent",
]


class BaseAgent(ABC):
    """
    Abstract base class for all SciOS agents.

    Every cognitive subsystem (Planner, Memory, Reasoning,
    ToolUse, Reflection, Collaboration) derives from this
    class to provide a consistent execution interface.
    """

    def __init__(
        self,
        name: str,
        version: str = "0.1.3",
    ) -> None:

        self._name = name

        self._version = version

        self._enabled = True

        self._created_at = datetime.now(
            timezone.utc
        ).isoformat()

        self._executions = 0

    # ======================================================
    # Metadata
    # ======================================================

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

    # ======================================================
    # Lifecycle
    # ======================================================

    def enable(self) -> None:
        """
        Enable the agent.
        """
        self._enabled = True

    def disable(self) -> None:
        """
        Disable the agent.
        """
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """
        Whether the agent is enabled.
        """
        return self._enabled

    # ======================================================
    # Execution
    # ======================================================

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Callable interface.
        """

        return self.execute(*args, **kwargs)

    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the agent.

        This wrapper checks lifecycle state before delegating
        to the concrete implementation.
        """

        if not self._enabled:
            raise RuntimeError(
                f"Agent '{self._name}' is disabled."
            )

        self._executions += 1

        return self.run(*args, **kwargs)

    @abstractmethod
    def run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Agent-specific implementation.

        Must be implemented by subclasses.
        """

    # ======================================================
    # Status
    # ======================================================

    def status(self) -> dict[str, Any]:
        """
        Return runtime status.
        """

        return {
            "name": self._name,
            "version": self._version,
            "enabled": self._enabled,
            "executions": self._executions,
            "created_at": self._created_at,
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self._name}', "
            f"enabled={self._enabled}, "
            f"executions={self._executions})"
        )
