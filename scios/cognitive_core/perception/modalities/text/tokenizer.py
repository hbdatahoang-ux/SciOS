"""Tokenizer for the SciOS Cognitive Core text perception modality."""

from __future__ import annotations

import re


_TOKEN_PATTERN = re.compile(
    r"\w+(?:['’]\w+)*|[^\w\s]",
    flags=re.UNICODE,
)


class TextTokenizer:
    """Dependency-free tokenizer for normalized text."""

    def tokenize(self, text: str) -> list[str]:
        """Split text into word and punctuation tokens."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            return []

        return _TOKEN_PATTERN.findall(text)

    def __call__(self, text: str) -> list[str]:
        """Tokenize text using the callable interface."""

        return self.tokenize(text)


__all__ = ["TextTokenizer"]
