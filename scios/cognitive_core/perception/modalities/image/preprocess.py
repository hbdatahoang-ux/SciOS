"""Image preprocessing for the SciOS Cognitive Core image modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class ImagePreprocessor:
    """Validate and normalize image data without external dependencies."""

    def validate_input(self, data: Any) -> None:
        """Validate raw image bytes."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "image preprocessing input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "image preprocessing input must not be empty"
            )

        self._detect_format(data)

    def preprocess(self, data: bytes) -> dict[str, Any]:
        """Preprocess image bytes into a deterministic representation."""

        self.validate_input(data)

        try:
            image_format = self._detect_format(data)

            return {
                "content": data,
                "metadata": {
                    "format": image_format,
                    "original_size": len(data),
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "image preprocessing failed"
            ) from exc

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
            "image preprocessing input has an unsupported "
            "or invalid image format"
        )


__all__ = ["ImagePreprocessor"]
