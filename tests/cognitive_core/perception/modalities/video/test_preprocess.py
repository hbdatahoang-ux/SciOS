"""Contract tests for the video preprocessor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.video.preprocess import (
    VideoPreprocessor,
)


@pytest.fixture
def preprocessor() -> VideoPreprocessor:
    return VideoPreprocessor()


@pytest.fixture
def frames() -> list[dict[str, object]]:
    return [
        {
            "index": 0,
            "identifier": "frame-0",
        },
        {
            "index": 1,
            "identifier": "frame-1",
        },
    ]


def test_validate_valid_input(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    preprocessor.validate_input(
        {
            "frames": frames,
            "frame_count": 2,
        }
    )


@pytest.mark.parametrize(
    "data",
    [
        None,
        "frames",
        b"frames",
        [],
        123,
        object(),
    ],
)
def test_invalid_input_type_rejected(
    preprocessor: VideoPreprocessor,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(data)


def test_missing_frames_rejected(
    preprocessor: VideoPreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frame_count": 0,
            }
        )


@pytest.mark.parametrize(
    "frames",
    [
        None,
        {},
        "frames",
        b"frames",
        123,
    ],
)
def test_invalid_frames_rejected(
    preprocessor: VideoPreprocessor,
    frames: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frames": frames,
                "frame_count": 0,
            }
        )


def test_missing_frame_count_rejected(
    preprocessor: VideoPreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frames": [],
            }
        )


@pytest.mark.parametrize(
    "frame_count",
    [
        None,
        1.0,
        "1",
        [],
        {},
    ],
)
def test_invalid_frame_count_type_rejected(
    preprocessor: VideoPreprocessor,
    frame_count: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frames": [],
                "frame_count": frame_count,
            }
        )


def test_negative_frame_count_rejected(
    preprocessor: VideoPreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frames": [],
                "frame_count": -1,
            }
        )


def test_frame_count_mismatch_rejected(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(
            {
                "frames": frames,
                "frame_count": 1,
            }
        )


def test_empty_frames_are_valid(
    preprocessor: VideoPreprocessor,
) -> None:
    preprocessor.validate_input(
        {
            "frames": [],
            "frame_count": 0,
        }
    )


def test_preprocess_preserves_frames(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    result = preprocessor.preprocess(
        {
            "frames": frames,
            "frame_count": 2,
        }
    )

    assert result["frames"] == frames
    assert result["frame_count"] == 2


def test_preprocess_returns_expected_metadata(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    result = preprocessor.preprocess(
        {
            "frames": frames,
            "frame_count": 2,
        }
    )

    assert result["metadata"] == {
        "backend": "deterministic",
        "frame_count": 2,
    }


def test_preprocess_empty_frames(
    preprocessor: VideoPreprocessor,
) -> None:
    result = preprocessor.preprocess(
        {
            "frames": [],
            "frame_count": 0,
        }
    )

    assert result == {
        "frames": [],
        "frame_count": 0,
        "metadata": {
            "backend": "deterministic",
            "frame_count": 0,
        },
    }


def test_preprocess_is_deterministic(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    data = {
        "frames": frames,
        "frame_count": 2,
    }

    first = preprocessor.preprocess(data)
    second = preprocessor.preprocess(data)

    assert first == second


def test_preprocess_does_not_mutate_input(
    preprocessor: VideoPreprocessor,
    frames: list[dict[str, object]],
) -> None:
    data = {
        "frames": frames,
        "frame_count": 2,
    }

    original_frames = list(frames)

    preprocessor.preprocess(data)

    assert data["frames"] == original_frames
    assert data["frame_count"] == 2


def test_preprocess_invalid_input_propagates(
    preprocessor: VideoPreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.preprocess(
            {
                "frames": [],
                "frame_count": -1,
            }
        )