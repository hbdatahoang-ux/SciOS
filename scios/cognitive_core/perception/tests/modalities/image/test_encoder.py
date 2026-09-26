"""Contract tests for image encoding."""

import pytest

from scios.cognitive_core.perception.core import PerceptionInputError
from scios.cognitive_core.perception.modalities.image.encoder import (
    ImageEncoder,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"
JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-data"
WEBP_BYTES = b"RIFFxxxxWEBPfake-webp-data"
BMP_BYTES = b"BMfake-bmp-data"
GIF_BYTES = b"GIF89afake-gif-data"


@pytest.fixture
def encoder() -> ImageEncoder:
    return ImageEncoder()


def test_constructor() -> None:
    encoder = ImageEncoder()

    assert isinstance(encoder, ImageEncoder)


@pytest.mark.parametrize(
    "data",
    [
        PNG_BYTES,
        JPEG_BYTES,
        WEBP_BYTES,
        BMP_BYTES,
        GIF_BYTES,
    ],
)
def test_validate_input_accepts_supported_image_bytes(
    encoder: ImageEncoder,
    data: bytes,
) -> None:
    encoder.validate_input(data)


def test_validate_input_rejects_empty_bytes(
    encoder: ImageEncoder,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(b"")


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "image.png",
        123,
        1.5,
        [],
        {},
        bytearray(b"image"),
    ],
)
def test_validate_input_rejects_non_bytes(
    encoder: ImageEncoder,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(value)


@pytest.mark.parametrize(
    "data",
    [
        b"invalid-image",
        b"not-an-image",
        b"\x00\x01\x02",
    ],
)
def test_validate_input_rejects_invalid_image_bytes(
    encoder: ImageEncoder,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.validate_input(data)


def test_encode_returns_expected_structure(
    encoder: ImageEncoder,
) -> None:
    result = encoder.encode(PNG_BYTES)

    assert set(result) == {
        "embedding",
        "metadata",
    }

    assert set(result["metadata"]) == {
        "format",
        "backend",
        "dimension",
    }


def test_encode_returns_tuple_embedding(
    encoder: ImageEncoder,
) -> None:
    result = encoder.encode(PNG_BYTES)

    assert isinstance(result["embedding"], tuple)


def test_encode_returns_fixed_dimension_embedding(
    encoder: ImageEncoder,
) -> None:
    result = encoder.encode(PNG_BYTES)

    assert len(result["embedding"]) == 32
    assert result["metadata"]["dimension"] == 32


@pytest.mark.parametrize(
    "data",
    [
        PNG_BYTES,
        JPEG_BYTES,
        WEBP_BYTES,
        BMP_BYTES,
        GIF_BYTES,
    ],
)
def test_encode_values_are_floats(
    encoder: ImageEncoder,
    data: bytes,
) -> None:
    result = encoder.encode(data)

    assert all(
        isinstance(value, float)
        for value in result["embedding"]
    )


@pytest.mark.parametrize(
    "data",
    [
        PNG_BYTES,
        JPEG_BYTES,
        WEBP_BYTES,
        BMP_BYTES,
        GIF_BYTES,
    ],
)
def test_encode_values_are_normalized(
    encoder: ImageEncoder,
    data: bytes,
) -> None:
    result = encoder.encode(data)

    assert all(
        0.0 <= value <= 1.0
        for value in result["embedding"]
    )


def test_encode_is_deterministic(
    encoder: ImageEncoder,
) -> None:
    first = encoder.encode(PNG_BYTES)
    second = encoder.encode(PNG_BYTES)

    assert first == second


def test_different_inputs_produce_different_embeddings(
    encoder: ImageEncoder,
) -> None:
    first = encoder.encode(PNG_BYTES)
    second = encoder.encode(
        b"\x89PNG\r\n\x1a\nanother-image"
    )

    assert first["embedding"] != second["embedding"]


@pytest.mark.parametrize(
    ("data", "expected_format"),
    [
        (PNG_BYTES, "png"),
        (JPEG_BYTES, "jpeg"),
        (WEBP_BYTES, "webp"),
        (BMP_BYTES, "bmp"),
        (GIF_BYTES, "gif"),
    ],
)
def test_encode_reports_format(
    encoder: ImageEncoder,
    data: bytes,
    expected_format: str,
) -> None:
    result = encoder.encode(data)

    assert result["metadata"]["format"] == expected_format


def test_encode_reports_deterministic_backend(
    encoder: ImageEncoder,
) -> None:
    result = encoder.encode(PNG_BYTES)

    assert result["metadata"]["backend"] == "deterministic"


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"invalid-image",
        b"not-an-image",
    ],
)
def test_encode_rejects_invalid_input(
    encoder: ImageEncoder,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        encoder.encode(data)


def test_private_embedding_dimension() -> None:
    embedding = ImageEncoder._create_embedding(PNG_BYTES)

    assert len(embedding) == 32


def test_private_embedding_is_deterministic() -> None:
    first = ImageEncoder._create_embedding(PNG_BYTES)
    second = ImageEncoder._create_embedding(PNG_BYTES)

    assert first == second


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (PNG_BYTES, "png"),
        (JPEG_BYTES, "jpeg"),
        (WEBP_BYTES, "webp"),
        (BMP_BYTES, "bmp"),
        (GIF_BYTES, "gif"),
    ],
)
def test_private_format_detection(
    data: bytes,
    expected: str,
) -> None:
    assert ImageEncoder._detect_format(data) == expected
