"""Contract tests for the video encoder."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.video.encoder import (
    VideoEncoder,
)


@pytest.fixture
def encoder() -> VideoEncoder:
    return VideoEncoder()


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


@pytest.fixture
def data(
    frames: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "frames": frames,
        "frame_count": 2,
    }


def test_encoder_dimension(
    encoder: VideoEncoder,
) -> None:
    assert encoder.DIMENSION == 32


def test_validate_valid_input(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    encoder.validate_input(data)


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
    encoder: VideoEncoder,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(value)


def test_missing_frames_rejected(
    encoder: VideoEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
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
    encoder: VideoEncoder,
    frames: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
            {
                "frames": frames,
                "frame_count": 0,
            }
        )


def test_missing_frame_count_rejected(
    encoder: VideoEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
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
    encoder: VideoEncoder,
    frame_count: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
            {
                "frames": [],
                "frame_count": frame_count,
            }
        )


def test_negative_frame_count_rejected(
    encoder: VideoEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
            {
                "frames": [],
                "frame_count": -1,
            }
        )


def test_frame_count_mismatch_rejected(
    encoder: VideoEncoder,
    frames: list[dict[str, object]],
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(
            {
                "frames": frames,
                "frame_count": 1,
            }
        )


def test_empty_frames_are_valid(
    encoder: VideoEncoder,
) -> None:
    encoder.validate_input(
        {
            "frames": [],
            "frame_count": 0,
        }
    )


def test_encode_returns_dictionary(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert isinstance(result, dict)


def test_embedding_is_list(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert isinstance(result["embedding"], list)


def test_embedding_dimension(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert result["dimension"] == 32
    assert len(result["embedding"]) == 32


def test_embedding_values_are_floats(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert all(
        isinstance(value, float)
        for value in result["embedding"]
    )


def test_embedding_values_are_normalized(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert all(
        0.0 <= value <= 1.0
        for value in result["embedding"]
    )


def test_embedding_is_deterministic(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    first = encoder.encode(data)
    second = encoder.encode(data)

    assert first == second


def test_different_frames_produce_different_embeddings(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    first = encoder.encode(data)

    changed = {
        "frames": [
            {
                "index": 0,
                "identifier": "different-frame",
            },
            {
                "index": 1,
                "identifier": "frame-1",
            },
        ],
        "frame_count": 2,
    }

    second = encoder.encode(changed)

    assert first["embedding"] != second["embedding"]


def test_frame_order_affects_embedding(
    encoder: VideoEncoder,
) -> None:
    first = encoder.encode(
        {
            "frames": [
                {"index": 0, "identifier": "a"},
                {"index": 1, "identifier": "b"},
            ],
            "frame_count": 2,
        }
    )

    second = encoder.encode(
        {
            "frames": [
                {"index": 1, "identifier": "b"},
                {"index": 0, "identifier": "a"},
            ],
            "frame_count": 2,
        }
    )

    assert first["embedding"] != second["embedding"]


def test_metadata_contract(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    result = encoder.encode(data)

    assert result["metadata"] == {
        "backend": "deterministic",
        "algorithm": "sha256",
    }


def test_empty_frames_produce_valid_embedding(
    encoder: VideoEncoder,
) -> None:
    result = encoder.encode(
        {
            "frames": [],
            "frame_count": 0,
        }
    )

    assert result["dimension"] == 32
    assert len(result["embedding"]) == 32
    assert all(
        isinstance(value, float)
        for value in result["embedding"]
    )


def test_input_is_not_mutated(
    encoder: VideoEncoder,
    data: dict[str, object],
) -> None:
    original = {
        "frames": list(data["frames"]),
        "frame_count": data["frame_count"],
    }

    encoder.encode(data)

    assert data == original


def test_invalid_input_propagates(
    encoder: VideoEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.encode(
            {
                "frames": [],
                "frame_count": -1,
            }
        )
