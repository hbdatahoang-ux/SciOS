"""Video loader for the SciOS Cognitive Core video modality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_SUPPORTED_EXTENSIONS = {
    ".mp4": "mp4",
    ".mov": "mov",
    ".avi": "avi",
    ".webm": "webm",
    ".mkv": "mkv",
}


class VideoLoader:
    """Load supported video containers into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported video source."""

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "video source bytes must not be empty"
                )
            return

        if isinstance(source, Path):
            self._validate_path(source)
            return

        if isinstance(source, str):
            if not source:
                raise PerceptionInputError(
                    "video source string must not be empty"
                )

            self._validate_path(Path(source))
            return

        raise PerceptionInputError(
            "video source must be a path or bytes"
        )

    def load(self, source: str | Path | bytes) -> dict[str, Any]:
        """Load a video source into a structured representation."""

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                data = source
                source_name = None
                video_format = self._detect_format_from_bytes(data)

            else:
                path = Path(source)
                data = path.read_bytes()
                source_name = path.name
                video_format = self._detect_format_from_path(path)

                detected_format = self._detect_format_from_bytes(data)

                if detected_format != video_format:
                    raise PerceptionInputError(
                        "video content does not match file extension"
                    )

            return {
                "content": data,
                "metadata": {
                    "source_name": source_name,
                    "format": video_format,
                },
            }

        except PerceptionInputError:
            raise
        except OSError as exc:
            raise PerceptionProcessingError(
                "video loading failed"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "video loading failed"
            ) from exc

    @staticmethod
    def _validate_path(path: Path) -> None:
        """Validate a video file path."""

        if not path.exists():
            raise PerceptionInputError(
                f"video source does not exist: {path}"
            )

        if not path.is_file():
            raise PerceptionInputError(
                f"video source is not a file: {path}"
            )

        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise PerceptionInputError(
                "video source must have a supported video extension"
            )

    @staticmethod
    def _detect_format_from_path(path: Path) -> str:
        """Detect video format from a file extension."""

        try:
            return _SUPPORTED_EXTENSIONS[path.suffix.lower()]
        except KeyError as exc:
            raise PerceptionInputError(
                "video source must have a supported video extension"
            ) from exc

    @staticmethod
    def _detect_format_from_bytes(data: bytes) -> str:
        """Detect video format from common container signatures."""

        if len(data) >= 12 and data[4:8] == b"ftyp":
            brand = data[8:12]

            if brand in {
                b"isom",
                b"iso2",
                b"mp41",
                b"mp42",
                b"avc1",
                b"MSNV",
            }:
                return "mp4"

            if brand in {
                b"qt  ",
            }:
                return "mov"

        if len(data) >= 12 and data.startswith(b"RIFF"):
            if data[8:12] == b"AVI ":
                return "avi"

        if data.startswith(b"\x1A\x45\xDF\xA3"):
            if b"webm" in data[:64].lower():
                return "webm"

            if b"matroska" in data[:64].lower():
                return "mkv"

        raise PerceptionInputError(
            "video source has an unsupported or invalid video format"
        )


__all__ = ["VideoLoader"]
