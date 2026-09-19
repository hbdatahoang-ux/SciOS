"""Document perceptor for the SciOS Cognitive Core."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...core.base import BasePerceptor
from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)
from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus, RawInput
from .html import HtmlDocumentReader
from .markdown import MarkdownDocumentReader
from .office import OfficeDocumentReader
from .pdf import PdfDocumentReader


class DocumentPerceptor(BasePerceptor):
    """Orchestrate perception across supported document formats."""

    def __init__(
        self,
        *,
        name: str = "document",
        pdf_reader: PdfDocumentReader | None = None,
        markdown_reader: MarkdownDocumentReader | None = None,
        html_reader: HtmlDocumentReader | None = None,
        office_reader: OfficeDocumentReader | None = None,
    ) -> None:
        """Initialize the document perception pipeline."""

        super().__init__(
            name=name,
            modality=Modality.DOCUMENT,
        )

        if pdf_reader is not None and not isinstance(
            pdf_reader,
            PdfDocumentReader,
        ):
            raise TypeError("pdf_reader must be a PdfDocumentReader")

        if markdown_reader is not None and not isinstance(
            markdown_reader,
            MarkdownDocumentReader,
        ):
            raise TypeError(
                "markdown_reader must be a MarkdownDocumentReader"
            )

        if html_reader is not None and not isinstance(
            html_reader,
            HtmlDocumentReader,
        ):
            raise TypeError("html_reader must be an HtmlDocumentReader")

        if office_reader is not None and not isinstance(
            office_reader,
            OfficeDocumentReader,
        ):
            raise TypeError("office_reader must be an OfficeDocumentReader")

        self.pdf_reader = pdf_reader or PdfDocumentReader()
        self.markdown_reader = (
            markdown_reader or MarkdownDocumentReader()
        )
        self.html_reader = html_reader or HtmlDocumentReader()
        self.office_reader = office_reader or OfficeDocumentReader()

    def perceive(
        self,
        raw_input: RawInput,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Transform a supported document into a perception result."""

        input_metadata = dict(metadata or {})

        try:
            document_format = self._detect_format(raw_input)
            document = self._read(raw_input, document_format)

            result_metadata = {
                **input_metadata,
                **document.get("metadata", {}),
                "document_type": document_format,
            }

            content = document.get("content")

            return PerceptionResult(
                status=PerceptionStatus.SUCCESS,
                modality=Modality.DOCUMENT,
                content=content,
                features={
                    "document_type": document_format,
                    "text_length": len(document.get("text", "")),
                },
                entities=[],
                relations=[],
                confidence=1.0,
                metadata=result_metadata,
            )

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "document perception processing failed"
            ) from exc

    def _detect_format(self, source: RawInput) -> str:
        """Detect the document format from the source."""

        if isinstance(source, bytes):
            return self.office_reader.detect_format(source) \
                if self._looks_like_office(source) \
                else self._detect_text_bytes_format(source)

        if isinstance(source, Path):
            return self._detect_path_format(source)

        if isinstance(source, str):
            if not source:
                raise PerceptionInputError(
                    "document input must not be empty"
                )

            path = Path(source)

            if path.exists():
                return self._detect_path_format(path)

            return "html" if self._looks_like_html(source) else "markdown"

        raise PerceptionInputError(
            "document input must be a supported path, string, or bytes"
        )

    def _read(
        self,
        source: RawInput,
        document_format: str,
    ) -> dict[str, Any]:
        """Read a document using its format-specific adapter."""

        if document_format == "pdf":
            return self.pdf_reader.read(source)

        if document_format == "markdown":
            return self.markdown_reader.read(source)

        if document_format == "html":
            return self.html_reader.read(source)

        if document_format in {"docx", "xlsx", "pptx"}:
            return self.office_reader.read(source)

        raise PerceptionInputError(
            f"unsupported document format: {document_format}"
        )

    @staticmethod
    def _detect_path_format(path: Path) -> str:
        """Detect format from a document path."""

        suffix = path.suffix.lower()

        formats = {
            ".pdf": "pdf",
            ".md": "markdown",
            ".markdown": "markdown",
            ".html": "html",
            ".htm": "html",
            ".docx": "docx",
            ".xlsx": "xlsx",
            ".pptx": "pptx",
        }

        try:
            return formats[suffix]
        except KeyError as exc:
            raise PerceptionInputError(
                f"unsupported document extension: {suffix}"
            ) from exc

    @staticmethod
    def _looks_like_html(value: str) -> bool:
        """Return whether a string appears to contain HTML."""

        lowered = value.lower()

        return (
            "<html" in lowered
            or "<body" in lowered
            or "<title" in lowered
            or "<h1" in lowered
            or "<p" in lowered
        )

    @staticmethod
    def _looks_like_office(data: bytes) -> bool:
        """Return whether bytes appear to be an Office ZIP package."""

        return data.startswith(b"PK\x03\x04")

    @staticmethod
    def _detect_text_bytes_format(data: bytes) -> str:
        """Detect PDF, HTML, or Markdown from byte content."""

        if data.startswith(b"%PDF-"):
            return "pdf"

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PerceptionInputError(
                "document bytes must be valid UTF-8"
            ) from exc

        if DocumentPerceptor._looks_like_html(text):
            return "html"

        return "markdown"


__all__ = ["DocumentPerceptor"]

