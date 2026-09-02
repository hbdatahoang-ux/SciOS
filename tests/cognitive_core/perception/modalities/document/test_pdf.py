"""Tests for the PDF document adapter."""

from pathlib import Path

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.document.pdf import (
    PdfDocumentReader,
)


PDF_HEADER = b"%PDF-1.7\n"


@pytest.fixture
def reader() -> PdfDocumentReader:
    return PdfDocumentReader()


def test_reader_can_be_created() -> None:
    assert isinstance(PdfDocumentReader(), PdfDocumentReader)


def test_validate_bytes(reader: PdfDocumentReader) -> None:
    reader.validate_source(PDF_HEADER)


def test_validate_path(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(PDF_HEADER)

    reader.validate_source(path)


def test_validate_string_path(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(PDF_HEADER)

    reader.validate_source(str(path))


@pytest.mark.parametrize("source", [None, 123, object()])
def test_invalid_source_type(
    reader: PdfDocumentReader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(source)


def test_missing_path_raises_input_error(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(tmp_path / "missing.pdf")


def test_directory_path_raises_input_error(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "document.pdf"
    directory.mkdir()

    with pytest.raises(PerceptionInputError):
        reader.validate_source(directory)


def test_non_pdf_extension_raises_input_error(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(PDF_HEADER)

    with pytest.raises(PerceptionInputError):
        reader.validate_source(path)


def test_empty_bytes_raise_input_error(
    reader: PdfDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(b"")


def test_invalid_pdf_header_raises_input_error(
    reader: PdfDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.read(b"not a pdf")


def test_read_bytes_returns_structured_representation(
    reader: PdfDocumentReader,
) -> None:
    result = reader.read(PDF_HEADER)

    assert result["content"] == PDF_HEADER
    assert result["metadata"] == {
        "source_name": None,
        "format": "pdf",
    }
    assert result["page_count"] == 0
    assert result["pages"] == []


def test_read_path_returns_source_metadata(
    reader: PdfDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.pdf"
    path.write_bytes(PDF_HEADER)

    result = reader.read(path)

    assert result["content"] == PDF_HEADER
    assert result["metadata"]["source_name"] == "sample.pdf"
    assert result["metadata"]["format"] == "pdf"


def test_page_count_uses_pdf_page_markers(
    reader: PdfDocumentReader,
) -> None:
    data = (
        b"%PDF-1.7\n"
        b"1 0 obj /Type /Page endobj\n"
        b"2 0 obj /Type /Page endobj\n"
    )

    result = reader.read(data)

    assert result["page_count"] == 2


def test_read_returns_empty_pages_until_page_extraction_is_configured(
    reader: PdfDocumentReader,
) -> None:
    result = reader.read(PDF_HEADER)

    assert result["pages"] == []


def test_processing_error_is_wrapped(
    reader: PdfDocumentReader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reader,
        "_count_pages",
        lambda data: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    with pytest.raises(PerceptionProcessingError):
        reader.read(PDF_HEADER)
