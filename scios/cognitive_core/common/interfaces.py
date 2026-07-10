from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Protocol


# ==========================================================
# Planner
# ==========================================================

class PlannerInterface(ABC):
    """
    PlannerInterface = Abstract contract for planning tasks.
    """

    @abstractmethod
    def plan(self, task: Any) -> dict[str, Any]:
        """
        Generate a plan for a given task.
        """
        raise NotImplementedError


# ==========================================================
# Reasoner
# ==========================================================

class ReasonerInterface(ABC):
    """
    ReasonerInterface = Abstract contract for reasoning engine.
    """

    @abstractmethod
    def infer(self, context: dict[str, Any]) -> list[str]:
        """
        Perform inference given a context.
        """
        raise NotImplementedError


# ==========================================================
# Memory
# ==========================================================

class MemoryInterface(ABC):
    """
    MemoryInterface = Abstract contract for memory subsystem.
    """

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """
        Store a value in memory.
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """
        Retrieve a value from memory.
        """
        raise NotImplementedError


# ==========================================================
# Tool
# ==========================================================

class ToolInterface(Protocol):
    """
    ToolInterface = Protocol for external tools.
    """

    def __call__(self, **inputs: Any) -> Any:
        ...
