"""Office document adapter for the SciOS Cognitive Core document modality."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile
from io import BytesIO
from xml.etree import ElementTree


_SUPPORTED_EXTENSIONS = {
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".pptx": "pptx",
}


class OfficeDocumentReader:
    """Read Office Open XML documents into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported Office document source."""

        from ...core.errors import PerceptionInputError

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "Office source bytes must not be empty"
                )
            return

        if isinstance(source, Path):
            self._validate_path(source)
            return

        if isinstance(source, str):
            if not source:
                raise PerceptionInputError(
                    "Office source string must not be empty"
                )

            self._validate_path(Path(source))
            return

        raise PerceptionInputError(
            "Office source must be a path or bytes"
        )

    def read(self, source: str | Path | bytes) -> dict[str, Any]:
        """Read an Office Open XML document."""

        from ...core.errors import (
            PerceptionInputError,
            PerceptionProcessingError,
        )

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                data = source
                source_name = None
                document_type = self._detect_type_from_bytes(data)
            else:
                path = Path(source)
                data = path.read_bytes()
                source_name = path.name
                document_type = self._detect_type_from_path(path)

            with ZipFile(BytesIO(data)) as archive:
                names = archive.namelist()

                if not names:
                    raise PerceptionInputError(
                        "Office document archive is empty"
                    )

                text = self._extract_text(
                    archive,
                    document_type,
                )

                return {
                    "content": data,
                    "metadata": {
                        "source_name": source_name,
                        "format": document_type,
                    },
                    "document_type": document_type,
                    "entry_count": len(names),
                    "text": text,
                }

        except PerceptionInputError:
            raise
        except (BadZipFile, OSError, ElementTree.ParseError) as exc:
            raise PerceptionProcessingError(
                "Office document processing failed"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "Office document processing failed"
            ) from exc

    def _validate_path(self, path: Path) -> None:
        from ...core.errors import PerceptionInputError

        if not path.exists():
            raise PerceptionInputError(
                f"Office source does not exist: {path}"
            )

        if not path.is_file():
            raise PerceptionInputError(
                f"Office source is not a file: {path}"
            )

        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise PerceptionInputError(
                "Office source must have a .docx, .xlsx, or .pptx extension"
            )

    @staticmethod
    def _detect_type_from_path(path: Path) -> str:
        from ...core.errors import PerceptionInputError

        try:
            return _SUPPORTED_EXTENSIONS[path.suffix.lower()]
        except KeyError as exc:
            raise PerceptionInputError(
                "Office source must have a .docx, .xlsx, or .pptx extension"
            ) from exc

    def detect_format(self, data: bytes) -> str:
        """Detect the supported Office format from package bytes."""

        from ...core.errors import PerceptionInputError

        if not isinstance(data, bytes):
            raise PerceptionInputError(
                "Office source must be bytes"
            )

        return self._detect_type_from_bytes(data)

    @staticmethod
    def _detect_type_from_bytes(data: bytes) -> str:
        from ...core.errors import PerceptionInputError

        try:
            with ZipFile(BytesIO(data)) as archive:
                names = set(archive.namelist())
        except BadZipFile as exc:
            raise PerceptionInputError(
                "Office source bytes must be a valid ZIP archive"
            ) from exc

        if "word/document.xml" in names:
            return "docx"

        if "xl/workbook.xml" in names:
            return "xlsx"

        if "ppt/presentation.xml" in names:
            return "pptx"

        raise PerceptionInputError(
            "Office source bytes are not a supported DOCX, XLSX, or PPTX document"
        )

    @staticmethod
    def _extract_text(
        archive: ZipFile,
        document_type: str,
    ) -> str:
        if document_type == "docx":
            return OfficeDocumentReader._extract_docx_text(archive)

        if document_type == "xlsx":
            return OfficeDocumentReader._extract_xlsx_text(archive)

        if document_type == "pptx":
            return OfficeDocumentReader._extract_pptx_text(archive)

        raise ValueError(
            f"unsupported Office document type: {document_type}"
        )

    @staticmethod
    def _xml_text(data: bytes) -> list[str]:
        root = ElementTree.fromstring(data)

        values: list[str] = []

        for element in root.iter():
            if element.text and element.text.strip():
                values.append(element.text.strip())

        return values

    @staticmethod
    def _extract_docx_text(archive: ZipFile) -> str:
        data = archive.read("word/document.xml")
        values = OfficeDocumentReader._xml_text(data)

        return "\n".join(values)

    @staticmethod
    def _extract_xlsx_text(archive: ZipFile) -> str:
        values: list[str] = []

        if "xl/sharedStrings.xml" in archive.namelist():
            values.extend(
                OfficeDocumentReader._xml_text(
                    archive.read("xl/sharedStrings.xml")
                )
            )

        if "xl/workbook.xml" in archive.namelist():
            values.extend(
                OfficeDocumentReader._xml_text(
                    archive.read("xl/workbook.xml")
                )
            )

        return "\n".join(values)

    @staticmethod
    def _extract_pptx_text(archive: ZipFile) -> str:
        values: list[str] = []

        for name in sorted(archive.namelist()):
            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                values.extend(
                    OfficeDocumentReader._xml_text(
                        archive.read(name)
                    )
                )

        return "\n".join(values)


__all__ = ["OfficeDocumentReader"]
