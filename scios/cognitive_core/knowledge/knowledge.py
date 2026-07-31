"""
SciOS Knowledge Stage
=====================

Provides a pipeline stage for knowledge retrieval and reasoning.

Python 3.11+
"""

from __future__ import annotations

from typing import Any


from scios.cognitive_core.pipeline.stage import (
    PipelineStage,
)


__all__ = [
    "KnowledgeStage",
]



class KnowledgeStage(PipelineStage):
    """
    Knowledge retrieval pipeline stage.
    """


    def __init__(self) -> None:

        super().__init__(
            name="knowledge",
            handler=self.execute,
        )



    def execute(
        self,
        context: dict[str, Any] | str,
    ) -> dict[str, Any]:
        """
        Execute knowledge retrieval.

        Accept:
        - dict context
        - raw string query
        """

        # Normalize input

        if isinstance(
            context,
            str,
        ):

            task = context

            base_context = {}

        else:

            task = context.get(
                "task",
                "",
            )

            base_context = context



        knowledge_output = (
            f"retrieved knowledge for '{task}'"
        )


        return {

            **base_context,

            "query": task,

            "output": knowledge_output,

            "status": "completed",

        }



        # ----------------------------------------------
        # Knowledge retrieval simulation
        # ----------------------------------------------

        knowledge_output = (
            f"retrieved knowledge for '{task}'"
        )



        return {

            **base_context,


            "knowledge": {

                "query": task,

                "output": knowledge_output,

                "status": "completed",

            },

        }



    def run(
        self,
        context: dict[str, Any] | str,
    ) -> dict[str, Any]:
        """
        Pipeline compatibility API.
        """

        return self.execute(
            context
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "KnowledgeStage("
            "name='knowledge'"
            ")"
        )