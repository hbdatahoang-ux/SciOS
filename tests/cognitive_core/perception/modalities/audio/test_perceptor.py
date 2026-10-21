"""Contract tests for the audio perceptor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import Modality
from scios.cognitive_core.perception.modalities.audio.encoder import (
    AudioEncoder,
)
from scios.cognitive_core.perception.modalities.audio.extractor import (
    AudioExtractor,
)
from scios.cognitive_core.perception.modalities.audio.loader import (
    AudioLoader,
)
from scios.cognitive_core.perception.modalities.audio.perceptor import (
    AudioPerceptor,
)
from scios.cognitive_core.perception.modalities.audio.preprocess import (
    AudioPreprocessor,
)
from scios.cognitive_core.perception.modalities.audio.speech import (
    SpeechProcessor,
)


@pytest.fixture
def perceptor() -> AudioPerceptor:
    return AudioPerceptor()


def test_perceptor_imports() -> None:
    assert AudioPerceptor is not None


def test_default_identity(
    perceptor: AudioPerceptor,
) -> None:
    assert perceptor.name == "audio"
    assert perceptor.modality is Modality.AUDIO


def test_default_components(
    perceptor: AudioPerceptor,
) -> None:
    assert isinstance(perceptor.loader, AudioLoader)
    assert isinstance(perceptor.preprocessor, AudioPreprocessor)
    assert isinstance(perceptor.speech_processor, SpeechProcessor)
    assert isinstance(perceptor.extractor, AudioExtractor)
    assert isinstance(perceptor.encoder, AudioEncoder)


def test_custom_components_are_preserved() -> None:
    loader = AudioLoader()
    preprocessor = AudioPreprocessor()
    speech_processor = SpeechProcessor()
    extractor = AudioExtractor()
    encoder = AudioEncoder()

    perceptor = AudioPerceptor(
        loader=loader,
        preprocessor=preprocessor,
        speech_processor=speech_processor,
        extractor=extractor,
        encoder=encoder,
    )

    assert perceptor.loader is loader
    assert perceptor.preprocessor is preprocessor
    assert perceptor.speech_processor is speech_processor
    assert perceptor.extractor is extractor
    assert perceptor.encoder is encoder


@pytest.mark.parametrize(
    "kwargs",
    [
        {"loader": object()},
        {"preprocessor": object()},
        {"speech_processor": object()},
        {"extractor": object()},
        {"encoder": object()},
    ],
)
def test_rejects_invalid_components(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(TypeError):
        AudioPerceptor(**kwargs)


def test_perceive_rejects_empty_input(
    perceptor: AudioPerceptor,
) -> None:
    with pytest.raises(PerceptionInputError):
        perceptor.perceive(b"")


def test_perceive_returns_result(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert isinstance(result, PerceptionResult)


def test_perceive_returns_audio_modality(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.modality is Modality.AUDIO


def test_perceive_returns_success(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.successful


def test_perceive_returns_transcribed_content(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.content == ""


def test_perceive_returns_features(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.features == {
        "text_length": 0,
        "segment_count": 0,
        "word_count": 0,
    }


def test_perceive_returns_empty_entities_and_relations(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.entities == []
    assert result.relations == []


def test_perceive_returns_embedding(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.embedding is not None
    assert len(result.embedding) == 32


def test_perceive_preserves_metadata(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE",
        metadata={"source": "test"},
    )

    assert result.metadata["source"] == "test"


def test_perceive_contains_backend_metadata(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.metadata["backend"] == "deterministic"


def test_perceive_contains_format_metadata(
    perceptor: AudioPerceptor,
) -> None:
    result = perceptor.perceive(
        b"RIFF\x00\x00\x00\x00WAVE"
    )

    assert result.metadata["format"] == "wav"
