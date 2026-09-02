"""Parser for the SciOS Cognitive Core text perception modality."""

from __future__ import annotations

from typing import Any

from .tokenizer import TextTokenizer


class TextParser:
    """Create a lightweight structured representation of text."""

    def __init__(self, tokenizer: TextTokenizer | None = None) -> None:
        """Initialize the parser with an optional tokenizer."""

        if tokenizer is not None and not isinstance(
            tokenizer,
            TextTokenizer,
        ):
            raise TypeError("tokenizer must be a TextTokenizer")

        self.tokenizer = tokenizer or TextTokenizer()

    def parse(
        self,
        text: str,
        tokens: list[str] | None = None,
    ) -> dict[str, Any]:
        """Parse text into a deterministic intermediate representation."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if tokens is None:
            parsed_tokens = self.tokenizer.tokenize(text)
        else:
            if not isinstance(tokens, list):
                raise TypeError("tokens must be a list")

            if not all(isinstance(token, str) for token in tokens):
                raise TypeError("tokens must contain only strings")

            parsed_tokens = list(tokens)

        word_count = sum(
            1 for token in parsed_tokens if any(char.isalnum() for char in token)
        )

        sentence_count = sum(
            1
            for token in parsed_tokens
            if token in {".", "!", "?"}
        )

        return {
            "text": text,
            "tokens": parsed_tokens,
            "token_count": len(parsed_tokens),
            "word_count": word_count,
            "sentence_count": sentence_count,
        }


__all__ = ["TextParser"]
