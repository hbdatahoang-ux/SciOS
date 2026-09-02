import pytest

from scios.cognitive_core.perception.modalities.text.extractor import (
    TextExtractor,
)
from scios.cognitive_core.perception.modalities.text.parser import (
    TextParser,
)


@pytest.fixture
def extractor() -> TextExtractor:
    return TextExtractor()


def test_extractor_can_be_constructed() -> None:
    assert isinstance(TextExtractor(), TextExtractor)


def test_extractor_uses_default_parser(extractor: TextExtractor) -> None:
    assert isinstance(extractor.parser, TextParser)


def test_extractor_accepts_custom_parser() -> None:
    parser = TextParser()
    extractor = TextExtractor(parser)

    assert extractor.parser is parser


def test_extractor_rejects_invalid_parser() -> None:
    with pytest.raises(TypeError, match="parser must be a TextParser"):
        TextExtractor(object())  # type: ignore[arg-type]


def test_extract_returns_dictionary(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world.")

    assert isinstance(result, dict)


def test_extract_has_features(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world.")

    assert "features" in result
    assert isinstance(result["features"], dict)


def test_extract_has_entities(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world.")

    assert result["entities"] == []


def test_extract_has_relations(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world.")

    assert result["relations"] == []


def test_extract_character_count(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello!")

    assert result["features"]["character_count"] == 6


def test_extract_token_count(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world!")

    assert result["features"]["token_count"] == 3


def test_extract_word_count(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world!")

    assert result["features"]["word_count"] == 2


def test_extract_sentence_count(extractor: TextExtractor) -> None:
    result = extractor.extract("Hello world!")

    assert result["features"]["sentence_count"] == 1


def test_extract_empty_text(extractor: TextExtractor) -> None:
    result = extractor.extract("")

    assert result == {
        "features": {
            "character_count": 0,
            "token_count": 0,
            "word_count": 0,
            "sentence_count": 0,
        },
        "entities": [],
        "relations": [],
    }


def test_extract_preserves_unicode_counts(
    extractor: TextExtractor,
) -> None:
    result = extractor.extract("Xin chào Việt Nam!")

    assert result["features"] == {
        "character_count": 18,
        "token_count": 5,
        "word_count": 4,
        "sentence_count": 1,
    }


def test_extract_accepts_explicit_parsed_data(
    extractor: TextExtractor,
) -> None:
    parsed = {
        "text": "custom",
        "tokens": ["custom"],
        "token_count": 1,
        "word_count": 1,
        "sentence_count": 0,
    }

    result = extractor.extract("ignored", parsed=parsed)

    assert result["features"]["token_count"] == 1
    assert result["features"]["word_count"] == 1
    assert result["features"]["sentence_count"] == 0


def test_extract_copies_parsed_data(
    extractor: TextExtractor,
) -> None:
    parsed = {
        "text": "custom",
        "tokens": ["custom"],
        "token_count": 1,
        "word_count": 1,
        "sentence_count": 0,
    }

    extractor.extract("custom", parsed=parsed)
    parsed["token_count"] = 99

    result = extractor.extract("custom", parsed=parsed)

    assert result["features"]["token_count"] == 99


def test_extract_requires_string(
    extractor: TextExtractor,
) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        extractor.extract(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "parsed",
    [None, "parsed", 123, [], object()],
)
def test_explicit_parsed_must_be_dictionary(
    extractor: TextExtractor,
    parsed: object,
) -> None:
    if parsed is None:
        pytest.skip("None means use the parser")

    with pytest.raises(
        TypeError,
        match="parsed must be a dictionary",
    ):
        extractor.extract("text", parsed=parsed)  # type: ignore[arg-type]


def test_extractor_is_stateless(extractor: TextExtractor) -> None:
    extractor.extract("first text.")

    result = extractor.extract("second text.")

    assert result["features"]["word_count"] == 2


def test_public_exports_are_locked() -> None:
    from scios.cognitive_core.perception.modalities.text import extractor

    assert extractor.__all__ == ["TextExtractor"]
