"""
SciOS Memory Stage
==================

Provides a pipeline stage for memory storage and retrieval.
"""

from __future__ import annotations
from scios.cognitive_core.pipeline.stage import PipelineStage


class MemoryStage(PipelineStage):
    """
    MemoryStage simulates memory operations.
    For demo purposes, it stores tasks into context memory.
    """

    def __init__(self) -> None:
        super().__init__("memory")
        self._memory_store: list[str] = []

    def execute(self, context) -> dict:
        """
        Execute memory operations on the given context.
        """
        task = context.get("task")

        # Lưu task vào bộ nhớ
        self._memory_store.append(task)

        # Trả về trạng thái bộ nhớ
        return {
            "input": task,
            "stored": True,
            "memory_size": len(self._memory_store),
            "memory_snapshot": list(self._memory_store),
        }

    def clear(self) -> None:
        """
        Clear memory store.
        """
        self._memory_store.clear()
