"""Image perceptor for the SciOS Cognitive Core."""

from __future__ import annotations

from pathlib import Path

from ...core.base import BasePerceptor
from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus, RawInput
from .detector import ImageDetector
from .encoder import ImageEncoder
from .loader import ImageLoader
from .preprocess import ImagePreprocessor


class ImagePerceptor(BasePerceptor):
    """Orchestrate the image perception pipeline."""

    def __init__(
        self,
        *,
        name: str = "image",
        loader: ImageLoader | None = None,
        preprocessor: ImagePreprocessor | None = None,
        detector: ImageDetector | None = None,
        encoder: ImageEncoder | None = None,
    ) -> None:
        """Initialize the image perception pipeline."""

        super().__init__(
            name=name,
            modality=Modality.IMAGE,
        )

        if loader is not None and not isinstance(loader, ImageLoader):
            raise TypeError("loader must be an ImageLoader")

        if preprocessor is not None and not isinstance(
            preprocessor,
            ImagePreprocessor,
        ):
            raise TypeError(
                "preprocessor must be an ImagePreprocessor"
            )

        if detector is not None and not isinstance(
            detector,
            ImageDetector,
        ):
            raise TypeError("detector must be an ImageDetector")

        if encoder is not None and not isinstance(
            encoder,
            ImageEncoder,
        ):
            raise TypeError("encoder must be an ImageEncoder")

        self.loader = loader or ImageLoader()
        self.preprocessor = preprocessor or ImagePreprocessor()
        self.detector = detector or ImageDetector()
        self.encoder = encoder or ImageEncoder()

    def perceive(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Transform an image source into a standardized result."""

        input_metadata = dict(metadata or {})

        try:
            loaded = self.loader.load(raw_input)

            processed = self.preprocessor.preprocess(
                loaded["content"]
            )

            detection = self.detector.detect(
                processed["content"]
            )

            encoded = self.encoder.encode(
                processed["content"]
            )

            result_metadata = {
                **input_metadata,
                **loaded.get("metadata", {}),
                **processed.get("metadata", {}),
                "detection_backend": detection["metadata"]["backend"],
                "encoding_backend": encoded["metadata"]["backend"],
            }

            return PerceptionResult(
                status=PerceptionStatus.SUCCESS,
                modality=Modality.IMAGE,
                content=processed["content"],
                features={
                    "format": processed["metadata"]["format"],
                    "original_size": processed["metadata"][
                        "original_size"
                    ],
                    "detection_count": detection["count"],
                    "detection_backend": detection["metadata"][
                        "backend"
                    ],
                },
                entities=detection["detections"],
                relations=[],
                embedding=encoded["embedding"],
                confidence=1.0,
                metadata=result_metadata,
            )

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "image perception processing failed"
            ) from exc


__all__ = ["ImagePerceptor"]
