"""Base perceptor contract for the SciOS Cognitive Core."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .result import PerceptionResult
from .types import Metadata, Modality, RawInput


class BasePerceptor(ABC):
    """Abstract base class for all perception modality implementations."""

    name: str
    modality: Modality

    def __init__(
        self,
        *,
        name: str,
        modality: Modality,
    ) -> None:
        """Initialize a perceptor with its identity and modality."""

        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")

        if not isinstance(modality, Modality):
            raise TypeError("modality must be a Modality")

        self.name = name
        self.modality = modality

    @abstractmethod
    def perceive(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Transform raw input into a standardized perception result."""

        raise NotImplementedError


__all__ = ["BasePerceptor"]
