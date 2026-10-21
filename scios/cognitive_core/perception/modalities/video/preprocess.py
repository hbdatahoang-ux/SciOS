"""Video preprocessing for the SciOS Cognitive Core video modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class VideoPreprocessor:
    """Validate and normalize extracted video frames."""

    def validate_input(self, data: Any) -> None:
        """Validate a structured frame extraction result."""

        if not isinstance(data, dict):
            raise PerceptionInputError(
                "video preprocessing input must be a dictionary"
            )

        if "frames" not in data:
            raise PerceptionInputError(
                "video preprocessing input must contain frames"
            )

        if not isinstance(data["frames"], list):
            raise PerceptionInputError(
                "video preprocessing frames must be a list"
            )

        if "frame_count" not in data:
            raise PerceptionInputError(
                "video preprocessing input must contain frame_count"
            )

        if not isinstance(data["frame_count"], int):
            raise PerceptionInputError(
                "video preprocessing frame_count must be an integer"
            )

        if data["frame_count"] < 0:
            raise PerceptionInputError(
                "video preprocessing frame_count must not be negative"
            )

        if data["frame_count"] != len(data["frames"]):
            raise PerceptionInputError(
                "video preprocessing frame_count must match frames length"
            )

    def preprocess(self, data: dict[str, Any]) -> dict[str, Any]:
        """Preprocess extracted frames into a deterministic representation."""

        self.validate_input(data)

        try:
            frames = list(data["frames"])
            frame_count = data["frame_count"]

            return {
                "frames": frames,
                "frame_count": frame_count,
                "metadata": {
                    "backend": "deterministic",
                    "frame_count": frame_count,
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "video preprocessing failed"
            ) from exc


__all__ = ["VideoPreprocessor"]
