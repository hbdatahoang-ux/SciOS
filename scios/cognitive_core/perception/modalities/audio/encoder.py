"""Audio encoding for the SciOS Cognitive Core audio modality."""

from __future__ import annotations

import hashlib
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_EMBEDDING_DIMENSION = 32


class AudioEncoder:
    """Produce deterministic embeddings from audio bytes."""

    def validate_input(self, data: Any) -> None:
        """Validate raw audio bytes accepted by the encoder."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "audio encoding input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "audio encoding input must not be empty"
            )

    def encode(self, data: bytes) -> dict[str, Any]:
        """Encode audio bytes into a deterministic embedding."""

        self.validate_input(data)

        try:
            digest = hashlib.sha256(data).digest()

            embedding: list[float] = []

            for index in range(_EMBEDDING_DIMENSION):
                byte_value = digest[index % len(digest)]
                embedding.append(byte_value / 255.0)

            return {
                "embedding": embedding,
                "metadata": {
                    "backend": "deterministic",
                    "dimension": _EMBEDDING_DIMENSION,
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "audio encoding failed"
            ) from exc


__all__ = ["AudioEncoder"]
