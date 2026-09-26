"""Extractor for the SciOS Cognitive Core text perception modality."""

from __future__ import annotations

from typing import Any

from .parser import TextParser


class TextExtractor:
    """Extract deterministic structural features from parsed text."""

    def __init__(self, parser: TextParser | None = None) -> None:
        """Initialize the extractor with an optional parser."""

        if parser is not None and not isinstance(parser, TextParser):
            raise TypeError("parser must be a TextParser")

        self.parser = parser or TextParser()

    def extract(
        self,
        text: str,
        parsed: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Extract structural features, entities, and relations."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if parsed is None:
            parsed_result = self.parser.parse(text)
        else:
            if not isinstance(parsed, dict):
                raise TypeError("parsed must be a dictionary")

            parsed_result = dict(parsed)

        tokens = parsed_result.get("tokens", [])
        token_count = parsed_result.get("token_count", len(tokens))
        word_count = parsed_result.get("word_count", 0)
        sentence_count = parsed_result.get("sentence_count", 0)

        return {
            "features": {
                "character_count": len(text),
                "token_count": token_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
            },
            "entities": [],
            "relations": [],
        }


__all__ = ["TextExtractor"]
