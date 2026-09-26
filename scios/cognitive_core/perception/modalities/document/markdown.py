"""Markdown adapter for the SciOS Cognitive Core document modality."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_HEADING_PATTERN = re.compile(
    r"^(#{1,6})[ \t]+(.+?)\s*$",
    flags=re.MULTILINE,
)

_LINK_PATTERN = re.compile(
    r"\[[^\]]+\]\([^)]+\)",
)


class MarkdownDocumentReader:
    """Read Markdown documents into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported Markdown source."""

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "Markdown source bytes must not be empty"
                )
            return

        if isinstance(source, str):
            if source == "":
                return

            path = Path(source)

            if path.exists():
                if not path.is_file():
                    raise PerceptionInputError(
                        f"Markdown source is not a file: {path}"
                    )

                if path.suffix.lower() not in {".md", ".markdown"}:
                    raise PerceptionInputError(
                        "Markdown source must have a .md or .markdown extension"
                    )

            return

        if isinstance(source, Path):
            if not source.exists():
                raise PerceptionInputError(
                    f"Markdown source does not exist: {source}"
                )

            if not source.is_file():
                raise PerceptionInputError(
                    f"Markdown source is not a file: {source}"
                )

            if source.suffix.lower() not in {".md", ".markdown"}:
                raise PerceptionInputError(
                    "Markdown source must have a .md or .markdown extension"
                )

            return

        raise PerceptionInputError(
            "Markdown source must be a path, string content, or bytes"
        )

    def read(self, source: str | Path | bytes) -> dict[str, Any]:
        """Read Markdown source into a structured representation."""

        self.validate_source(source)

        try:
            if isinstance(source, bytes):
                content = source.decode("utf-8")
                source_name = None

            elif isinstance(source, Path):
                content = source.read_text(encoding="utf-8")
                source_name = source.name

            elif isinstance(source, str):
                if source == "":
                    content = ""
                    source_name = None
                else:
                    path = Path(source)

                    if path.exists():
                        content = path.read_text(encoding="utf-8")
                        source_name = path.name
                    else:
                        content = source
                        source_name = None

            else:
                raise PerceptionInputError(
                    "Markdown source must be a path, string content, or bytes"
                )

            headings = list(_HEADING_PATTERN.finditer(content))

            sections: list[dict[str, Any]] = []

            for index, match in enumerate(headings):
                start = match.end()
                end = (
                    headings[index + 1].start()
                    if index + 1 < len(headings)
                    else len(content)
                )

                sections.append(
                    {
                        "level": len(match.group(1)),
                        "title": match.group(2),
                        "content": content[start:end].strip(),
                    }
                )

            return {
                "content": content,
                "metadata": {
                    "source_name": source_name,
                    "format": "markdown",
                },
                "heading_count": len(headings),
                "link_count": len(_LINK_PATTERN.findall(content)),
                "sections": sections,
            }

        except PerceptionInputError:
            raise
        except UnicodeDecodeError as exc:
            raise PerceptionProcessingError(
                "Markdown document must be valid UTF-8"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "Markdown document processing failed"
            ) from exc


__all__ = ["MarkdownDocumentReader"]
