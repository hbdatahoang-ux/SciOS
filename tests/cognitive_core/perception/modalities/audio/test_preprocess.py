"""Contract tests for the audio preprocessor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.audio.preprocess import (
    AudioPreprocessor,
)


@pytest.fixture
def preprocessor() -> AudioPreprocessor:
    return AudioPreprocessor()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"RIFF" + b"\x00" * 4 + b"WAVE", "wav"),
        (b"ID3" + b"\x00" * 8, "mp3"),
        (b"fLaC" + b"\x00" * 8, "flac"),
        (b"OggS" + b"\x00" * 8, "ogg"),
        (b"\x00\x00\x00\x18ftypM4A " + b"\x00" * 8, "m4a"),
        (b"ADIF" + b"\x00" * 8, "aac"),
        (b"\xff\xf1" + b"\x00" * 8, "aac"),
    ],
)
def test_detect_format(
    preprocessor: AudioPreprocessor,
    data: bytes,
    expected: str,
) -> None:
    assert preprocessor._detect_format(data) == expected


def test_validate_input_accepts_supported_audio(
    preprocessor: AudioPreprocessor,
) -> None:
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"

    assert preprocessor.validate_input(data) is None


def test_preprocess_preserves_content(
    preprocessor: AudioPreprocessor,
) -> None:
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"

    result = preprocessor.preprocess(data)

    assert result["content"] == data


def test_preprocess_returns_format(
    preprocessor: AudioPreprocessor,
) -> None:
    data = b"fLaC" + b"\x00" * 8

    result = preprocessor.preprocess(data)

    assert result["metadata"]["format"] == "flac"


def test_preprocess_returns_original_size(
    preprocessor: AudioPreprocessor,
) -> None:
    data = b"OggS" + b"\x00" * 10

    result = preprocessor.preprocess(data)

    assert result["metadata"]["original_size"] == len(data)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"not audio",
        b"\x00\x01\x02",
    ],
)
def test_invalid_audio_bytes(
    preprocessor: AudioPreprocessor,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(data)


@pytest.mark.parametrize(
    "data",
    [
        None,
        "audio",
        bytearray(b"audio"),
        123,
    ],
)
def test_invalid_input_type(
    preprocessor: AudioPreprocessor,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(data)


def test_preprocess_rejects_invalid_input(
    preprocessor: AudioPreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.preprocess(b"invalid audio")
