"""Audio preprocessing for the SciOS Cognitive Core audio modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class AudioPreprocessor:
    """Validate and normalize audio data without external dependencies."""

    def validate_input(self, data: Any) -> None:
        """Validate raw audio bytes."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "audio preprocessing input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "audio preprocessing input must not be empty"
            )

        self._detect_format(data)

    def preprocess(self, data: bytes) -> dict[str, Any]:
        """Preprocess audio bytes into a deterministic representation."""

        self.validate_input(data)

        try:
            audio_format = self._detect_format(data)

            return {
                "content": data,
                "metadata": {
                    "format": audio_format,
                    "original_size": len(data),
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "audio preprocessing failed"
            ) from exc

    @staticmethod
    def _detect_format(data: bytes) -> str:
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

        if len(data) >= 12 and data[4:8] == b"ftyp":
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
            "audio preprocessing input has an unsupported "
            "or invalid audio format"
        )


__all__ = ["AudioPreprocessor"]
