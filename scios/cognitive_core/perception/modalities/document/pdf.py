"""PDF adapter for the SciOS Cognitive Core document modality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


class PdfDocumentReader:
    """Read PDF documents into a deterministic document representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported PDF source."""

        if isinstance(source, (str, Path)):
            path = Path(source)

            if not path.exists():
                raise PerceptionInputError(
                    f"PDF source does not exist: {path}"
                )

            if not path.is_file():
                raise PerceptionInputError(
                    f"PDF source is not a file: {path}"
                )

            if path.suffix.lower() != ".pdf":
                raise PerceptionInputError(
                    "PDF source must have a .pdf extension"
                )

            return

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "PDF source bytes must not be empty"
                )

            return

        raise PerceptionInputError(
            "PDF source must be a path or bytes"
        )

    def read(self, source: str | Path | bytes) -> dict[str, Any]:
        """Read a PDF source into a structured representation."""

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                data = source
                source_name = None
            else:
                path = Path(source)
                data = path.read_bytes()
                source_name = path.name

            if not data.startswith(b"%PDF-"):
                raise PerceptionInputError(
                    "source does not contain a valid PDF header"
                )

            return {
                "content": data,
                "metadata": {
                    "source_name": source_name,
                    "format": "pdf",
                },
                "page_count": self._count_pages(data),
                "pages": [],
            }

        except PerceptionInputError:
            raise
        except Exception as exc:
            raise PerceptionProcessingError(
                "PDF document processing failed"
            ) from exc

    @staticmethod
    def _count_pages(data: bytes) -> int:
        """Return a conservative page count from PDF page objects."""

        marker = b"/Type /Page"
        count = data.count(marker)

        if count <= 0:
            return 0

        return count


__all__ = ["PdfDocumentReader"]
