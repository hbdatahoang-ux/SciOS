"""
SciOS Embedding
===============

Backend-independent embedding abstraction for the SciOS
VectorStore.

Responsibilities
----------------
- Embedding provider abstraction
- Text embedding
- Batch embedding
- Dimension reporting
- Backend independence
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from scios.substrate.tensor import SciOSTensor

__all__ = [
    "EmbeddingResult",
    "EmbeddingProvider",
]


# ==========================================================
# Embedding Result
# ==========================================================

@dataclass(slots=True)
class EmbeddingResult:
    """
    Result returned by an embedding provider.
    """

    vector: SciOSTensor

    model: str

    dimension: int

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:

        return {

            "model": self.model,

            "dimension": self.dimension,

            "metadata": self.metadata,
        }


# ==========================================================
# Abstract Embedding Provider
# ==========================================================

class EmbeddingProvider(ABC):
    """
    Abstract embedding provider.

    Concrete implementations may use local models,
    cloud APIs, or custom embedding engines.
    """

    def __init__(
        self,
        model: str,
    ) -> None:

        self._model = model

    # ======================================================

    @property
    def model(self) -> str:
        """
        Provider model name.
        """

        return self._model

    # ======================================================

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Embedding dimension.
        """
        raise NotImplementedError

    # ======================================================

    @abstractmethod
    def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Embed a single text.
        """
        raise NotImplementedError

    # ======================================================

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """
        Embed multiple texts.

        Default implementation processes sequentially.
        Providers may override for optimized batching.
        """

        return [

            self.embed(text)

            for text in texts

        ]

    # ======================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"model='{self.model}', "

            f"dimension={self.dimension})"

        )
