"""Audio loader for the SciOS Cognitive Core audio modality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_SUPPORTED_EXTENSIONS = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".flac": "flac",
    ".ogg": "ogg",
    ".m4a": "m4a",
    ".aac": "aac",
}


class AudioLoader:
    """Load supported audio sources into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported audio source."""

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "audio source bytes must not be empty"
                )
            return

        if isinstance(source, Path):
            self._validate_path(source)
            return

        if isinstance(source, str):
            if not source:
                raise PerceptionInputError(
                    "audio source string must not be empty"
                )

            self._validate_path(Path(source))
            return

        raise PerceptionInputError(
            "audio source must be a path or bytes"
        )

    def load(self, source: str | Path | bytes) -> dict[str, Any]:
        """Load an audio source into a structured representation."""

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                data = source
                source_name = None
                audio_format = self._detect_format_from_bytes(data)

            else:
                path = Path(source)
                data = path.read_bytes()
                source_name = path.name
                audio_format = self._detect_format_from_path(path)

                detected_format = self._detect_format_from_bytes(data)

                if detected_format != audio_format:
                    raise PerceptionInputError(
                        "audio content does not match file extension"
                    )

            return {
                "content": data,
                "metadata": {
                    "source_name": source_name,
                    "format": audio_format,
                },
            }

        except PerceptionInputError:
            raise
        except OSError as exc:
            raise PerceptionProcessingError(
                "audio loading failed"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "audio loading failed"
            ) from exc

    @staticmethod
    def _validate_path(path: Path) -> None:
        """Validate an audio file path."""

        if not path.exists():
            raise PerceptionInputError(
                f"audio source does not exist: {path}"
            )

        if not path.is_file():
            raise PerceptionInputError(
                f"audio source is not a file: {path}"
            )

        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise PerceptionInputError(
                "audio source must have a supported audio extension"
            )

    @staticmethod
    def _detect_format_from_path(path: Path) -> str:
        """Detect audio format from a file extension."""

        try:
            return _SUPPORTED_EXTENSIONS[path.suffix.lower()]
        except KeyError as exc:
            raise PerceptionInputError(
                "audio source must have a supported audio extension"
            ) from exc

    @staticmethod
    def _detect_format_from_bytes(data: bytes) -> str:
        """Detect audio format from common file signatures."""

        if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
            return "wav"

        if data.startswith(b"ID3") or data.startswith(
            (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
        ):
            return "mp3"

        if data.startswith(b"fLaC"):
            return "flac"

        if data.startswith(b"OggS"):
            return "ogg"

        if len(data) >= 8 and data[4:8] == b"ftyp":
            brand = data[8:12]

            if brand in {
                b"M4A ",
                b"m4a ",
                b"mp42",
                b"mp41",
            }:
                return "m4a"

        if data.startswith(b"ADIF"):
            return "aac"

        if len(data) >= 2 and data[0] == 0xFF:
            second = data[1]

            if second & 0xF6 == 0xF0:
                return "aac"

        raise PerceptionInputError(
            "audio source has an unsupported or invalid audio format"
        )


__all__ = ["AudioLoader"]
