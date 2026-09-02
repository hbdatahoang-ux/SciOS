"""Speech processing for the SciOS Cognitive Core audio modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class SpeechProcessor:
    """Provide a backend-independent speech transcription contract."""

    def validate_input(self, data: Any) -> None:
        """Validate audio data accepted by the speech processor."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "speech processing input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "speech processing input must not be empty"
            )

    def transcribe(self, data: bytes) -> dict[str, Any]:
        """Transcribe audio using the deterministic baseline backend."""

        self.validate_input(data)

        try:
            return {
                "text": "",
                "segments": [],
                "metadata": {
                    "backend": "deterministic",
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "speech transcription failed"
            ) from exc


__all__ = ["SpeechProcessor"]
