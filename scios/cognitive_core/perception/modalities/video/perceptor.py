"""Video perceptor for the SciOS Cognitive Core video modality."""

from __future__ import annotations

from pathlib import Path

from ...core.base import BasePerceptor
from ...core.result import PerceptionResult
from ...core.types import (
    Metadata,
    Modality,
    PerceptionStatus,
)
from .encoder import VideoEncoder
from .extractor import VideoExtractor
from .frames import VideoFrameExtractor
from .loader import VideoLoader
from .preprocess import VideoPreprocessor


class VideoPerceptor(BasePerceptor):
    """Orchestrate the complete deterministic video perception pipeline."""

    def __init__(
        self,
        *,
        name: str = "video",
        loader: VideoLoader | None = None,
        frame_extractor: VideoFrameExtractor | None = None,
        preprocessor: VideoPreprocessor | None = None,
        extractor: VideoExtractor | None = None,
        encoder: VideoEncoder | None = None,
    ) -> None:
        """Initialize the video perception pipeline."""

        super().__init__(
            name=name,
            modality=Modality.VIDEO,
        )

        self.loader = loader or VideoLoader()
        self.frame_extractor = (
            frame_extractor or VideoFrameExtractor()
        )
        self.preprocessor = (
            preprocessor or VideoPreprocessor()
        )
        self.extractor = extractor or VideoExtractor()
        self.encoder = encoder or VideoEncoder()

    def perceive(
        self,
        raw_input: str | Path | bytes,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Perceive a video source and return a standardized result."""

        loaded = self.loader.load(raw_input)

        extracted_frames = self.frame_extractor.extract(
            loaded["content"]
        )

        processed = self.preprocessor.preprocess(
            extracted_frames
        )

        features_result = self.extractor.extract(
            processed
        )

        encoded = self.encoder.encode(
            processed
        )

        result_metadata = dict(metadata or {})
        result_metadata.update(loaded.get("metadata", {}))
        result_metadata.update(extracted_frames.get("metadata", {}))
        result_metadata.update(processed.get("metadata", {}))
        result_metadata.update(
            {
                "feature_frame_count": features_result[
                    "frame_count"
                ],
                "has_frames": features_result[
                    "has_frames"
                ],
                "embedding_dimension": encoded[
                    "dimension"
                ],
            }
        )

        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=Modality.VIDEO,
            content=processed,
            features=features_result,
            entities=[],
            relations=[],
            embedding=encoded["embedding"],
            confidence=1.0,
            metadata=result_metadata,
        )


__all__ = ["VideoPerceptor"]
