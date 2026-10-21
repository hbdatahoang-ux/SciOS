"""Contract tests for the audio speech processor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.audio.speech import (
    SpeechProcessor,
)


@pytest.fixture
def processor() -> SpeechProcessor:
    return SpeechProcessor()


def test_speech_processor_imports() -> None:
    processor = SpeechProcessor()

    assert processor is not None


def test_validate_input_accepts_bytes(
    processor: SpeechProcessor,
) -> None:
    assert processor.validate_input(b"audio") is None


@pytest.mark.parametrize(
    "data",
    [
        b"",
        None,
        "audio",
        bytearray(b"audio"),
        123,
    ],
)
def test_validate_input_rejects_invalid_data(
    processor: SpeechProcessor,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        processor.validate_input(data)


def test_transcribe_returns_text(
    processor: SpeechProcessor,
) -> None:
    result = processor.transcribe(b"audio")

    assert result["text"] == ""


def test_transcribe_returns_segments(
    processor: SpeechProcessor,
) -> None:
    result = processor.transcribe(b"audio")

    assert result["segments"] == []


def test_transcribe_returns_metadata(
    processor: SpeechProcessor,
) -> None:
    result = processor.transcribe(b"audio")

    assert result["metadata"] == {
        "backend": "deterministic",
    }


def test_transcribe_has_expected_structure(
    processor: SpeechProcessor,
) -> None:
    result = processor.transcribe(b"audio")

    assert set(result) == {
        "text",
        "segments",
        "metadata",
    }


def test_transcribe_rejects_empty_audio(
    processor: SpeechProcessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        processor.transcribe(b"")
