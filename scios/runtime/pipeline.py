"""
SciOS Runtime Pipeline
======================

Pipeline orchestration layer.
"""

from __future__ import annotations

from typing import Iterable

from .context import ExecutionContext
from .stage import Stage


__all__ = [
    "Pipeline",
]



class Pipeline:
    """
    Sequential execution pipeline.
    """


    def __init__(
        self,
        stages: Iterable[Stage] | None = None,
    ) -> None:


        self._stages: list[Stage] = (
            list(stages)
            if stages
            else []
        )



    # ==================================================
    # Stage Management
    # ==================================================

    def add_stage(
        self,
        stage: Stage,
    ) -> None:

        self._stages.append(
            stage
        )



    def remove_stage(
        self,
        stage: Stage,
    ) -> None:

        self._stages.remove(
            stage
        )



    def clear(
        self,
    ) -> None:

        self._stages.clear()



    @property
    def stages(
        self,
    ) -> tuple[Stage,...]:

        return tuple(
            self._stages
        )



    def __len__(
        self,
    ) -> int:

        return len(
            self._stages
        )



    # ==================================================
    # Execution
    # ==================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Execute stages sequentially.
        """


        context.add_event(
            "pipeline.started"
        )


        context.log(
            "Pipeline started"
        )


        for stage in self._stages:


            context.add_event(
                f"{stage.name}.started"
            )


            context.log(
                f"Executing stage: {stage.name}"
            )


            stage.execute(
                context
            )


            context.add_event(
                f"{stage.name}.completed"
            )



        context.add_event(
            "pipeline.completed"
        )


        context.log(
            "Pipeline completed"
        )


        return context



    # ==================================================
    # Diagnostics
    # ==================================================

    def summary(
        self,
    ) -> dict:


        return {

            "stage_count":
                len(self._stages),

            "stages":
            [
                stage.name
                for stage in self._stages
            ]

        }



    def __repr__(
        self,
    ) -> str:

        return (
            "Pipeline("
            f"stages={len(self._stages)}"
            ")"
        )