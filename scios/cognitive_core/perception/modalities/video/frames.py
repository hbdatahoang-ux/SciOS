"""Video frame extraction for the SciOS Cognitive Core video modality."""

from __future__ import annotations

import hashlib
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class VideoFrameExtractor:
    """Produce a deterministic frame representation from video bytes."""

    def validate_input(self, data: Any) -> None:
        """Validate raw video bytes."""

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "video frame extraction input must be bytes"
            )

        if not data:
            raise PerceptionInputError(
                "video frame extraction input must not be empty"
            )

    def extract(self, data: bytes) -> dict[str, Any]:
        """Extract a deterministic baseline frame representation."""

        self.validate_input(data)

        try:
            digest = hashlib.sha256(data).hexdigest()

            frame = {
                "index": 0,
                "identifier": digest,
            }

            return {
                "frames": [frame],
                "frame_count": 1,
                "metadata": {
                    "backend": "deterministic",
                },
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "video frame extraction failed"
            ) from exc


__all__ = ["VideoFrameExtractor"]
