"""Tests for the Markdown document adapter."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.document.markdown import (
    MarkdownDocumentReader,
)


@pytest.fixture
def reader() -> MarkdownDocumentReader:
    return MarkdownDocumentReader()


MARKDOWN = """# Title

Introduction.

## Section One

Section content.

### Subsection

More content.

[Example](https://example.com)
"""


def test_reader_can_be_created() -> None:
    assert isinstance(MarkdownDocumentReader(), MarkdownDocumentReader)


def test_validate_bytes(reader: MarkdownDocumentReader) -> None:
    reader.validate_source(b"# Title")


def test_validate_md_path(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.md"
    path.write_text("# Title", encoding="utf-8")

    reader.validate_source(path)


def test_validate_markdown_path(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.markdown"
    path.write_text("# Title", encoding="utf-8")

    reader.validate_source(path)


@pytest.mark.parametrize("source", [None, 123, object()])
def test_invalid_source_type(
    reader: MarkdownDocumentReader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(source)


def test_missing_path_raises_input_error(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(tmp_path / "missing.md")


def test_directory_path_raises_input_error(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "document.md"
    directory.mkdir()

    with pytest.raises(PerceptionInputError):
        reader.validate_source(directory)


def test_invalid_extension_raises_input_error(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_text("# Title", encoding="utf-8")

    with pytest.raises(PerceptionInputError):
        reader.validate_source(path)


def test_empty_bytes_raise_input_error(
    reader: MarkdownDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(b"")


def test_read_bytes_returns_structured_representation(
    reader: MarkdownDocumentReader,
) -> None:
    result = reader.read(MARKDOWN.encode("utf-8"))

    assert result["content"] == MARKDOWN
    assert result["metadata"] == {
        "source_name": None,
        "format": "markdown",
    }
    assert result["heading_count"] == 3
    assert result["link_count"] == 1


def test_read_path_returns_source_metadata(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.md"
    path.write_text(MARKDOWN, encoding="utf-8")

    result = reader.read(path)

    assert result["metadata"]["source_name"] == "sample.md"
    assert result["metadata"]["format"] == "markdown"


def test_heading_count_is_deterministic(
    reader: MarkdownDocumentReader,
) -> None:
    result = reader.read("# One\n\n## Two\n\n### Three\n")

    assert result["heading_count"] == 3


def test_link_count_is_deterministic(
    reader: MarkdownDocumentReader,
) -> None:
    result = reader.read(
        "[One](https://one.example)\n"
        "[Two](https://two.example)\n"
    )

    assert result["link_count"] == 2


def test_sections_preserve_heading_structure(
    reader: MarkdownDocumentReader,
) -> None:
    result = reader.read(MARKDOWN)

    assert result["sections"] == [
        {
            "level": 1,
            "title": "Title",
            "content": "Introduction.",
        },
        {
            "level": 2,
            "title": "Section One",
            "content": "Section content.",
        },
        {
            "level": 3,
            "title": "Subsection",
            "content": (
                "More content.\n\n"
                "[Example](https://example.com)"
            ),
        },
    ]


def test_empty_markdown_has_no_sections(
    reader: MarkdownDocumentReader,
) -> None:
    result = reader.read("")

    assert result["heading_count"] == 0
    assert result["sections"] == []


def test_unicode_content_is_preserved(
    reader: MarkdownDocumentReader,
) -> None:
    content = "# Tiếng Việt\n\nXin chào 🌍"

    result = reader.read(content.encode("utf-8"))

    assert result["content"] == content
    assert result["sections"][0]["title"] == "Tiếng Việt"


def test_invalid_utf8_is_wrapped(
    reader: MarkdownDocumentReader,
) -> None:
    with pytest.raises(PerceptionProcessingError):
        reader.read(b"# \xff\xfe")


def test_processing_error_is_wrapped(
    reader: MarkdownDocumentReader,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "document.md"
    path.write_text("# Title", encoding="utf-8")

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
    from scios.cognitive_core.perception.modalities.document import markdown

    assert markdown.__all__ == ["MarkdownDocumentReader"]