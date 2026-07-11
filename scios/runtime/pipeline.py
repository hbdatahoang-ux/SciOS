"""
SciOS Runtime Pipeline
======================

Pipeline orchestration for the SciOS Runtime.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .context import ExecutionContext


class Stage(ABC):
    """
    Base class for all runtime pipeline stages.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def execute(self, context: ExecutionContext) -> None:
        """
        Execute the stage.
        """
        raise NotImplementedError


class Pipeline:
    """
    Sequential execution pipeline.
    """

    def __init__(self, stages: Iterable[Stage] | None = None) -> None:
        self._stages: list[Stage] = list(stages) if stages else []

    def add_stage(self, stage: Stage) -> None:
        """Append a stage to the pipeline."""
        self._stages.append(stage)

    def remove_stage(self, stage: Stage) -> None:
        """Remove a stage."""
        self._stages.remove(stage)

    def clear(self) -> None:
        """Remove all stages."""
        self._stages.clear()

    @property
    def stages(self) -> tuple[Stage, ...]:
        """Read-only view of configured stages."""
        return tuple(self._stages)

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        """
        Execute all stages sequentially.
        """

        context.log("Pipeline started")

        for stage in self._stages:

            context.add_event(f"{stage.name}.started")
            context.log(f"Executing stage: {stage.name}")

            stage.execute(context)

            context.add_event(f"{stage.name}.completed")

        context.log("Pipeline completed")

        return context