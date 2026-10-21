"""Contract tests for the audio encoder."""

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.audio.encoder import (
    AudioEncoder,
)


@pytest.fixture
def encoder() -> AudioEncoder:
    return AudioEncoder()


def test_encoder_imports() -> None:
    encoder = AudioEncoder()

    assert encoder is not None


def test_validate_input_accepts_bytes(
    encoder: AudioEncoder,
) -> None:
    assert encoder.validate_input(b"audio") is None


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
    encoder: AudioEncoder,
    data: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(data)


def test_encode_returns_embedding(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert "embedding" in result
    assert isinstance(result["embedding"], list)


def test_embedding_has_fixed_dimension(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert len(result["embedding"]) == 32


def test_embedding_contains_floats(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert all(
        isinstance(value, float)
        for value in result["embedding"]
    )


def test_embedding_values_are_normalized(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert all(
        0.0 <= value <= 1.0
        for value in result["embedding"]
    )


def test_embedding_is_deterministic(
    encoder: AudioEncoder,
) -> None:
    first = encoder.encode(b"audio")
    second = encoder.encode(b"audio")

    assert first["embedding"] == second["embedding"]


def test_different_inputs_produce_different_embeddings(
    encoder: AudioEncoder,
) -> None:
    first = encoder.encode(b"audio-one")
    second = encoder.encode(b"audio-two")

    assert first["embedding"] != second["embedding"]


def test_encode_returns_backend_metadata(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert result["metadata"]["backend"] == "deterministic"


def test_encode_returns_dimension_metadata(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert result["metadata"]["dimension"] == 32


def test_encode_has_expected_structure(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert set(result) == {
        "embedding",
        "metadata",
    }


def test_encode_rejects_empty_audio(
    encoder: AudioEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.encode(b"")


def test_same_instance_repeated_encoding_is_stable(
    encoder: AudioEncoder,
) -> None:
    values = [
        encoder.encode(b"audio")["embedding"]
        for _ in range(3)
    ]

    assert values[0] == values[1] == values[2]


def test_embedding_is_not_empty(
    encoder: AudioEncoder,
) -> None:
    result = encoder.encode(b"audio")

    assert result["embedding"]


def test_metadata_is_deterministic(
    encoder: AudioEncoder,
) -> None:
    first = encoder.encode(b"audio")
    second = encoder.encode(b"audio")

    assert first["metadata"] == second["metadata"]
