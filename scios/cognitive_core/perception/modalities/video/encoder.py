"""Video encoding for the SciOS Cognitive Core video modality."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class VideoEncoder:
    """Encode processed video frames into a deterministic embedding."""

    DIMENSION = 32

    def validate_input(self, data: Any) -> None:
        """Validate a processed frame representation."""

        if not isinstance(data, dict):
            raise PerceptionInputError(
                "video encoding input must be a dictionary"
            )

        if "frames" not in data:
            raise PerceptionInputError(
                "video encoding input must contain frames"
            )

        if not isinstance(data["frames"], list):
            raise PerceptionInputError(
                "video encoding frames must be a list"
            )

        if "frame_count" not in data:
            raise PerceptionInputError(
                "video encoding input must contain frame_count"
            )

        if not isinstance(data["frame_count"], int):
            raise PerceptionInputError(
                "video encoding frame_count must be an integer"
            )

        if data["frame_count"] < 0:
            raise PerceptionInputError(
                "video encoding frame_count must not be negative"
            )

        if data["frame_count"] != len(data["frames"]):
            raise PerceptionInputError(
                "video encoding frame_count must match frames length"
            )

    def encode(self, data: dict[str, Any]) -> dict[str, Any]:
        """Encode processed frames into a deterministic 32-value embedding."""

        self.validate_input(data)

        try:
            canonical = json.dumps(
                {
                    "frames": data["frames"],
                    "frame_count": data["frame_count"],
                },
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")

            digest = hashlib.sha256(canonical).digest()

            embedding = [
                byte / 255.0
                for byte in digest
            ]

            return {
                "embedding": embedding,
                "dimension": self.DIMENSION,
                "metadata": {
                    "backend": "deterministic",
                    "algorithm": "sha256",
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "video encoding failed"
            ) from exc


__all__ = ["VideoEncoder"]
