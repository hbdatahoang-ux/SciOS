"""Text cleaner for the SciOS Cognitive Core text perception modality."""

from __future__ import annotations

import re


_WHITESPACE_PATTERN = re.compile(r"\s+", flags=re.UNICODE)


class TextCleaner:
    """Deterministic, dependency-free text normalizer."""

    def clean(self, text: str) -> str:
        """Normalize whitespace without changing textual semantics."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        return _WHITESPACE_PATTERN.sub(" ", text).strip()

    def __call__(self, text: str) -> str:
        """Clean text using the callable interface."""

        return self.clean(text)


__all__ = ["TextCleaner"]
