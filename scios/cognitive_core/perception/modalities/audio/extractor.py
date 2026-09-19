"""Audio feature extraction for the SciOS Cognitive Core audio modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class AudioExtractor:
    """Extract deterministic structural features from speech results."""

    def validate_input(self, data: Any) -> None:
        """Validate a structured speech result."""

        if not isinstance(data, dict):
            raise PerceptionInputError(
                "audio extraction input must be a dictionary"
            )

        if "text" not in data:
            raise PerceptionInputError(
                "audio extraction input must contain text"
            )

        if not isinstance(data["text"], str):
            raise PerceptionInputError(
                "audio extraction text must be a string"
            )

        if "segments" in data and not isinstance(
            data["segments"],
            list,
        ):
            raise PerceptionInputError(
                "audio extraction segments must be a list"
            )

    def extract(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract deterministic features from a speech result."""

        self.validate_input(data)

        try:
            text = data["text"]
            segments = data.get("segments", [])

            words = text.split()

            return {
                "features": {
                    "text_length": len(text),
                    "segment_count": len(segments),
                    "word_count": len(words),
                },
                "entities": [],
                "relations": [],
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "audio feature extraction failed"
            ) from exc


__all__ = ["AudioExtractor"]
