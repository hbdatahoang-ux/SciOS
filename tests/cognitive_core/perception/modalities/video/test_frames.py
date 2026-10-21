"""Contract tests for the video frame extractor."""

import hashlib

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.video.frames import (
    VideoFrameExtractor,
)


@pytest.fixture
def extractor() -> VideoFrameExtractor:
    return VideoFrameExtractor()


def test_validate_bytes(
    extractor: VideoFrameExtractor,
) -> None:
    extractor.validate_input(b"video")


def test_empty_bytes_rejected(
    extractor: VideoFrameExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(b"")


@pytest.mark.parametrize(
    "data",
    [
        "video",
        bytearray(b"video"),
        memoryview(b"video"),
        123,
        None,
        object(),
        [],
    ],
)
def test_invalid_input_rejected(
    extractor: VideoFrameExtractor,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(data)


def test_extract_returns_frame_representation(
    extractor: VideoFrameExtractor,
) -> None:
    data = b"video"

    result = extractor.extract(data)

    assert isinstance(result, dict)
    assert result["frame_count"] == 1
    assert isinstance(result["frames"], list)
    assert len(result["frames"]) == 1
    assert result["metadata"] == {
        "backend": "deterministic",
    }


def test_extract_frame_descriptor(
    extractor: VideoFrameExtractor,
) -> None:
    data = b"video"

    result = extractor.extract(data)

    frame = result["frames"][0]

    assert frame["index"] == 0
    assert frame["identifier"] == hashlib.sha256(data).hexdigest()


def test_extract_is_deterministic(
    extractor: VideoFrameExtractor,
) -> None:
    data = b"same-video-content"

    first = extractor.extract(data)
    second = extractor.extract(data)

    assert first == second


def test_different_input_produces_different_identifier(
    extractor: VideoFrameExtractor,
) -> None:
    first = extractor.extract(b"video-one")
    second = extractor.extract(b"video-two")

    assert (
        first["frames"][0]["identifier"]
        != second["frames"][0]["identifier"]
    )


def test_input_bytes_are_not_modified(
    extractor: VideoFrameExtractor,
) -> None:
    data = b"video-content"
    original = bytes(data)

    extractor.extract(data)

    assert data == original


def test_extract_invalid_input_propagates(
    extractor: VideoFrameExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.extract(b"")


def test_processing_error_is_wrapped(
    extractor: VideoFrameExtractor,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_sha256(data: bytes) -> object:
        raise RuntimeError("hash failure")

    monkeypatch.setattr(
        hashlib,
        "sha256",
        fail_sha256,
    )

    with pytest.raises(PerceptionProcessingError):
        extractor.extract(b"video")
