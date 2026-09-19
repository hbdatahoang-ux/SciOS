from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class PlannerInterface(ABC):
    """Abstract contract for the planning subsystem."""

    @abstractmethod
    def plan(self, task: Any) -> dict[str, Any]:
        """Generate a plan for a task."""
        raise NotImplementedError


class ReasonerInterface(ABC):
    """Abstract contract for the reasoning subsystem."""

    @abstractmethod
    def infer(self, context: dict[str, Any]) -> list[str]:
        """Perform inference using the supplied context."""
        raise NotImplementedError


class MemoryInterface(ABC):
    """Abstract contract for the memory subsystem."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a value under a key."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve a value by key."""
        raise NotImplementedError


class ToolInterface(Protocol):
    """Structural contract for external tools."""

    def __call__(self, **inputs: Any) -> Any:
        """Invoke the tool with keyword arguments."""
        ...