"""Contract tests for the video loader."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.video.loader import (
    VideoLoader,
)


@pytest.fixture
def loader() -> VideoLoader:
    return VideoLoader()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00",
            "mp4",
        ),
        (
            b"\x00\x00\x00\x18ftypqt  \x00\x00\x02\x00",
            "mov",
        ),
        (
            b"RIFF\x00\x00\x00\x00AVI ",
            "avi",
        ),
        (
            b"\x1A\x45\xDF\xA3\x00\x00\x00\x00webm",
            "webm",
        ),
        (
            b"\x1A\x45\xDF\xA3\x00\x00\x00\x00matroska",
            "mkv",
        ),
    ],
)
def test_load_bytes(
    loader: VideoLoader,
    data: bytes,
    expected: str,
) -> None:
    result = loader.load(data)

    assert result["content"] == data
    assert result["metadata"]["source_name"] is None
    assert result["metadata"]["format"] == expected


def test_validate_bytes_accepts_non_empty_data(
    loader: VideoLoader,
) -> None:
    loader.validate_source(b"video")


def test_validate_empty_bytes_rejected(
    loader: VideoLoader,
) -> None:
    with pytest.raises(PerceptionInputError):
        loader.validate_source(b"")


@pytest.mark.parametrize(
    "source",
    [
        123,
        None,
        object(),
        [],
    ],
)
def test_validate_invalid_source_type(
    loader: VideoLoader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        loader.validate_source(source)


def test_empty_string_rejected(
    loader: VideoLoader,
) -> None:
    with pytest.raises(PerceptionInputError):
        loader.validate_source("")


def test_missing_path_rejected(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing.mp4"

    with pytest.raises(PerceptionInputError):
        loader.validate_source(source)


def test_directory_rejected(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "video.mp4"
    source.mkdir()

    with pytest.raises(PerceptionInputError):
        loader.validate_source(source)


def test_unsupported_extension_rejected(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "video.txt"
    source.write_bytes(b"video")

    with pytest.raises(PerceptionInputError):
        loader.validate_source(source)


def test_path_load(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.mp4"
    data = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00"
    source.write_bytes(data)

    result = loader.load(source)

    assert result["content"] == data
    assert result["metadata"] == {
        "source_name": "sample.mp4",
        "format": "mp4",
    }


def test_string_path_load(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.avi"
    data = b"RIFF\x00\x00\x00\x00AVI "
    source.write_bytes(data)

    result = loader.load(str(source))

    assert result["content"] == data
    assert result["metadata"]["source_name"] == "sample.avi"
    assert result["metadata"]["format"] == "avi"


def test_extension_content_mismatch_rejected(
    loader: VideoLoader,
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.mp4"
    source.write_bytes(b"RIFF\x00\x00\x00\x00AVI ")

    with pytest.raises(PerceptionInputError):
        loader.load(source)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"not-video",
        b"RIFF\x00\x00\x00\x00WAVE",
        b"\x1A\x45\xDF\xA3\x00\x00\x00\x00unknown",
    ],
)
def test_invalid_video_bytes_rejected(
    loader: VideoLoader,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        loader.load(data)


def test_read_os_error_wrapped(
    loader: VideoLoader,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "sample.mp4"
    source.write_bytes(
        b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00"
    )

    def fail_read_bytes(self: Path) -> bytes:
        raise OSError("read failure")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    with pytest.raises(PerceptionProcessingError):
        loader.load(source)
