"""Contract tests for the document perceptor."""

from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)
from scios.cognitive_core.perception.modalities.document.html import (
    HtmlDocumentReader,
)
from scios.cognitive_core.perception.modalities.document.markdown import (
    MarkdownDocumentReader,
)
from scios.cognitive_core.perception.modalities.document.office import (
    OfficeDocumentReader,
)
from scios.cognitive_core.perception.modalities.document.pdf import (
    PdfDocumentReader,
)
from scios.cognitive_core.perception.modalities.document.perceptor import (
    DocumentPerceptor,
)


def make_office_bytes(member: str) -> bytes:
    """Create a minimal OOXML-like ZIP package."""

    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        archive.writestr(member, b"<document />")

    return buffer.getvalue()


def test_constructor_defaults() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor.name == "document"
    assert perceptor.modality is Modality.DOCUMENT
    assert isinstance(perceptor.pdf_reader, PdfDocumentReader)
    assert isinstance(perceptor.markdown_reader, MarkdownDocumentReader)
    assert isinstance(perceptor.html_reader, HtmlDocumentReader)
    assert isinstance(perceptor.office_reader, OfficeDocumentReader)


def test_constructor_accepts_custom_readers() -> None:
    pdf = PdfDocumentReader()
    markdown = MarkdownDocumentReader()
    html = HtmlDocumentReader()
    office = OfficeDocumentReader()

    perceptor = DocumentPerceptor(
        pdf_reader=pdf,
        markdown_reader=markdown,
        html_reader=html,
        office_reader=office,
    )

    assert perceptor.pdf_reader is pdf
    assert perceptor.markdown_reader is markdown
    assert perceptor.html_reader is html
    assert perceptor.office_reader is office


@pytest.mark.parametrize(
    "kwargs",
    [
        {"pdf_reader": object()},
        {"markdown_reader": object()},
        {"html_reader": object()},
        {"office_reader": object()},
    ],
)
def test_constructor_rejects_invalid_readers(kwargs: dict[str, object]) -> None:
    with pytest.raises(TypeError):
        DocumentPerceptor(**kwargs)


def test_detect_pdf_path() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(Path("sample.pdf")) == "pdf"


def test_detect_markdown_path() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(Path("sample.md")) == "markdown"


def test_detect_markdown_extension_path() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(Path("sample.markdown")) == "markdown"


def test_detect_html_path() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(Path("sample.html")) == "html"


def test_detect_htm_path() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(Path("sample.htm")) == "html"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (Path("sample.docx"), "docx"),
        (Path("sample.xlsx"), "xlsx"),
        (Path("sample.pptx"), "pptx"),
    ],
)
def test_detect_office_paths(path: Path, expected: str) -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(path) == expected


def test_detect_raw_markdown_string() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format("# Heading\n\nText") == "markdown"


def test_detect_raw_html_string() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(
        "<html><body><h1>Hello</h1></body></html>"
    ) == "html"


def test_detect_pdf_bytes() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(b"%PDF-1.7\n") == "pdf"


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("word/document.xml", "docx"),
        ("xl/workbook.xml", "xlsx"),
        ("ppt/presentation.xml", "pptx"),
    ],
)
def test_detect_office_bytes(member: str, expected: str) -> None:
    perceptor = DocumentPerceptor()

    data = make_office_bytes(member)

    assert perceptor._detect_format(data) == expected


def test_detect_html_bytes() -> None:
    perceptor = DocumentPerceptor()

    data = b"<html><body><h1>Hello</h1></body></html>"

    assert perceptor._detect_format(data) == "html"


def test_detect_markdown_bytes() -> None:
    perceptor = DocumentPerceptor()

    assert perceptor._detect_format(b"# Heading\n\nText") == "markdown"


def test_empty_string_is_rejected() -> None:
    perceptor = DocumentPerceptor()

    with pytest.raises(PerceptionInputError):
        perceptor._detect_format("")


def test_unsupported_path_extension_is_rejected() -> None:
    perceptor = DocumentPerceptor()

    with pytest.raises(PerceptionInputError):
        perceptor._detect_format(Path("sample.txt"))


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
def test_unsupported_input_type_is_rejected(value: object) -> None:
    perceptor = DocumentPerceptor()

    with pytest.raises(PerceptionInputError):
        perceptor._detect_format(value)


def test_markdown_perception() -> None:
    perceptor = DocumentPerceptor()

    result = perceptor.perceive("# Hello\n\nWorld")

    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.DOCUMENT
    assert result.content == "# Hello\n\nWorld"
    assert result.features["document_type"] == "markdown"
    assert result.features["text_length"] == 0
    assert result.confidence == 1.0
    assert result.entities == []
    assert result.relations == []
    assert result.metadata["format"] == "markdown"
    assert result.metadata["document_type"] == "markdown"


def test_html_perception() -> None:
    perceptor = DocumentPerceptor()

    source = "<html><title>Test</title><h1>Hello</h1></html>"

    result = perceptor.perceive(source)

    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.DOCUMENT
    assert result.content == source
    assert result.features["document_type"] == "html"
    assert result.confidence == 1.0
    assert result.metadata["format"] == "html"


def test_pdf_perception(tmp_path: Path) -> None:
    path = tmp_path / "sample.pdf"
    path.write_bytes(b"%PDF-1.7\n1 0 obj\n/Type /Page\n")

    result = DocumentPerceptor().perceive(path)

    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.DOCUMENT
    assert result.content.startswith(b"%PDF-1.7")
    assert result.features["document_type"] == "pdf"
    assert result.metadata["format"] == "pdf"


def test_office_perception(tmp_path: Path) -> None:
    path = tmp_path / "sample.docx"

    data = make_office_bytes("word/document.xml")
    path.write_bytes(data)

    result = DocumentPerceptor().perceive(path)

    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.DOCUMENT
    assert result.content == data
    assert result.features["document_type"] == "docx"
    assert result.metadata["format"] == "docx"


def test_metadata_is_preserved() -> None:
    result = DocumentPerceptor().perceive(
        "# Hello",
        metadata={
            "source": "test",
            "request_id": "abc",
        },
    )

    assert result.metadata["source"] == "test"
    assert result.metadata["request_id"] == "abc"
    assert result.metadata["format"] == "markdown"
    assert result.metadata["document_type"] == "markdown"


def test_reader_processing_failure_is_wrapped() -> None:
    class BrokenMarkdownReader(MarkdownDocumentReader):
        def read(self, source):
            raise RuntimeError("boom")

    perceptor = DocumentPerceptor(
        markdown_reader=BrokenMarkdownReader(),
    )

    with pytest.raises(PerceptionProcessingError):
        perceptor.perceive("# Hello")


def test_input_error_is_not_wrapped() -> None:
    perceptor = DocumentPerceptor()

    with pytest.raises(PerceptionInputError):
        perceptor.perceive(Path("missing.xyz"))
