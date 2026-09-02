"""Tests for the Office document adapter."""

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest

from scios.cognitive_core.perception.core import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from scios.cognitive_core.perception.modalities.document.office import (
    OfficeDocumentReader,
)


@pytest.fixture
def reader() -> OfficeDocumentReader:
    return OfficeDocumentReader()


def make_office_package(
    main_file: str,
    main_xml: str,
    extra_files: dict[str, str] | None = None,
) -> bytes:
    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        archive.writestr(main_file, main_xml)

        for name, content in (extra_files or {}).items():
            archive.writestr(name, content)

    return buffer.getvalue()


DOCX = make_office_package(
    "word/document.xml",
    """
    <document>
        <body>
            <p>Hello</p>
            <p>SciOS</p>
        </body>
    </document>
    """,
)

XLSX = make_office_package(
    "xl/workbook.xml",
    """
    <workbook>
        <sheet name="Sheet1" />
    </workbook>
    """,
    {
        "xl/sharedStrings.xml": """
        <sst>
            <si><t>Scientific</t></si>
            <si><t>Operating System</t></si>
        </sst>
        """,
    },
)

PPTX = make_office_package(
    "ppt/presentation.xml",
    """
    <presentation>
        <sldIdLst />
    </presentation>
    """,
    {
        "ppt/slides/slide1.xml": """
        <slide>
            <txBody>
                <p>SciOS</p>
                <p>Perception</p>
            </txBody>
        </slide>
        """,
    },
)


def test_reader_can_be_created() -> None:
    assert isinstance(OfficeDocumentReader(), OfficeDocumentReader)


@pytest.mark.parametrize(
    "data",
    [DOCX, XLSX, PPTX],
)
def test_validate_bytes(
    reader: OfficeDocumentReader,
    data: bytes,
) -> None:
    reader.validate_source(data)


@pytest.mark.parametrize(
    ("suffix", "data"),
    [
        (".docx", DOCX),
        (".xlsx", XLSX),
        (".pptx", PPTX),
    ],
)
def test_validate_supported_path(
    reader: OfficeDocumentReader,
    tmp_path: Path,
    suffix: str,
    data: bytes,
) -> None:
    path = tmp_path / f"document{suffix}"
    path.write_bytes(data)

    reader.validate_source(path)


@pytest.mark.parametrize("source", [None, 123, object()])
def test_invalid_source_type(
    reader: OfficeDocumentReader,
    source: object,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(source)


def test_empty_bytes_raise_input_error(
    reader: OfficeDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(b"")


def test_empty_string_raises_input_error(
    reader: OfficeDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source("")


def test_missing_path_raises_input_error(
    reader: OfficeDocumentReader,
    tmp_path: Path,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.validate_source(tmp_path / "missing.docx")


def test_directory_path_raises_input_error(
    reader: OfficeDocumentReader,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "document.docx"
    directory.mkdir()

    with pytest.raises(PerceptionInputError):
        reader.validate_source(directory)


def test_invalid_extension_raises_input_error(
    reader: OfficeDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_text("not office", encoding="utf-8")

    with pytest.raises(PerceptionInputError):
        reader.validate_source(path)


def test_read_docx_bytes(
    reader: OfficeDocumentReader,
) -> None:
    result = reader.read(DOCX)

    assert result["content"] == DOCX
    assert result["metadata"] == {
        "source_name": None,
        "format": "docx",
    }
    assert result["document_type"] == "docx"
    assert result["entry_count"] == 1
    assert "Hello" in result["text"]
    assert "SciOS" in result["text"]


def test_read_xlsx_bytes(
    reader: OfficeDocumentReader,
) -> None:
    result = reader.read(XLSX)

    assert result["document_type"] == "xlsx"
    assert "Scientific" in result["text"]
    assert "Operating System" in result["text"]


def test_read_pptx_bytes(
    reader: OfficeDocumentReader,
) -> None:
    result = reader.read(PPTX)

    assert result["document_type"] == "pptx"
    assert "SciOS" in result["text"]
    assert "Perception" in result["text"]


def test_read_path_returns_source_metadata(
    reader: OfficeDocumentReader,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.docx"
    path.write_bytes(DOCX)

    result = reader.read(path)

    assert result["metadata"]["source_name"] == "sample.docx"
    assert result["metadata"]["format"] == "docx"


def test_invalid_zip_bytes_are_wrapped(
    reader: OfficeDocumentReader,
) -> None:
    with pytest.raises(PerceptionInputError):
        reader.read(b"not a zip archive")


def test_unsupported_zip_bytes_raise_input_error(
    reader: OfficeDocumentReader,
) -> None:
    data = make_office_package(
        "[Content_Types].xml",
        "<Types />",
    )

    with pytest.raises(PerceptionInputError):
        reader.read(data)


def test_invalid_xml_is_wrapped(
    reader: OfficeDocumentReader,
) -> None:
    data = make_office_package(
        "word/document.xml",
        "<document>",
    )

    with pytest.raises(PerceptionProcessingError):
        reader.read(data)


def test_processing_error_is_wrapped(
    reader: OfficeDocumentReader,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "document.docx"
    path.write_bytes(DOCX)

    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("boom")
        ),
    )

    with pytest.raises(PerceptionProcessingError):
        reader.read(path)


def test_module_public_exports() -> None:
    from scios.cognitive_core.perception.modalities.document import office

    assert office.__all__ == ["OfficeDocumentReader"]
