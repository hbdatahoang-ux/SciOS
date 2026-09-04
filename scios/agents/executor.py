from __future__ import annotations

from typing import Any

from scios.cognitive_core.memory import (
    KeywordRetrieval,
    MemoryKind,
    MemoryManager,
)
from scios.cognitive_core.reasoning.core import (
    ReasoningProblem,
)
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.engine import ReasoningEngine


__all__ = ["AgentExecutor"]


class AgentExecutor:
    def __init__(
        self,
        *,
        memory: MemoryManager,
        reasoning: ReasoningEngine,
    ) -> None:
        if not isinstance(memory, MemoryManager):
            raise TypeError("memory must be a MemoryManager")

        if not isinstance(reasoning, ReasoningEngine):
            raise TypeError("reasoning must be a ReasoningEngine")

        self.memory = memory
        self.reasoning = reasoning
        self._retrieval = KeywordRetrieval()

    def execute(self, task: str) -> dict[str, Any]:
        problem = ReasoningProblem(
            query=task,
            context={},
            reasoning_type=ReasoningType.DEDUCTIVE,
        )

        memory = self.memory.retrieve(
            self._retrieval,
            task,
            MemoryKind.SEMANTIC,
        )

        problem.context["memory"] = memory

        reasoning = self.reasoning.execute(problem)

        tools = self._tool_use(task, reasoning)
        reflection = self._reflect(reasoning)

        return {
            "task": task,
            "plan": self._plan(task),
            "memory": memory,
            "reasoning": reasoning,
            "tools": tools,
            "reflection": reflection,
            "response": (
                reasoning.conclusion
                if reasoning.conclusion is not None
                else f"processed: {task}"
            ),
        }

    def _plan(self, task: str) -> dict[str, Any]:
        return {
            "steps": [
                "retrieve_memory",
                "reason",
                "respond",
            ]
        }

    def _tool_use(
        self,
        task: str,
        reasoning: Any,
    ) -> list[Any]:
        return []

    def _reflect(self, reasoning: Any) -> dict[str, Any]:
        return {
            "accepted": reasoning.accepted,
            "confidence": 1.0 if reasoning.accepted else 0.0,
        }

    def status(self) -> dict[str, Any]:
        return {
            "memory": self.memory.__class__.__name__,
            "reasoning": self.reasoning.__class__.__name__,
            "planner": "placeholder",
            "tooluse": "placeholder",
            "reflection": "placeholder",
        }

    def __call__(self, task: str) -> dict[str, Any]:
        return self.execute(task)

    def __repr__(self) -> str:
        return (
            "AgentExecutor("
            f"memory={self.memory.__class__.__name__}, "
            f"reasoning={self.reasoning.__class__.__name__})"
        )
