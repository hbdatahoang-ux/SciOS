"""
SciOS Knowledge Stage
=====================

Provides a pipeline stage for knowledge retrieval and reasoning.
"""

from __future__ import annotations
from scios.cognitive_core.pipeline.stage import PipelineStage


class KnowledgeStage(PipelineStage):
    """
    KnowledgeStage simulates knowledge retrieval.
    For demo purposes, it echoes back the task as 'knowledge'.
    """

    def __init__(self) -> None:
        super().__init__("knowledge")

    def execute(self, context) -> dict:
        """
        Execute knowledge retrieval on the given context.
        """
        task = context.get("task")

        # Demo: giả lập tri thức bằng cách trả về chuỗi mô tả
        knowledge_output = f"retrieved knowledge for '{task}'"

        return {
            "input": task,
            "output": knowledge_output,
        }
