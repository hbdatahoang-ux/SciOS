"""Image encoder for the SciOS Cognitive Core image modality."""

from __future__ import annotations

import hashlib
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_EMBEDDING_DIMENSION = 32


class ImageEncoder:
    """Encode image bytes into a deterministic baseline representation."""

    def validate_input(self, data: Any) -> None:
        """Validate image bytes accepted by the encoder."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "image encoding input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "image encoding input must not be empty"
            )

        self._detect_format(data)

    def encode(self, data: bytes) -> dict[str, Any]:
        """Encode image bytes into a deterministic embedding."""

        self.validate_input(data)

        try:
            image_format = self._detect_format(data)
            embedding = self._create_embedding(data)

            return {
                "embedding": embedding,
                "metadata": {
                    "format": image_format,
                    "backend": "deterministic",
                    "dimension": _EMBEDDING_DIMENSION,
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "image encoding failed"
            ) from exc

    @staticmethod
    def _create_embedding(data: bytes) -> tuple[float, ...]:
        """Create a deterministic fixed-size representation from image bytes."""

        digest = hashlib.sha256(data).digest()

        values: list[float] = []

        for index in range(_EMBEDDING_DIMENSION):
            byte_value = digest[index % len(digest)]
            values.append(byte_value / 255.0)

        return tuple(values)

    @staticmethod
    def _detect_format(data: bytes) -> str:
        """Detect image format from common file signatures."""

        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "png"

        if data.startswith(b"\xff\xd8\xff"):
            return "jpeg"

        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return "webp"

        if data.startswith(b"BM"):
            return "bmp"

        if data.startswith((b"GIF87a", b"GIF89a")):
            return "gif"

        raise PerceptionInputError(
            "image encoding input has an unsupported "
            "or invalid image format"
        )


__all__ = ["ImageEncoder"]
