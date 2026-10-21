"""Audio perceptor for the SciOS Cognitive Core."""

from __future__ import annotations

from ...core.base import BasePerceptor
from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus, RawInput
from .encoder import AudioEncoder
from .extractor import AudioExtractor
from .loader import AudioLoader
from .preprocess import AudioPreprocessor
from .speech import SpeechProcessor


class AudioPerceptor(BasePerceptor):
    """Orchestrate the complete audio perception pipeline."""

    def __init__(
        self,
        *,
        name: str = "audio",
        loader: AudioLoader | None = None,
        preprocessor: AudioPreprocessor | None = None,
        speech_processor: SpeechProcessor | None = None,
        extractor: AudioExtractor | None = None,
        encoder: AudioEncoder | None = None,
    ) -> None:
        """Initialize the audio perception pipeline."""

        super().__init__(
            name=name,
            modality=Modality.AUDIO,
        )

        if loader is not None and not isinstance(loader, AudioLoader):
            raise TypeError("loader must be an AudioLoader")

        if preprocessor is not None and not isinstance(
            preprocessor,
            AudioPreprocessor,
        ):
            raise TypeError(
                "preprocessor must be an AudioPreprocessor"
            )

        if speech_processor is not None and not isinstance(
            speech_processor,
            SpeechProcessor,
        ):
            raise TypeError(
                "speech_processor must be a SpeechProcessor"
            )

        if extractor is not None and not isinstance(
            extractor,
            AudioExtractor,
        ):
            raise TypeError(
                "extractor must be an AudioExtractor"
            )

        if encoder is not None and not isinstance(
            encoder,
            AudioEncoder,
        ):
            raise TypeError(
                "encoder must be an AudioEncoder"
            )

        self.loader = loader or AudioLoader()
        self.preprocessor = preprocessor or AudioPreprocessor()
        self.speech_processor = speech_processor or SpeechProcessor()
        self.extractor = extractor or AudioExtractor()
        self.encoder = encoder or AudioEncoder()

    def perceive(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Transform raw audio into a standardized perception result."""

        input_metadata = dict(metadata or {})

        try:
            loaded = self.loader.load(raw_input)

            preprocessed = self.preprocessor.preprocess(
                loaded["content"]
            )

            speech = self.speech_processor.transcribe(
                preprocessed["content"]
            )

            extracted = self.extractor.extract(speech)

            encoded = self.encoder.encode(
                preprocessed["content"]
            )

            result_metadata = {
                **input_metadata,
                **loaded.get("metadata", {}),
                **preprocessed.get("metadata", {}),
                **speech.get("metadata", {}),
                **encoded.get("metadata", {}),
            }

            return PerceptionResult(
                status=PerceptionStatus.SUCCESS,
                modality=Modality.AUDIO,
                content=speech.get("text", ""),
                features=extracted["features"],
                entities=extracted["entities"],
                relations=extracted["relations"],
                embedding=encoded["embedding"],
                confidence=1.0,
                metadata=result_metadata,
            )

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "audio perception processing failed"
            ) from exc


__all__ = ["AudioPerceptor"]
