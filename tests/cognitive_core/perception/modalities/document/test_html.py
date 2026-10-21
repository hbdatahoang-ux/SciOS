"""Tests for the HTML document adapter."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.document.html import (
    HtmlDocumentReader,
)


@pytest.fixture
def reader() -> HtmlDocumentReader:
    return HtmlDocumentReader()


HTML = """<!DOCTYPE html>
<html>
<head>
    <title>SciOS Document</title>
</head>
<body>
    <h1>Main Title</h1>
    <p>Introduction.</p>

    <h2>Section One</h2>
    <p>Section content.</p>

    <h3>Subsection</h3>
    <p>More content.</p>

    <a href="https://example.com">Example</a>
    <img src="image.png" alt="Example image">
</body>
</html>
"""


def test_reader_can_be_created() -> None:
    assert isinstance(HtmlDocumentReader(), HtmlDocumentReader)


def test_validate_bytes(reader: HtmlDocumentReader) -> None:
    reader.validate_source(b"<html></html>")


def test_validate_html_path(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.html"
    path.write_text(HTML, encoding="utf-8")

    reader.validate_source(path)


def test_validate_htm_path(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.htm"
    path.write_text(HTML, encoding="utf-8")

    reader.validate_source(path)


@pytest.mark.parametrize("source", [None, 123, object()])
def test_invalid_source_type(
    reader: HtmlDocumentReader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(source)


def test_missing_path_raises_input_error(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(tmp_path / "missing.html")


def test_directory_path_raises_input_error(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "document.html"
    directory.mkdir()

    with pytest.raises(PerceptionInputError):
        reader.validate_source(directory)


def test_invalid_extension_raises_input_error(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_text(HTML, encoding="utf-8")

    with pytest.raises(PerceptionInputError):
        reader.validate_source(path)


def test_empty_bytes_raise_input_error(
    reader: HtmlDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(b"")


def test_read_bytes_returns_structured_representation(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read(HTML.encode("utf-8"))

    assert result["content"] == HTML
    assert result["metadata"] == {
        "source_name": None,
        "format": "html",
    }
    assert result["title"] == "SciOS Document"
    assert result["heading_count"] == 3
    assert result["link_count"] == 1
    assert result["image_count"] == 1


def test_read_path_returns_source_metadata(
    reader: HtmlDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.html"
    path.write_text(HTML, encoding="utf-8")

    result = reader.read(path)

    assert result["metadata"]["source_name"] == "sample.html"
    assert result["metadata"]["format"] == "html"


def test_heading_count_is_deterministic(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read(
        "<h1>One</h1>"
        "<h2>Two</h2>"
        "<h3>Three</h3>"
    )

    assert result["heading_count"] == 3


def test_link_count_is_deterministic(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read(
        '<a href="https://one.example">One</a>'
        '<a href="https://two.example">Two</a>'
    )

    assert result["link_count"] == 2


def test_image_count_is_deterministic(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read(
        '<img src="one.png">'
        '<img src="two.png">'
    )

    assert result["image_count"] == 2


def test_headings_preserve_structure(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read(HTML)

    assert result["headings"] == [
        {
            "level": 1,
            "text": "Main Title",
        },
        {
            "level": 2,
            "text": "Section One",
        },
        {
            "level": 3,
            "text": "Subsection",
        },
    ]


def test_title_is_optional(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read("<html><body><h1>Title</h1></body></html>")

    assert result["title"] is None


def test_empty_html_has_no_structure(
    reader: HtmlDocumentReader,
) -> None:
    result = reader.read("")

    assert result["content"] == ""
    assert result["title"] is None
    assert result["heading_count"] == 0
    assert result["link_count"] == 0
    assert result["image_count"] == 0
    assert result["headings"] == []


def test_unicode_content_is_preserved(
    reader: HtmlDocumentReader,
) -> None:
    content = "<html><body><h1>Tiếng Việt 🌍</h1></body></html>"

    result = reader.read(content.encode("utf-8"))

    assert result["content"] == content
    assert result["headings"][0]["text"] == "Tiếng Việt 🌍"


def test_invalid_utf8_is_wrapped(
    reader: HtmlDocumentReader,
) -> None:
    with pytest.raises(PerceptionProcessingError):
        reader.read(b"<html>\xff\xfe</html>")


def test_processing_error_is_wrapped(
    reader: HtmlDocumentReader,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "document.html"
    path.write_text(HTML, encoding="utf-8")

    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("boom")
        ),
    )

    with pytest.raises(PerceptionProcessingError):
        reader.read(path)


def test_module_public_exports() -> None:
    from scios.cognitive_core.perception.modalities.document import html

    assert html.__all__ == ["HtmlDocumentReader"]
