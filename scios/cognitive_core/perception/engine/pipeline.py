"""Perception pipeline for the SciOS Cognitive Core."""

from __future__ import annotations

from collections.abc import Sequence

from ..core.base import BasePerceptor
from ..core.result import PerceptionResult
from ..core.types import Metadata, RawInput


class PerceptionPipeline:
    """Sequential pipeline of perception components."""

    def __init__(
        self,
        perceptors: Sequence[BasePerceptor] | None = None,
    ) -> None:
        """Initialize the pipeline with optional perceptors."""

        self._perceptors: list[BasePerceptor] = []

        if perceptors is not None:
            for perceptor in perceptors:
                self.add(perceptor)

    @property
    def perceptors(self) -> tuple[BasePerceptor, ...]:
        """Return the registered pipeline perceptors."""

        return tuple(self._perceptors)

    def add(self, perceptor: BasePerceptor) -> BasePerceptor:
        """Append a perceptor to the pipeline."""

        if not isinstance(perceptor, BasePerceptor):
            raise TypeError("perceptor must be a BasePerceptor")

        self._perceptors.append(perceptor)
        return perceptor

    def remove(self, name: str) -> BasePerceptor:
        """Remove and return the first perceptor matching name."""

        for index, perceptor in enumerate(self._perceptors):
            if perceptor.name == name:
                return self._perceptors.pop(index)

        raise KeyError(f"perceptor not found in pipeline: {name}")

    def clear(self) -> None:
        """Remove all perceptors from the pipeline."""

        self._perceptors.clear()

    def run(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Run the input through the complete pipeline."""

        if not self._perceptors:
            raise RuntimeError("cannot run an empty perception pipeline")

        current_input = raw_input
        current_metadata = dict(metadata or {})
        result: PerceptionResult | None = None

        for perceptor in self._perceptors:
            result = perceptor.perceive(
                current_input,
                current_metadata,
            )

            current_input = result.content
            current_metadata.update(result.metadata)

        assert result is not None
        return result

    def __len__(self) -> int:
        """Return the number of perceptors in the pipeline."""

        return len(self._perceptors)


__all__ = ["PerceptionPipeline"]
