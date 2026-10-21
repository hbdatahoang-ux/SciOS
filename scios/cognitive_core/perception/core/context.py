"""Context passed from perception into the SciOS Cognitive Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .result import PerceptionResult
from .types import Metadata, Modality, RawInput


@dataclass
class PerceptionContext:
    """Standard cognitive context produced by the perception layer."""

    raw_input: RawInput
    modality: Modality
    result: PerceptionResult
    metadata: Metadata = field(default_factory=dict)
    context_id: str | None = None

    @property
    def successful(self) -> bool:
        """Return whether the underlying perception succeeded."""

        return self.result.successful

    @property
    def partial(self) -> bool:
        """Return whether the underlying perception was partial."""

        return self.result.partial

    @property
    def failed(self) -> bool:
        """Return whether the underlying perception failed."""

        return self.result.failed

    @property
    def confidence(self) -> float:
        """Return the confidence of the underlying perception result."""

        return self.result.confidence

    def validate(self) -> None:
        """Validate the context and its underlying perception result."""

        if not isinstance(self.modality, Modality):
            raise TypeError("modality must be a Modality")

        if not isinstance(self.result, PerceptionResult):
            raise TypeError("result must be a PerceptionResult")

        if self.result.modality is not self.modality:
            raise ValueError(
                "context modality must match result modality"
            )

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

        self.result.validate()

    def to_dict(self) -> dict[str, Any]:
        """Return a structural representation of the context."""

        return {
            "raw_input": self.raw_input,
            "modality": self.modality.value,
            "result": self.result.to_dict(),
            "metadata": self.metadata,
            "context_id": self.context_id,
        }


__all__ = ["PerceptionContext"]