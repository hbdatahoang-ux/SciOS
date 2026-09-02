"""Video feature extraction for the SciOS Cognitive Core video modality."""

from __future__ import annotations

from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class VideoExtractor:
    """Extract deterministic structural features from processed frames."""

    def validate_input(self, data: Any) -> None:
        """Validate a processed frame representation."""

        if not isinstance(data, dict):
            raise PerceptionInputError(
                "video extraction input must be a dictionary"
            )

        if "frames" not in data:
            raise PerceptionInputError(
                "video extraction input must contain frames"
            )

        if not isinstance(data["frames"], list):
            raise PerceptionInputError(
                "video extraction frames must be a list"
            )

        if "frame_count" not in data:
            raise PerceptionInputError(
                "video extraction input must contain frame_count"
            )

        if not isinstance(data["frame_count"], int):
            raise PerceptionInputError(
                "video extraction frame_count must be an integer"
            )

        if data["frame_count"] < 0:
            raise PerceptionInputError(
                "video extraction frame_count must not be negative"
            )

        if data["frame_count"] != len(data["frames"]):
            raise PerceptionInputError(
                "video extraction frame_count must match frames length"
            )

    def extract(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract deterministic structural features from processed frames."""

        self.validate_input(data)

        try:
            frames = data["frames"]
            frame_count = data["frame_count"]

            has_frames = bool(frames)

            first_frame_index = None
            last_frame_index = None

            if has_frames:
                first_frame_index = frames[0].get("index")
                last_frame_index = frames[-1].get("index")

            return {
                "frame_count": frame_count,
                "first_frame_index": first_frame_index,
                "last_frame_index": last_frame_index,
                "has_frames": has_frames,
                "features": {
                    "frame_count": frame_count,
                    "has_frames": has_frames,
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "video feature extraction failed"
            ) from exc


__all__ = ["VideoExtractor"]
