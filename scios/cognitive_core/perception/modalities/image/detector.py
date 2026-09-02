"""Image detection for the SciOS Cognitive Core image modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class ImageDetector:
    """Provide a deterministic detection contract for image data."""

    def validate_input(self, data: Any) -> None:
        """Validate image bytes accepted by the detector."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "image detection input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "image detection input must not be empty"
            )

        self._detect_format(data)

    def detect(self, data: bytes) -> dict[str, Any]:
        """Detect image structures using the current deterministic backend."""

        self.validate_input(data)

        try:
            image_format = self._detect_format(data)

            return {
                "detections": [],
                "count": 0,
                "metadata": {
                    "format": image_format,
                    "backend": "deterministic",
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "image detection failed"
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
            "image detection input has an unsupported "
            "or invalid image format"
        )


__all__ = ["ImageDetector"]
