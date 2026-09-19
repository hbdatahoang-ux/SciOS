"""Contract tests for the audio loader."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.audio.loader import (
    AudioLoader,
)


@pytest.fixture
def loader() -> AudioLoader:
    return AudioLoader()


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
def test_detect_format_from_bytes(
    loader: AudioLoader,
    data: bytes,
    expected: str,
) -> None:
    assert loader._detect_format_from_bytes(data) == expected


def test_load_bytes(loader: AudioLoader) -> None:
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"

    result = loader.load(data)

    assert result["content"] == data
    assert result["metadata"]["source_name"] is None
    assert result["metadata"]["format"] == "wav"


def test_load_path(loader: AudioLoader, tmp_path: Path) -> None:
    path = tmp_path / "sample.wav"
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"
    path.write_bytes(data)

    result = loader.load(path)

    assert result["content"] == data
    assert result["metadata"]["source_name"] == "sample.wav"
    assert result["metadata"]["format"] == "wav"


def test_load_string_path(loader: AudioLoader, tmp_path: Path) -> None:
    path = tmp_path / "sample.wav"
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"
    path.write_bytes(data)

    result = loader.load(str(path))

    assert result["content"] == data
    assert result["metadata"]["source_name"] == "sample.wav"
    assert result["metadata"]["format"] == "wav"


@pytest.mark.parametrize(
    "source",
    [
        b"",
        "",
        123,
        None,
    ],
)
def test_invalid_source(
    loader: AudioLoader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        loader.validate_source(source)


def test_missing_path(loader: AudioLoader, tmp_path: Path) -> None:
    with pytest.raises(PerceptionInputError):
        loader.load(tmp_path / "missing.wav")


def test_unsupported_extension(
    loader: AudioLoader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.txt"
    path.write_bytes(b"data")

    with pytest.raises(PerceptionInputError):
        loader.load(path)


def test_invalid_audio_bytes(loader: AudioLoader) -> None:
    with pytest.raises(PerceptionInputError):
        loader.load(b"not audio")


def test_extension_content_mismatch(
    loader: AudioLoader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.mp3"
    path.write_bytes(
        b"RIFF" + b"\x00" * 4 + b"WAVE"
    )

    with pytest.raises(PerceptionInputError):
        loader.load(path)


def test_supported_extensions_are_case_insensitive(
    loader: AudioLoader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.WAV"
    data = b"RIFF" + b"\x00" * 4 + b"WAVE"
    path.write_bytes(data)

    result = loader.load(path)

    assert result["metadata"]["format"] == "wav"
