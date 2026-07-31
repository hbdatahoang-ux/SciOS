"""
SciOS Cognitive Pipeline

Stage based execution pipeline.
"""

from __future__ import annotations

from typing import Any


class CognitivePipeline:
    """
    Executes cognitive stages sequentially.
    """


    def __init__(
        self,
        stages: list[Any] | None = None,
    ) -> None:

        self.stages = (
            stages
            if stages
            else []
        )


    def run(
        self,
        raw_input: Any,
        context: Any | None = None,
    ) -> dict[str, Any]:
        """
        Execute pipeline.

        Example:

            pipeline.run(
                "calculate 2+2"
            )
        """


        state = {

            "input":
                raw_input,

        }


        if context is not None:

            state["context"] = context



        for stage in self.stages:

            name = getattr(
                stage,
                "name",
                stage.__class__.__name__,
            )


            output = stage.run(
                raw_input
            )


            state[name.lower()] = output



        return state

        context.add_event(
            "pipeline.completed"
        )

        context.log(
            "Pipeline completed"
        )

        return context



    def add_stage(
        self,
        stage: Any,
    ) -> None:

        self.stages.append(
            stage
        )



    def summary(
        self,
    ) -> dict[str, Any]:

        return {

            "stages":
            [
                getattr(
                    s,
                    "name",
                    s.__class__.__name__,
                )
                for s in self.stages
            ]

        }