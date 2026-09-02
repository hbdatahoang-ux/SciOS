"""Contract tests for image preprocessing."""

import pytest

from scios.cognitive_core.perception.core import PerceptionInputError
from scios.cognitive_core.perception.modalities.image.preprocess import (
    ImagePreprocessor,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"
JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-data"
WEBP_BYTES = b"RIFFxxxxWEBPfake-webp-data"
BMP_BYTES = b"BMfake-bmp-data"
GIF_BYTES = b"GIF89afake-gif-data"


@pytest.fixture
def preprocessor() -> ImagePreprocessor:
    return ImagePreprocessor()


def test_constructor() -> None:
    processor = ImagePreprocessor()

    assert isinstance(processor, ImagePreprocessor)


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
    preprocessor: ImagePreprocessor,
    data: bytes,
) -> None:
    preprocessor.validate_input(data)


def test_validate_input_rejects_empty_bytes(
    preprocessor: ImagePreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(b"")


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
    preprocessor: ImagePreprocessor,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(value)


@pytest.mark.parametrize(
    "data",
    [
        b"invalid-image",
        b"not-an-image",
        b"\x00\x01\x02",
    ],
)
def test_validate_input_rejects_invalid_image_bytes(
    preprocessor: ImagePreprocessor,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.validate_input(data)


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
def test_preprocess_detects_format(
    preprocessor: ImagePreprocessor,
    data: bytes,
    expected_format: str,
) -> None:
    result = preprocessor.preprocess(data)

    assert result["metadata"]["format"] == expected_format


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
def test_preprocess_preserves_original_bytes(
    preprocessor: ImagePreprocessor,
    data: bytes,
) -> None:
    result = preprocessor.preprocess(data)

    assert result["content"] is data
    assert result["content"] == data


def test_preprocess_reports_original_size(
    preprocessor: ImagePreprocessor,
) -> None:
    result = preprocessor.preprocess(PNG_BYTES)

    assert result["metadata"]["original_size"] == len(PNG_BYTES)


def test_preprocess_returns_expected_structure(
    preprocessor: ImagePreprocessor,
) -> None:
    result = preprocessor.preprocess(PNG_BYTES)

    assert set(result) == {"content", "metadata"}
    assert set(result["metadata"]) == {
        "format",
        "original_size",
    }


def test_preprocess_rejects_invalid_bytes(
    preprocessor: ImagePreprocessor,
) -> None:
    with pytest.raises(PerceptionInputError):
        preprocessor.preprocess(b"invalid")


def test_private_format_detection() -> None:
    assert ImagePreprocessor._detect_format(PNG_BYTES) == "png"
    assert ImagePreprocessor._detect_format(JPEG_BYTES) == "jpeg"
    assert ImagePreprocessor._detect_format(WEBP_BYTES) == "webp"
    assert ImagePreprocessor._detect_format(BMP_BYTES) == "bmp"
    assert ImagePreprocessor._detect_format(GIF_BYTES) == "gif"
