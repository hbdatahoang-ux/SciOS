"""Tests for the public Text modality API."""

from scios.cognitive_core.perception.modalities.text import (
    TextCleaner,
    TextExtractor,
    TextParser,
    TextPerceptor,
    TextTokenizer,
)


def test_public_exports_are_available() -> None:
    assert TextCleaner is not None
    assert TextExtractor is not None
    assert TextParser is not None
    assert TextPerceptor is not None
    assert TextTokenizer is not None


def test_public_exports_contract() -> None:
    from scios.cognitive_core.perception.modalities import text

    assert text.__all__ == [
        "TextCleaner",
        "TextExtractor",
        "TextParser",
        "TextPerceptor",
        "TextTokenizer",
    ]
