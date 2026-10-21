"""Contract tests for image detection."""

import pytest

from scios.cognitive_core.perception.core import PerceptionInputError
from scios.cognitive_core.perception.modalities.image.detector import (
    ImageDetector,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"
JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-data"
WEBP_BYTES = b"RIFFxxxxWEBPfake-webp-data"
BMP_BYTES = b"BMfake-bmp-data"
GIF_BYTES = b"GIF89afake-gif-data"


@pytest.fixture
def detector() -> ImageDetector:
    return ImageDetector()


def test_constructor() -> None:
    detector = ImageDetector()

    assert isinstance(detector, ImageDetector)


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
    detector: ImageDetector,
    data: bytes,
) -> None:
    detector.validate_input(data)


def test_validate_input_rejects_empty_bytes(
    detector: ImageDetector,
) -> None:
    with pytest.raises(PerceptionInputError):
        detector.validate_input(b"")


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
    detector: ImageDetector,
    value: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        detector.validate_input(value)


@pytest.mark.parametrize(
    "data",
    [
        b"invalid-image",
        b"not-an-image",
        b"\x00\x01\x02",
    ],
)
def test_validate_input_rejects_invalid_image_bytes(
    detector: ImageDetector,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        detector.validate_input(data)


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
def test_detect_reports_image_format(
    detector: ImageDetector,
    data: bytes,
    expected_format: str,
) -> None:
    result = detector.detect(data)

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
def test_detect_returns_empty_detections(
    detector: ImageDetector,
    data: bytes,
) -> None:
    result = detector.detect(data)

    assert result["detections"] == []
    assert result["count"] == 0


def test_detect_returns_expected_structure(
    detector: ImageDetector,
) -> None:
    result = detector.detect(PNG_BYTES)

    assert set(result) == {
        "detections",
        "count",
        "metadata",
    }

    assert set(result["metadata"]) == {
        "format",
        "backend",
    }


def test_detect_backend_is_deterministic(
    detector: ImageDetector,
) -> None:
    first = detector.detect(PNG_BYTES)
    second = detector.detect(PNG_BYTES)

    assert first == second


def test_detect_backend_name(
    detector: ImageDetector,
) -> None:
    result = detector.detect(PNG_BYTES)

    assert result["metadata"]["backend"] == "deterministic"


@pytest.mark.parametrize(
    "data",
    [
        b"invalid-image",
        b"",
        b"not-an-image",
    ],
)
def test_detect_rejects_invalid_input(
    detector: ImageDetector,
    data: bytes,
) -> None:
    with pytest.raises(PerceptionInputError):
        detector.detect(data)


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
    assert ImageDetector._detect_format(data) == expected
