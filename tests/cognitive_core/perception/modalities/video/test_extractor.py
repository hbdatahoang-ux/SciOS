"""Contract tests for the video extractor."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.video.extractor import (
    VideoExtractor,
)


@pytest.fixture
def extractor() -> VideoExtractor:
    return VideoExtractor()


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
        {
            "index": 2,
            "identifier": "frame-2",
        },
    ]


@pytest.fixture
def data(
    frames: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "frames": frames,
        "frame_count": 3,
    }


def test_validate_valid_input(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    extractor.validate_input(data)


@pytest.mark.parametrize(
    "value",
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
    extractor: VideoExtractor,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(value)


def test_missing_frames_rejected(
    extractor: VideoExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
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
    extractor: VideoExtractor,
    frames: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "frames": frames,
                "frame_count": 0,
            }
        )


def test_missing_frame_count_rejected(
    extractor: VideoExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
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
def test_invalid_frame_count_rejected(
    extractor: VideoExtractor,
    frame_count: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "frames": [],
                "frame_count": frame_count,
            }
        )


def test_negative_frame_count_rejected(
    extractor: VideoExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "frames": [],
                "frame_count": -1,
            }
        )


def test_frame_count_mismatch_rejected(
    extractor: VideoExtractor,
    frames: list[dict[str, object]],
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.validate_input(
            {
                "frames": frames,
                "frame_count": 2,
            }
        )


def test_empty_frames_are_valid(
    extractor: VideoExtractor,
) -> None:
    extractor.validate_input(
        {
            "frames": [],
            "frame_count": 0,
        }
    )


def test_extract_returns_dictionary(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert isinstance(result, dict)


def test_extract_frame_count(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert result["frame_count"] == 3


def test_extract_has_frames(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert result["has_frames"] is True


def test_extract_first_frame_index(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert result["first_frame_index"] == 0


def test_extract_last_frame_index(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert result["last_frame_index"] == 2


def test_extract_features(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    result = extractor.extract(data)

    assert result["features"] == {
        "frame_count": 3,
        "has_frames": True,
    }


def test_extract_empty_frames(
    extractor: VideoExtractor,
) -> None:
    result = extractor.extract(
        {
            "frames": [],
            "frame_count": 0,
        }
    )

    assert result == {
        "frame_count": 0,
        "first_frame_index": None,
        "last_frame_index": None,
        "has_frames": False,
        "features": {
            "frame_count": 0,
            "has_frames": False,
        },
    }


def test_extract_is_deterministic(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    first = extractor.extract(data)
    second = extractor.extract(data)

    assert first == second


def test_extract_does_not_mutate_input(
    extractor: VideoExtractor,
    data: dict[str, object],
) -> None:
    original = {
        "frames": list(data["frames"]),
        "frame_count": data["frame_count"],
    }

    extractor.extract(data)

    assert data == original


def test_extract_preserves_frame_indices(
    extractor: VideoExtractor,
) -> None:
    result = extractor.extract(
        {
            "frames": [
                {"index": 10, "identifier": "a"},
                {"index": 20, "identifier": "b"},
            ],
            "frame_count": 2,
        }
    )

    assert result["first_frame_index"] == 10
    assert result["last_frame_index"] == 20


def test_missing_frame_index_returns_none(
    extractor: VideoExtractor,
) -> None:
    result = extractor.extract(
        {
            "frames": [
                {"identifier": "a"},
                {"identifier": "b"},
            ],
            "frame_count": 2,
        }
    )

    assert result["first_frame_index"] is None
    assert result["last_frame_index"] is None


def test_invalid_input_propagates(
    extractor: VideoExtractor,
) -> None:
    with pytest.raises(PerceptionInputError):
        extractor.extract(
            {
                "frames": [],
                "frame_count": -1,
            }
        )
