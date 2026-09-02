"""Contract tests for the image loader."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
)
from scios.cognitive_core.perception.modalities.image.loader import (
    ImageLoader,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"
JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-data"
WEBP_BYTES = b"RIFFxxxxWEBPfake-webp-data"
BMP_BYTES = b"BMfake-bmp-data"
GIF_BYTES = b"GIF89afake-gif-data"


def test_constructor() -> None:
    loader = ImageLoader()

    assert isinstance(loader, ImageLoader)


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
def test_validate_bytes(data: bytes) -> None:
    ImageLoader().validate_source(data)


def test_validate_path(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(PNG_BYTES)

    ImageLoader().validate_source(path)


def test_validate_string_path(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(PNG_BYTES)

    ImageLoader().validate_source(str(path))


def test_empty_bytes_rejected() -> None:
    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source(b"")


def test_empty_string_rejected() -> None:
    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source("")


def test_missing_path_rejected(tmp_path: Path) -> None:
    path = tmp_path / "missing.png"

    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source(path)


def test_directory_rejected(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.mkdir()

    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source(path)


def test_unsupported_extension_rejected(tmp_path: Path) -> None:
    path = tmp_path / "image.txt"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source(path)


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        1.5,
        [],
        {},
    ],
)
def test_unsupported_source_type_rejected(value: object) -> None:
    with pytest.raises(PerceptionInputError):
        ImageLoader().validate_source(value)


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
def test_load_bytes(data: bytes, expected: str) -> None:
    result = ImageLoader().load(data)

    assert result["content"] == data
    assert result["metadata"]["source_name"] is None
    assert result["metadata"]["format"] == expected


def test_load_png_path(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    path.write_bytes(PNG_BYTES)

    result = ImageLoader().load(path)

    assert result["content"] == PNG_BYTES
    assert result["metadata"] == {
        "source_name": "sample.png",
        "format": "png",
    }


def test_load_string_path(tmp_path: Path) -> None:
    path = tmp_path / "sample.jpg"
    path.write_bytes(JPEG_BYTES)

    result = ImageLoader().load(str(path))

    assert result["content"] == JPEG_BYTES
    assert result["metadata"]["source_name"] == "sample.jpg"
    assert result["metadata"]["format"] == "jpeg"


def test_extension_content_mismatch_rejected(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    path.write_bytes(JPEG_BYTES)

    with pytest.raises(PerceptionInputError):
        ImageLoader().load(path)


@pytest.mark.parametrize(
    "data",
    [
        b"invalid",
        b"",
        b"not-an-image",
    ],
)
def test_invalid_image_bytes_rejected(data: bytes) -> None:
    with pytest.raises(PerceptionInputError):
        ImageLoader().load(data)


def test_private_path_detection_contract() -> None:
    assert (
        ImageLoader()._detect_format_from_path(Path("a.png"))
        == "png"
    )
    assert (
        ImageLoader()._detect_format_from_path(Path("a.jpg"))
        == "jpeg"
    )
    assert (
        ImageLoader()._detect_format_from_path(Path("a.jpeg"))
        == "jpeg"
    )
    assert (
        ImageLoader()._detect_format_from_path(Path("a.webp"))
        == "webp"
    )


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
def test_private_byte_detection_contract(
    data: bytes,
    expected: str,
) -> None:
    assert ImageLoader()._detect_format_from_bytes(data) == expected
