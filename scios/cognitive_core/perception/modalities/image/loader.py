"""Image loader for the SciOS Cognitive Core image modality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_SUPPORTED_EXTENSIONS = {
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".webp": "webp",
    ".bmp": "bmp",
    ".gif": "gif",
}


class ImageLoader:
    """Load supported image sources into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported image source."""

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "image source bytes must not be empty"
                )
            return

        if isinstance(source, Path):
            self._validate_path(source)
            return

        if isinstance(source, str):
            if not source:
                raise PerceptionInputError(
                    "image source string must not be empty"
                )

            self._validate_path(Path(source))
            return

        raise PerceptionInputError(
            "image source must be a path or bytes"
        )

    def load(self, source: str | Path | bytes) -> dict[str, Any]:
        """Load an image source into a structured representation."""

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                data = source
                source_name = None
                image_format = self._detect_format_from_bytes(data)

            else:
                path = Path(source)
                data = path.read_bytes()
                source_name = path.name
                image_format = self._detect_format_from_path(path)

                detected_format = self._detect_format_from_bytes(data)

                if detected_format != image_format:
                    raise PerceptionInputError(
                        "image content does not match file extension"
                    )

            return {
                "content": data,
                "metadata": {
                    "source_name": source_name,
                    "format": image_format,
                },
            }

        except PerceptionInputError:
            raise
        except OSError as exc:
            raise PerceptionProcessingError(
                "image loading failed"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "image loading failed"
            ) from exc

    @staticmethod
    def _validate_path(path: Path) -> None:
        """Validate an image file path."""

        if not path.exists():
            raise PerceptionInputError(
                f"image source does not exist: {path}"
            )

        if not path.is_file():
            raise PerceptionInputError(
                f"image source is not a file: {path}"
            )

        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise PerceptionInputError(
                "image source must have a supported image extension"
            )

    @staticmethod
    def _detect_format_from_path(path: Path) -> str:
        """Detect image format from a file extension."""

        try:
            return _SUPPORTED_EXTENSIONS[path.suffix.lower()]
        except KeyError as exc:
            raise PerceptionInputError(
                "image source must have a supported image extension"
            ) from exc

    @staticmethod
    def _detect_format_from_bytes(data: bytes) -> str:
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
            "image source has an unsupported or invalid image format"
        )


__all__ = ["ImageLoader"]
