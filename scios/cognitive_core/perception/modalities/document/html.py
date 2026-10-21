"""HTML adapter for the SciOS Cognitive Core document modality."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ...core.errors import (
    PerceptionInputError,
    PerceptionProcessingError,
)


_TITLE_PATTERN = re.compile(
    r"<title\b[^>]*>(.*?)</title\s*>",
    flags=re.IGNORECASE | re.DOTALL,
)

_HEADING_PATTERN = re.compile(
    r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>",
    flags=re.IGNORECASE | re.DOTALL,
)

_LINK_PATTERN = re.compile(
    r"<a\b[^>]*\bhref\s*=\s*"
    r"""(?:"[^"]*"|'[^']*'|[^\s>]+)""",
    flags=re.IGNORECASE,
)

_IMAGE_PATTERN = re.compile(
    r"<img\b[^>]*>",
    flags=re.IGNORECASE,
)


class HtmlDocumentReader:
    """Read HTML documents into a deterministic representation."""

    def validate_source(self, source: Any) -> None:
        """Validate a supported HTML source."""

        if isinstance(source, bytes):
            if not source:
                raise PerceptionInputError(
                    "HTML source bytes must not be empty"
                )
            return

        if isinstance(source, str):
            if source == "":
                return

            path = Path(source)

            if path.exists():
                if not path.is_file():
                    raise PerceptionInputError(
                        f"HTML source is not a file: {path}"
                    )

                if path.suffix.lower() not in {".html", ".htm"}:
                    raise PerceptionInputError(
                        "HTML source must have a .html or .htm extension"
                    )

            return

        if isinstance(source, Path):
            if not source.exists():
                raise PerceptionInputError(
                    f"HTML source does not exist: {source}"
                )

            if not source.is_file():
                raise PerceptionInputError(
                    f"HTML source is not a file: {source}"
                )

            if source.suffix.lower() not in {".html", ".htm"}:
                raise PerceptionInputError(
                    "HTML source must have a .html or .htm extension"
                )

            return

        raise PerceptionInputError(
            "HTML source must be a path, string content, or bytes"
        )

    def read(self, source: str | Path | bytes) -> dict[str, Any]:
        """Read HTML source into a structured representation."""

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
                    "HTML source must be a path, string content, or bytes"
                )

            title_match = _TITLE_PATTERN.search(content)

            title = (
                self._strip_tags(title_match.group(1))
                if title_match
                else None
            )

            heading_matches = list(_HEADING_PATTERN.finditer(content))

            headings = [
                {
                    "level": int(match.group(1)),
                    "text": self._strip_tags(match.group(2)),
                }
                for match in heading_matches
            ]

            return {
                "content": content,
                "metadata": {
                    "source_name": source_name,
                    "format": "html",
                },
                "title": title,
                "heading_count": len(headings),
                "link_count": len(_LINK_PATTERN.findall(content)),
                "image_count": len(_IMAGE_PATTERN.findall(content)),
                "headings": headings,
            }

        except PerceptionInputError:
            raise
        except UnicodeDecodeError as exc:
            raise PerceptionProcessingError(
                "HTML document must be valid UTF-8"
            ) from exc
        except Exception as exc:
            raise PerceptionProcessingError(
                "HTML document processing failed"
            ) from exc

    @staticmethod
    def _strip_tags(value: str) -> str:
        """Remove HTML tags from a small structural text fragment."""

        return re.sub(r"<[^>]+>", "", value).strip()


__all__ = ["HtmlDocumentReader"]
