"""Perception engine for the SciOS Cognitive Core."""

from __future__ import annotations

from ..core.result import PerceptionResult
from ..core.types import Metadata, RawInput
from ..factory.factory import PerceptorFactory
from .pipeline import PerceptionPipeline


class PerceptionEngine:
    """Coordinate perception execution through factory and pipeline."""

    def __init__(
        self,
        factory: PerceptorFactory,
        pipeline: PerceptionPipeline | None = None,
    ) -> None:
        """Initialize the perception engine."""

        if not isinstance(factory, PerceptorFactory):
            raise TypeError("factory must be a PerceptorFactory")

        if pipeline is not None and not isinstance(
            pipeline,
            PerceptionPipeline,
        ):
            raise TypeError("pipeline must be a PerceptionPipeline")

        self.factory = factory
        self.pipeline = pipeline

    def perceive(
        self,
        name: str,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Run a named perceptor against raw input."""

        perceptor = self.factory.create(name)

        return perceptor.perceive(
            raw_input,
            metadata,
        )

    def perceive_pipeline(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Run the configured perception pipeline."""

        if self.pipeline is None:
            raise RuntimeError("no perception pipeline configured")

        return self.pipeline.run(
            raw_input,
            metadata,
        )


__all__ = ["PerceptionEngine"]
